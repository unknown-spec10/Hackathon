"""
Interview Schemas for API Request/Response
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.models.interview import DifficultyLevel, InterviewDomain


class InterviewStartRequest(BaseModel):
    """Request to start a new interview session"""
    domain: InterviewDomain = Field(..., description="Technical domain for interview")
    years_of_experience: int = Field(..., ge=0, le=20, description="Years of experience (0-20)")
    
    class Config:
        use_enum_values = True


class QuestionSchema(BaseModel):
    """Individual question structure"""
    id: int = Field(..., description="Question ID")
    question: str = Field(..., description="Question text")
    type: str = Field(default="text", description="Question type (text, code, multiple_choice)")
    options: Optional[List[str]] = Field(None, description="Options for multiple choice")
    answer: str = Field(default="", description="User's answer")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "question": "Explain the difference between list and tuple in Python",
                "type": "text",
                "answer": ""
            }
        }


class InterviewQuestionsResponse(BaseModel):
    """Response containing generated questions"""
    session_id: int = Field(..., description="Interview session ID")
    domain: str = Field(..., description="Interview domain")
    difficulty_level: str = Field(..., description="Difficulty level")
    total_questions: int = Field(..., description="Total number of questions")
    questions: List[QuestionSchema] = Field(..., description="List of questions")
    estimated_time: int = Field(..., description="Estimated time in minutes")


class AnswerSubmissionRequest(BaseModel):
    """Request to submit answers"""
    session_id: int = Field(..., description="Interview session ID")
    answers: List[Dict[str, Any]] = Field(..., description="List of answers with question IDs")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": 1,
                "answers": [
                    {"question_id": 1, "answer": "Lists are mutable while tuples are immutable..."},
                    {"question_id": 2, "answer": "def fibonacci(n): ..."}
                ]
            }
        }


class QuestionEvaluation(BaseModel):
    """Individual question evaluation"""
    question_id: int
    question: str
    user_answer: str
    score: float = Field(..., ge=0, le=10, description="Score out of 10")
    feedback: str = Field(..., description="Detailed feedback")
    key_points_covered: List[str] = Field(default_factory=list)
    missing_points: List[str] = Field(default_factory=list)


class InterviewResultResponse(BaseModel):
    """Complete interview evaluation results"""
    session_id: int
    domain: str
    difficulty_level: str
    
    # Overall results
    overall_score: float = Field(..., ge=0, le=100, description="Overall score percentage")
    grade: str = Field(..., description="Letter grade (A+, A, B+, B, C+, C, D, F)")
    
    # Detailed evaluation
    question_evaluations: List[QuestionEvaluation]
    
    # Analysis
    strengths: List[str] = Field(..., description="Identified strengths")
    weaknesses: List[str] = Field(..., description="Areas for improvement")
    recommendations: List[str] = Field(..., description="Learning recommendations")
    
    # Performance metrics
    time_taken: int = Field(..., description="Time taken in minutes")
    accuracy_rate: float = Field(..., description="Percentage of correct answers")
    
    # Next steps
    suggested_resources: List[Dict[str, str]] = Field(default_factory=list)
    next_level_readiness: bool = Field(..., description="Ready for next difficulty level")


class InterviewHistoryResponse(BaseModel):
    """User's interview history"""
    user_id: int
    total_interviews: int
    average_score: float
    best_score: float
    recent_sessions: List[Dict[str, Any]]
    domain_performance: Dict[str, float]  # Average score per domain
    progress_trend: List[Dict[str, Any]]  # Score progression over time


class DomainDifficultyInfo(BaseModel):
    """Information about domain and difficulty options"""
    domains: List[Dict[str, str]] = Field(..., description="Available domains")
    difficulty_levels: List[Dict[str, str]] = Field(..., description="Difficulty levels with YOE mapping")
    
    class Config:
        schema_extra = {
            "example": {
                "domains": [
                    {"value": "python", "label": "Python Programming"},
                    {"value": "data_science", "label": "Data Science"}
                ],
                "difficulty_levels": [
                    {"value": "fresher", "label": "Fresher (0-1 years)", "yoe_range": "0-1"},
                    {"value": "junior", "label": "Junior (1-3 years)", "yoe_range": "1-3"}
                ]
            }
        }
