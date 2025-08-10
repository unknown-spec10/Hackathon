"""
Interview Models for Technical Assessment System
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from database.db_setup import Base
from datetime import datetime
import enum


class DifficultyLevel(enum.Enum):
    """Difficulty levels based on Years of Experience"""
    FRESHER = "fresher"           # 0-1 years
    JUNIOR = "junior"             # 1-3 years  
    INTERMEDIATE = "intermediate" # 3-5 years
    SENIOR = "senior"             # 5-8 years
    EXPERT = "expert"             # 8+ years


class InterviewDomain(enum.Enum):
    """Technical domains for interviews"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    CLOUD_COMPUTING = "cloud_computing"
    DEVOPS = "devops"
    CYBERSECURITY = "cybersecurity"
    MOBILE_DEVELOPMENT = "mobile_development"
    WEB_DEVELOPMENT = "web_development"
    BLOCKCHAIN = "blockchain"
    AI_ML = "ai_ml"


class InterviewSession(Base):
    """Interview session tracking"""
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Interview configuration
    domain = Column(Enum(InterviewDomain), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    
    # Session data
    questions = Column(JSON)  # Generated questions in JSON format
    answers = Column(JSON)    # User answers
    
    # Evaluation results
    individual_scores = Column(JSON)  # Score for each question
    overall_score = Column(Float)     # Final score (0-100)
    recommendations = Column(JSON)    # LLM recommendations
    strengths = Column(JSON)          # Identified strengths
    weaknesses = Column(JSON)         # Areas for improvement
    
    # Session metadata
    status = Column(String(20), default="active")  # active, completed, abandoned
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    time_taken = Column(Integer)  # Total time in seconds
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    
    def __repr__(self):
        return f"<InterviewSession(id={self.id}, domain={self.domain.value}, level={self.difficulty_level.value})>"


class QuestionBank(Base):
    """Static question bank for reference"""
    __tablename__ = "question_bank"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(Enum(InterviewDomain), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    
    question_text = Column(Text, nullable=False)
    expected_answer = Column(Text)
    key_points = Column(JSON)  # Key points to look for in answers
    tags = Column(JSON)        # Question tags/categories
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<QuestionBank(id={self.id}, domain={self.domain.value})>"


class InterviewFeedback(Base):
    """User feedback on interview experience"""
    __tablename__ = "interview_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    
    rating = Column(Integer)  # 1-5 rating
    feedback_text = Column(Text)
    suggestions = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession")
