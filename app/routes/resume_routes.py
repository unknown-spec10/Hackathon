from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.schemas.resume_schema import ResumeUploadResponse, ResumeListResponse, ResumeDetailResponse
from app.utils.auth_deps import get_current_user
from app.utils.deps import get_db
from app.repositories.user_repo import UserRepository
from app.services.langgraph_resume_parser import LangGraphResumeParser
from app.services.pdf_processor import PDFProcessor
from app.services.job_recommender import JobRecommender
from app.services.course_recommender import CourseRecommender
import os
import json
from datetime import datetime, timedelta
import logging

router = APIRouter(prefix="/resume", tags=["Resume Processing"])
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload and process resume with AI"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Save uploaded file
    upload_dir = "app/uploads/resumes"
    os.makedirs(upload_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Process PDF
        pdf_processor = PDFProcessor()
        pdf_data = pdf_processor.extract_complete_pdf_data(file_path)
        
        # Parse with AI
        parser = LangGraphResumeParser(groq_api_key=os.getenv("GROQ_API_KEY"))
        parsed_data = await parser.parse_resume(pdf_data["text"])
        
        # Save to database
        user_repo = UserRepository()
        resume_data = {
            "user_id": current_user.id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "extracted_text": pdf_data["text"],
            "parsed_data": parsed_data.model_dump(),
            "processing_status": "completed",
            "confidence_score": "0.85",  # String as per model
            "processing_time": 2,  # Integer as per model
            "parsing_errors": []
        }
        
        resume = user_repo.create_resume(resume_data)

        # Clean up uploaded file after successful processing to avoid stacking
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned uploaded file: {file_path}")
        except Exception as ce:
            logger.warning(f"Could not remove uploaded file {file_path}: {ce}")

        # Sweep stale files (>24h) as a safety
        try:
            sweep_dir = upload_dir
            cutoff = datetime.now() - timedelta(hours=24)
            for fname in os.listdir(sweep_dir):
                if not fname.lower().endswith('.pdf'):
                    continue
                fpath = os.path.join(sweep_dir, fname)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                    if mtime < cutoff:
                        os.remove(fpath)
                        logger.info(f"Removed stale resume file: {fpath}")
                except Exception:
                    # best-effort cleanup
                    pass
        except Exception:
            pass

        return ResumeUploadResponse(
            id=resume.id,
            filename=file.filename,
            status="processed",
            confidence_score=float(resume.confidence_score),
            message="Resume processed successfully"
        )
    
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume processing failed: {str(e)}"
        )

@router.get("/", response_model=List[ResumeListResponse])
async def get_user_resumes(current_user = Depends(get_current_user)):
    """Get all resumes for current user"""
    user_repo = UserRepository()
    resumes = user_repo.get_user_resumes(current_user.id)
    
    return [
        ResumeListResponse(
            id=resume.id,
            filename=resume.filename,
            uploaded_at=(resume.created_at.isoformat() if hasattr(resume.created_at, "isoformat") else str(resume.created_at)),
            confidence_score=float(resume.confidence_score),
            status="processed"
        )
        for resume in resumes
    ]

@router.get("/recommendations")
async def get_recommendations(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered job and course recommendations"""
    user_repo = UserRepository()
    resumes = user_repo.get_user_resumes(current_user.id)
    
    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resumes found. Please upload a resume first."
        )
    
    # Use latest resume
    latest_resume = resumes[0]
    
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Getting recommendations for resume {latest_resume.id}")
        logger.info(f"Resume parsed_data keys: {list(latest_resume.parsed_data.keys()) if latest_resume.parsed_data else 'None'}")
        
        # Get job recommendations
        job_recommender = JobRecommender()
        logger.info("Created job recommender")
        job_recommendations = job_recommender.get_recommendations(latest_resume.parsed_data, db=db)
        logger.info(f"Got {len(job_recommendations)} job recommendations")
        for i, rec in enumerate(job_recommendations):
            job = rec.get('job')
            job_title = job.title if job else 'Unknown'
            logger.info(f"Job rec {i}: {job_title} - Score: {rec.get('score', 0)}")
        
        # Get course recommendations
        course_recommender = CourseRecommender()
        logger.info("Created course recommender")
        course_recommendations = course_recommender.get_recommendations(latest_resume.parsed_data, db=db)
        logger.info(f"Got {len(course_recommendations)} course recommendations")
        
        # Simplify - extract job details properly from SQLAlchemy objects
        job_recs_simple = []
        for rec in job_recommendations[:5]:
            job = rec.get('job')  # This is a SQLAlchemy Job object
            if job:
                job_recs_simple.append({
                    'job_title': job.title,
                    'job_id': job.id,
                    'location': job.location,
                    'salary_range': job.salary_range,
                    'job_type': job.job_type,
                    'remote_option': job.remote_option,
                    'experience_level': job.experience_level,
                    'industry': job.industry,
                    'score': rec.get('score', 0),
                    'matching_skills': rec.get('matching_skills', []),
                    'skill_gaps': rec.get('skill_gaps', []),
                    'recommendation_reason': rec.get('recommendation_reason', '')
                })
        
        course_recs_simple = []
        for rec in course_recommendations[:5]:
            course = rec.get('course')  # This is a SQLAlchemy Course object
            if course:
                course_recs_simple.append({
                    'course_name': course.name,
                    'course_id': course.id,
                    'duration': course.duration,
                    'mode': course.mode,
                    'fees': course.fees,
                    'description': course.description,
                    'score': rec.get('score', 0),
                    'skill_gaps_addressed': rec.get('skill_gaps_addressed', []),
                    'career_impact': rec.get('career_impact', '')
                })
        
        return {
            "job_recommendations": job_recs_simple,
            "course_recommendations": course_recs_simple,
            "based_on_resume": latest_resume.filename
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )

@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume_details(resume_id: int, current_user = Depends(get_current_user)):
    """Get detailed resume information"""
    user_repo = UserRepository()
    resume = user_repo.get_resume_by_id(resume_id)
    
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return ResumeDetailResponse(
        id=resume.id,
        filename=resume.filename,
        uploaded_at=(resume.created_at.isoformat() if hasattr(resume.created_at, "isoformat") else str(resume.created_at)),
        confidence_score=float(resume.confidence_score),
        processing_time=resume.processing_time,
        parsed_data=resume.parsed_data,
        parsing_errors=resume.parsing_errors or [],
        raw_text=resume.extracted_text or ""  # Include the raw extracted text
    )

@router.delete("/{resume_id}")
async def delete_resume(resume_id: int, current_user = Depends(get_current_user)):
    """Delete a resume"""
    user_repo = UserRepository()
    resume = user_repo.get_resume_by_id(resume_id)
    
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete from database
    user_repo.delete_resume(resume_id)
    
    return {"message": "Resume deleted successfully"}
