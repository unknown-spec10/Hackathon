"""
Interview API Routes
Handles technical interview chatbot endpoints with domain-specific questions and LLM evaluation.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
from datetime import datetime
import os
import logging

from database.db_setup import get_db
from app.models.interview import InterviewSession, DifficultyLevel, InterviewDomain, InterviewFeedback
from app.models.user import User
from app.schemas.interview_schema import (
    InterviewStartRequest, InterviewQuestionsResponse, AnswerSubmissionRequest,
    InterviewResultResponse, InterviewHistoryResponse, DomainDifficultyInfo,
    QuestionSchema
)
from app.services.interview_service import InterviewOrchestrator, InterviewConfig
from app.utils.auth_deps import get_current_user
from app.core.settings import settings

router = APIRouter(prefix="/interview", tags=["Technical Interview"])
logger = logging.getLogger(__name__)

# Initialize interview orchestrator with settings
if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key":
    interview_orchestrator = InterviewOrchestrator(settings.GROQ_API_KEY)
    logger.info("Interview orchestrator initialized with Groq API")
else:
    interview_orchestrator = None
    logger.warning("GROQ_API_KEY not properly configured. Interview features will be limited.")


@router.get("/domains", response_model=DomainDifficultyInfo)
async def get_available_domains():
    """Get available interview domains and difficulty levels"""
    
    domains = [
        {"value": domain.value, "label": domain.value.replace('_', ' ').title()}
        for domain in InterviewDomain
    ]
    
    difficulty_levels = [
        {"value": "fresher", "label": "Fresher (0-1 years)", "yoe_range": "0-1"},
        {"value": "junior", "label": "Junior (1-3 years)", "yoe_range": "1-3"},
        {"value": "intermediate", "label": "Intermediate (3-5 years)", "yoe_range": "3-5"},
        {"value": "senior", "label": "Senior (5-8 years)", "yoe_range": "5-8"},
        {"value": "expert", "label": "Expert (8+ years)", "yoe_range": "8+"}
    ]
    
    return DomainDifficultyInfo(
        domains=domains,
        difficulty_levels=difficulty_levels
    )


@router.post("/start", response_model=InterviewQuestionsResponse)
async def start_interview(
    request: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new interview session and generate questions"""
    
    if not interview_orchestrator:
        raise HTTPException(status_code=503, detail="Interview service unavailable - API key not configured")
    
    try:
        # Generate questions using the orchestrator
        difficulty, questions = await interview_orchestrator.generate_interview_questions(
            domain=request.domain,
            years_experience=request.years_of_experience,
            config=InterviewConfig(max_questions=20)
        )
        
        # Create interview session in database
        session = InterviewSession(
            user_id=current_user.id,
            domain=request.domain,
            difficulty_level=difficulty,
            years_of_experience=request.years_of_experience,
            questions=questions,
            status="active"
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Convert questions to response format
        question_schemas = [
            QuestionSchema(
                id=q["id"],
                question=q["question"],
                type=q.get("type", "text"),
                answer=""
            )
            for q in questions
        ]
        
        # Estimate time (3 minutes per question)
        estimated_time = len(questions) * 3
        
        logger.info(f"Started interview session {session.id} for user {current_user.id}")
        
        return InterviewQuestionsResponse(
            session_id=session.id,
            domain=request.domain.value,
            difficulty_level=difficulty.value,
            total_questions=len(questions),
            questions=question_schemas,
            estimated_time=estimated_time
        )
        
    except Exception as e:
        logger.error(f"Failed to start interview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate interview questions: {str(e)}")


@router.post("/submit", response_model=InterviewResultResponse)
async def submit_answers(
    request: AnswerSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answers and get evaluation results"""
    
    if not interview_orchestrator:
        raise HTTPException(status_code=503, detail="Interview service unavailable")
    
    # Get interview session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == request.session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Interview session is not active")
    
    try:
        # Calculate time taken
        time_taken_seconds = (datetime.utcnow() - session.started_at).total_seconds()
        time_taken_minutes = int(time_taken_seconds / 60)
        
        # Evaluate answers using the orchestrator
        result = await interview_orchestrator.evaluate_interview(
            questions=session.questions,
            answers=request.answers,
            domain=session.domain,
            difficulty=session.difficulty_level,
            years_experience=session.years_of_experience
        )
        
        # Update session with results
        session.answers = request.answers
        session.individual_scores = [
            {"question_id": eval.question_id, "score": eval.score}
            for eval in result.question_evaluations
        ]
        session.overall_score = result.overall_score
        session.recommendations = result.recommendations
        session.strengths = result.strengths
        session.weaknesses = result.weaknesses
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.time_taken = int(time_taken_seconds)
        
        db.commit()
        
        # Set session ID and time in result
        result.session_id = session.id
        result.time_taken = time_taken_minutes
        
        logger.info(f"Completed interview evaluation for session {session.id}. Score: {result.overall_score}%")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to evaluate interview: {e}")
        # Mark session as failed
        session.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answers: {str(e)}")


@router.get("/session/{session_id}", response_model=InterviewResultResponse)
async def get_interview_result(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get results of a completed interview session"""
    
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview not completed yet")
    
    # Reconstruct the result from stored data
    question_evaluations = []
    if session.individual_scores and session.answers:
        answer_map = {ans["question_id"]: ans["answer"] for ans in session.answers}
        
        for question in session.questions:
            question_id = question["id"]
            score_data = next((s for s in session.individual_scores if s["question_id"] == question_id), None)
            
            question_evaluations.append({
                "question_id": question_id,
                "question": question["question"],
                "user_answer": answer_map.get(question_id, ""),
                "score": score_data["score"] if score_data else 0,
                "feedback": "Detailed feedback available in full report",
                "key_points_covered": [],
                "missing_points": []
            })
    
    time_taken_minutes = session.time_taken // 60 if session.time_taken else 0
    
    return InterviewResultResponse(
        session_id=session.id,
        domain=session.domain.value,
        difficulty_level=session.difficulty_level.value,
        overall_score=session.overall_score or 0,
        grade=_calculate_grade(session.overall_score or 0),
        question_evaluations=question_evaluations,
        strengths=session.strengths or [],
        weaknesses=session.weaknesses or [],
        recommendations=session.recommendations or [],
        time_taken=time_taken_minutes,
        accuracy_rate=0,  # Would need to recalculate
        suggested_resources=[],
        next_level_readiness=session.overall_score >= 70 if session.overall_score else False
    )


@router.get("/history", response_model=InterviewHistoryResponse)
async def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's interview history and performance analytics"""
    
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.desc()).all()
    
    completed_sessions = [s for s in sessions if s.status == "completed" and s.overall_score is not None]
    
    if not completed_sessions:
        return InterviewHistoryResponse(
            user_id=current_user.id,
            total_interviews=0,
            average_score=0,
            best_score=0,
            recent_sessions=[],
            domain_performance={},
            progress_trend=[]
        )
    
    # Calculate metrics
    total_interviews = len(completed_sessions)
    average_score = sum(s.overall_score for s in completed_sessions) / total_interviews
    best_score = max(s.overall_score for s in completed_sessions)
    
    # Recent sessions (last 5)
    recent_sessions = [
        {
            "session_id": s.id,
            "domain": s.domain.value,
            "difficulty": s.difficulty_level.value,
            "score": s.overall_score,
            "date": s.completed_at.isoformat() if s.completed_at else s.created_at.isoformat(),
            "grade": _calculate_grade(s.overall_score)
        }
        for s in completed_sessions[:5]
    ]
    
    # Domain performance
    domain_scores = {}
    for session in completed_sessions:
        domain = session.domain.value
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append(session.overall_score)
    
    domain_performance = {
        domain: sum(scores) / len(scores)
        for domain, scores in domain_scores.items()
    }
    
    # Progress trend (last 10 sessions)
    progress_trend = [
        {
            "session_id": s.id,
            "date": s.completed_at.isoformat() if s.completed_at else s.created_at.isoformat(),
            "score": s.overall_score,
            "domain": s.domain.value
        }
        for s in completed_sessions[:10]
    ]
    
    return InterviewHistoryResponse(
        user_id=current_user.id,
        total_interviews=total_interviews,
        average_score=round(average_score, 2),
        best_score=round(best_score, 2),
        recent_sessions=recent_sessions,
        domain_performance={k: round(v, 2) for k, v in domain_performance.items()},
        progress_trend=progress_trend
    )


@router.post("/feedback/{session_id}")
async def submit_feedback(
    session_id: int,
    rating: int,
    feedback_text: str = "",
    suggestions: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for an interview session"""
    
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    # Check if feedback already exists
    existing_feedback = db.query(InterviewFeedback).filter(
        InterviewFeedback.session_id == session_id
    ).first()
    
    if existing_feedback:
        existing_feedback.rating = rating
        existing_feedback.feedback_text = feedback_text
        existing_feedback.suggestions = suggestions
    else:
        feedback = InterviewFeedback(
            session_id=session_id,
            rating=rating,
            feedback_text=feedback_text,
            suggestions=suggestions
        )
        db.add(feedback)
    
    db.commit()
    
    return {"message": "Feedback submitted successfully"}


def _calculate_grade(percentage: float) -> str:
    """Convert percentage to letter grade"""
    if percentage >= 95: return "A+"
    elif percentage >= 90: return "A"
    elif percentage >= 85: return "A-"
    elif percentage >= 80: return "B+"
    elif percentage >= 75: return "B"
    elif percentage >= 70: return "B-"
    elif percentage >= 65: return "C+"
    elif percentage >= 60: return "C"
    elif percentage >= 55: return "C-"
    elif percentage >= 50: return "D"
    else: return "F"
