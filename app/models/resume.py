from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from database.db_setup import Base
from datetime import datetime


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    content_type = Column(String(100), default="application/pdf")
    
    # Extracted raw data
    extracted_text = Column(Text)  # Raw text from PDF
    extracted_tables = Column(JSON)  # Tables found in PDF
    extracted_images = Column(JSON)  # Image metadata
    
    # Parsed structured data
    parsed_data = Column(JSON)  # Structured resume data from LangGraph
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    parsing_errors = Column(JSON)  # Any errors during parsing
    confidence_score = Column(String(10))  # Overall parsing confidence
    
    # Analysis results
    skills_extracted = Column(JSON)  # List of skills
    experience_summary = Column(Text)
    education_summary = Column(Text)
    job_match_score = Column(Float, default=0.0)
    
    # Processing metadata
    is_active = Column(Boolean, default=True)  # Current/active resume
    processing_time = Column(Integer)  # Time taken to process in seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)  # When parsing was completed
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename='{self.filename}')>"
    
    @property
    def is_processed(self) -> bool:
        """Check if resume has been successfully processed"""
        return self.processing_status == "completed"
    
    @property
    def has_errors(self) -> bool:
        """Check if there were errors during processing"""
        return bool(self.parsing_errors)
    
    def get_personal_info(self) -> dict:
        """Get personal information from parsed data"""
        if self.parsed_data and "personal_info" in self.parsed_data:
            return self.parsed_data["personal_info"]
        return {}
    
    def get_skills(self) -> list:
        """Get skills list from parsed data"""
        if self.parsed_data and "skills" in self.parsed_data:
            return self.parsed_data["skills"]
        return []
    
    def get_experience(self) -> list:
        """Get work experience from parsed data"""
        if self.parsed_data and "experience" in self.parsed_data:
            return self.parsed_data["experience"]
        return []
    
    def get_education(self) -> list:
        """Get education from parsed data"""
        if self.parsed_data and "education" in self.parsed_data:
            return self.parsed_data["education"]
        return []


class JobRecommendation(Base):
    __tablename__ = "job_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Recommendation metrics
    match_score = Column(Float, nullable=False)
    matching_skills = Column(JSON)  # List of matching skills
    skill_gaps = Column(JSON)  # List of missing skills
    recommendation_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume")
    job = relationship("Job")


class CourseRecommendation(Base):
    __tablename__ = "course_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Recommendation metrics
    relevance_score = Column(Float, nullable=False)
    skill_gaps_addressed = Column(JSON)  # Skills this course will help with
    career_impact = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume")
    course = relationship("Course")
