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
from datetime import datetime

router = APIRouter(prefix="/resume", tags=["Resume Processing"])

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
        parsed_data = parser.parse_resume(pdf_data["text"])
        
        # Save to database
        user_repo = UserRepository()
        resume_data = {
            "user_id": current_user.id,
            "file_path": file_path,
            "original_filename": file.filename,
            "parsed_data": parsed_data.model_dump(),
            "confidence_score": 0.85,  # Default confidence
            "processing_time": 2.5,    # Default processing time
            "parsing_errors": []
        }
        
        resume = user_repo.create_resume(resume_data)
        
        return ResumeUploadResponse(
            id=resume.id,
            filename=file.filename,
            status="processed",
            confidence_score=resume.confidence_score,
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
            filename=resume.original_filename,
            uploaded_at=resume.created_at,
            confidence_score=resume.confidence_score,
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
        # Get job recommendations
        job_recommender = JobRecommender()
        job_recommendations = job_recommender.get_recommendations(latest_resume.parsed_data, db)
        
        # Get course recommendations
        course_recommender = CourseRecommender()
        course_recommendations = course_recommender.get_recommendations(latest_resume.parsed_data)
        
        return {
            "job_recommendations": job_recommendations[:5],  # Top 5
            "course_recommendations": course_recommendations[:5],  # Top 5
            "based_on_resume": latest_resume.original_filename
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
        filename=resume.original_filename,
        uploaded_at=resume.created_at,
        confidence_score=resume.confidence_score,
        processing_time=resume.processing_time,
        parsed_data=resume.parsed_data,
        parsing_errors=resume.parsing_errors or []
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
