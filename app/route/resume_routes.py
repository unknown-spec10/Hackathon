from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import asyncio
from pathlib import Path
import uuid
from datetime import datetime

from database.db_setup import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.schemas.resume_schema import (
    ResumeUploadResponse, ParsedResumeData, JobRecommendationResponse, 
    CourseRecommendationResponse, ResumeListResponse, ResumeDetailResponse,
    RecommendationsResponse, ProcessingProgressResponse, ResumeSearchRequest, 
    JobSearchResponse, ProcessingStatus
)
from app.services.pdf_processor import PDFProcessor
from app.services.langgraph_resume_parser import LangGraphResumeParser
from app.services.job_recommender import JobRecommender
from app.services.course_recommender import CourseRecommender
from app.utils.auth_deps import get_current_user


router = APIRouter(prefix="/resume", tags=["Resume Processing"])

# Initialize services
pdf_processor = PDFProcessor()
# Using Groq for faster inference
resume_parser = LangGraphResumeParser()
job_recommender = JobRecommender()
course_recommender = CourseRecommender()

# Create upload directory
UPLOAD_DIR = Path("app/uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Only PDF files are supported."
        )
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
        )


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process resume PDF
    
    - **file**: PDF file containing the resume
    - Returns resume processing status and initial data
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB"
        )
    
    # Generate unique filename
    resume_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{resume_id}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Save file
        file_content = await file.read()
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create resume record
        resume = Resume(
            id=resume_id,
            user_id=current_user.id,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(file_content),
            status="processing"
        )
        
        db.add(resume)
        db.commit()
        
        # Process resume immediately with LangGraph
        try:
            # Extract PDF text
            pdf_text = pdf_processor.extract_text_from_pdf(str(file_path))
            
            # Parse with LangGraph
            start_time = datetime.now()
            parsed_data = await resume_parser.parse_resume(pdf_text)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update resume with parsed data
            resume.parsed_data = parsed_data
            resume.processing_time = processing_time
            resume.status = "completed"
            resume.processed_at = datetime.now()
            
            db.commit()
            
            return ResumeUploadResponse(
                resume_id=resume_id,
                filename=file.filename,
                status="completed",
                parsed_data=ParsedResumeData(**parsed_data),
                message="Resume uploaded and processed successfully"
            )
            
        except Exception as e:
            # Update resume with error status
            resume.status = "failed"
            resume.parsing_errors = [str(e)]
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process resume: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if something goes wrong
        if file_path.exists():
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading resume: {str(e)}"
        )


@router.get("/", response_model=List[ResumeListResponse])
async def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for the current user"""
    
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.uploaded_at.desc()).all()
    
    return [
        ResumeListResponse(
            resume_id=resume.id,
            filename=resume.original_filename,
            status=resume.status,
            uploaded_at=resume.uploaded_at,
            processed_at=resume.processed_at
        )
        for resume in resumes
    ]


@router.get("/recommendations", response_model=dict)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    resume_id: Optional[str] = Query(None, description="Specific resume ID, defaults to latest"),
    job_limit: int = Query(5, description="Number of job recommendations"),
    course_limit: int = Query(5, description="Number of course recommendations")
):
    """Get job and course recommendations based on resume"""
    
    # Get resume
    if resume_id:
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        ).first()
    else:
        # Get latest resume
        resume = db.query(Resume).filter(
            Resume.user_id == current_user.id,
            Resume.status == "completed"
        ).order_by(Resume.processed_at.desc()).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )
    
    if resume.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume is still being processed. Please wait for processing to complete."
        )
    
    if not resume.parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume data not available. Please re-upload your resume."
        )
    
    try:
        # Get job recommendations
        job_recommendations = job_recommender.get_recommendations(
            parsed_resume=resume.parsed_data,
            db=db,
            limit=job_limit
        )
        
        # Get course recommendations
        course_recommendations = course_recommender.get_recommendations(
            resume_data=resume.parsed_data,
            limit=course_limit
        )
        
        return {
            "resume_id": resume.id,
            "resume_filename": resume.original_filename,
            "processed_at": resume.processed_at,
            "job_recommendations": [
                JobRecommendationResponse(
                    job_id=rec["job_id"],
                    title=rec["title"],
                    company=rec["company"],
                    location=rec["location"],
                    description=rec["description"],
                    requirements=rec["requirements"],
                    salary_range=rec.get("salary_range"),
                    employment_type=rec.get("employment_type"),
                    experience_level=rec.get("experience_level"),
                    match_score=rec["match_score"],
                    matching_skills=rec.get("matching_skills", []),
                    skill_gaps=rec.get("skill_gaps", []),
                    match_explanation=rec.get("match_explanation")
                )
                for rec in job_recommendations
            ],
            "course_recommendations": [
                CourseRecommendationResponse(
                    course_id=rec["course_id"],
                    title=rec["title"],
                    provider=rec["provider"],
                    description=rec["description"],
                    skills_covered=rec["skills_covered"],
                    duration=rec.get("duration"),
                    difficulty_level=rec.get("difficulty_level"),
                    price=rec.get("price"),
                    rating=rec.get("rating"),
                    relevance_score=rec["relevance_score"],
                    skill_gaps_addressed=rec.get("skill_gaps_addressed", []),
                    career_impact=rec.get("career_impact"),
                    recommendation_reason=rec.get("recommendation_reason")
                )
                for rec in course_recommendations
            ],
            "total_jobs": len(job_recommendations),
            "total_courses": len(course_recommendations)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/{resume_id}/job-recommendations", response_model=List[JobRecommendationResponse])
def get_job_recommendations(
    resume_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job recommendations based on a specific resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.status != "completed" or not resume.parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume has not been processed successfully"
        )
    
    try:
        recommendations = job_recommender.get_recommendations(
            parsed_resume=resume.parsed_data,
            db=db,
            limit=limit
        )
        
        return [
            JobRecommendationResponse(
                job_id=rec["job_id"],
                title=rec["title"],
                company=rec["company"],
                location=rec["location"],
                description=rec["description"],
                requirements=rec["requirements"],
                salary_range=rec.get("salary_range"),
                employment_type=rec.get("employment_type"),
                experience_level=rec.get("experience_level"),
                match_score=rec["match_score"],
                matching_skills=rec.get("matching_skills", []),
                skill_gaps=rec.get("skill_gaps", []),
                match_explanation=rec.get("match_explanation")
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job recommendations: {str(e)}"
        )


@router.get("/{resume_id}/course-recommendations", response_model=List[CourseRecommendationResponse])
def get_course_recommendations(
    resume_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get course recommendations based on a specific resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.status != "completed" or not resume.parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume has not been processed successfully"
        )
    
    try:
        recommendations = course_recommender.get_recommendations(
            resume_data=resume.parsed_data,
            limit=limit
        )
        
        return [
            CourseRecommendationResponse(
                course_id=rec["course_id"],
                title=rec["title"],
                provider=rec["provider"],
                description=rec["description"],
                skills_covered=rec["skills_covered"],
                duration=rec.get("duration"),
                difficulty_level=rec.get("difficulty_level"),
                price=rec.get("price"),
                rating=rec.get("rating"),
                relevance_score=rec["relevance_score"],
                skill_gaps_addressed=rec.get("skill_gaps_addressed", []),
                career_impact=rec.get("career_impact"),
                recommendation_reason=rec.get("recommendation_reason")
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course recommendations: {str(e)}"
        )


@router.post("/search-jobs", response_model=JobSearchResponse)
async def search_jobs(
    search_request: ResumeSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for jobs based on criteria"""
    
    if current_user.user_type.value != "B2C":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only B2C users can search jobs"
        )
    
    try:
        # Build query
        query = db.query(Job).filter(Job.is_active == True)
        
        # Apply filters
        if search_request.query:
            query = query.filter(
                Job.title.ilike(f"%{search_request.query}%") |
                Job.description.ilike(f"%{search_request.query}%") |
                Job.requirements.ilike(f"%{search_request.query}%")
            )
        
        if search_request.location:
            query = query.filter(Job.location.ilike(f"%{search_request.location}%"))
        
        if search_request.job_type:
            query = query.filter(Job.employment_type.ilike(f"%{search_request.job_type}%"))
        
        if search_request.experience_level:
            query = query.filter(Job.experience_level.ilike(f"%{search_request.experience_level}%"))
        
        # Apply salary filter if provided
        if search_request.salary_range:
            min_salary = search_request.salary_range.get("min")
            max_salary = search_request.salary_range.get("max")
            
            if min_salary:
                query = query.filter(Job.salary_max >= min_salary)
            if max_salary:
                query = query.filter(Job.salary_min <= max_salary)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        jobs = query.offset(search_request.offset).limit(search_request.limit).all()
        
        # Convert to dict format
        job_dicts = []
        for job in jobs:
            job_dict = {
                "id": job.id,
                "title": job.title,
                "company": job.company_name,
                "location": job.location,
                "employment_type": job.employment_type,
                "experience_level": job.experience_level,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                "requirements": job.requirements[:200] + "..." if len(job.requirements) > 200 else job.requirements,
                "posted_date": job.created_at.isoformat() if job.created_at else None
            }
            job_dicts.append(job_dict)
        
        # Calculate pagination info
        page = (search_request.offset // search_request.limit) + 1
        has_next = (search_request.offset + search_request.limit) < total_count
        has_prev = search_request.offset > 0
        
        return JobSearchResponse(
            jobs=job_dicts,
            total_count=total_count,
            page=page,
            per_page=search_request.limit,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching jobs: {str(e)}"
        )


@router.delete("/resume/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume and its associated file"""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    try:
        # Delete file if it exists
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
        
        # Delete database record
        db.delete(resume)
        db.commit()
        
        return {"message": "Resume deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting resume: {str(e)}"
        )


@router.get("/resume/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume_details(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific resume"""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return ResumeDetailResponse(
        resume_id=resume.id,
        filename=resume.original_filename,
        status=resume.status,
        uploaded_at=resume.uploaded_at,
        processed_at=resume.processed_at,
        file_size=resume.file_size,
        processing_time=resume.processing_time,
        parsed_data=ParsedResumeData(**resume.parsed_data) if resume.parsed_data else None,
        parsing_errors=resume.parsing_errors
    )
