from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"


class PersonalInfo(BaseModel):
    name: str = Field(default="", description="Full name")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    location: str = Field(default="", description="Location (city, state/country)")
    linkedin: str = Field(default="", description="LinkedIn profile URL")
    github: str = Field(default="", description="GitHub profile URL")
    portfolio: str = Field(default="", description="Portfolio website URL")


class Education(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    location: Optional[str] = None


class Experience(BaseModel):
    title: str = Field(default="", description="Job title")
    company: str = Field(default="", description="Company name")
    location: str = Field(default="", description="Work location")
    start_date: str = Field(default="", description="Start date (MM/YYYY format)")
    end_date: str = Field(default="", description="End date (MM/YYYY or Present)")
    description: str = Field(default="", description="Job description and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    achievements: Optional[List[str]] = Field(default_factory=list)


class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = []
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ParsedResumeData(BaseModel):
    personal_info: PersonalInfo
    education: List[Education] = []
    experience: List[Experience] = []
    skills: List[str] = []
    certifications: List[Certification] = []
    languages: List[str] = []
    projects: List[Project] = []
    summary: Optional[str] = None
    achievements: List[str] = []


class ResumeUploadRequest(BaseModel):
    """Request for resume upload"""
    pass  # File will be handled by FastAPI UploadFile


class ResumeResponse(BaseModel):
    id: int
    filename: str
    processing_status: ProcessingStatus
    parsed_data: Optional[ParsedResumeData] = None
    skills_extracted: Optional[List[str]] = None
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    job_match_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class JobRecommendationResponse(BaseModel):
    job_id: int
    title: str
    company: str
    location: Optional[str] = None
    match_score: float
    matching_skills: List[str]
    skill_gaps: List[str]
    recommendation_reason: Optional[str] = None
    
    model_config = {"from_attributes": True}


class CourseRecommendationResponse(BaseModel):
    course_id: int
    title: str
    provider: str
    relevance_score: float
    skill_gaps_addressed: List[str]
    career_impact: Optional[str] = None
    
    model_config = {"from_attributes": True}


class RecommendationsResponse(BaseModel):
    jobs: List[JobRecommendationResponse]
    courses: List[CourseRecommendationResponse]
    total_jobs: int
    total_courses: int


class ResumeSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[Dict[str, int]] = None
    skills_filter: Optional[List[str]] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)


class JobSearchResponse(BaseModel):
    jobs: List[Dict[str, Any]]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class ProcessingProgressResponse(BaseModel):
    status: ProcessingStatus
    progress_percentage: int
    current_step: str
    estimated_time_remaining: Optional[int] = None  # seconds
    error_message: Optional[str] = None

class ResumeUploadResponse(BaseModel):
    """Response for resume upload"""
    id: int
    filename: str
    status: str
    confidence_score: float
    message: str

class ResumeListResponse(BaseModel):
    """Response for listing resumes"""
    id: int
    filename: str
    uploaded_at: str  # ISO format datetime string
    confidence_score: float
    status: str

class ResumeDetailResponse(BaseModel):
    """Response for detailed resume information"""
    id: int
    filename: str
    uploaded_at: str  # ISO format datetime string
    confidence_score: float
    processing_time: float
    parsed_data: dict
    parsing_errors: List[str]
    raw_text: Optional[str] = None  # Include raw extracted text for debugging
