from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
from typing import List, Optional, Tuple
from datetime import date
from enum import Enum


class JobType(str, Enum):
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"
    PART_TIME = "Part-time"


class RemoteOption(str, Enum):
    REMOTE = "Remote"
    ONSITE = "On-site"
    HYBRID = "Hybrid"


class ExperienceLevel(str, Enum):
    ENTRY = "Entry"
    MID = "Mid"
    SENIOR = "Senior"


class JobBase(BaseModel):
    title: str = Field(..., min_length=1, description="Job title", example="Software Engineer")
    job_type: JobType = Field(..., description="Job type (Full-time / Internship / etc.)", example=JobType.FULL_TIME)
    location: str = Field(..., pattern=r"^[A-Za-z\s]+,\s*[A-Za-z\s]+$", description="Job location (e.g., 'New York, USA')", example="New York, USA")
    salary_range: str = Field(
        ..., pattern=r"^\$\d{1,3}(,\d{3})*\s*-\s*\$\d{1,3}(,\d{3})*$", description="Salary range (e.g., '$50,000 - $70,000')", example="$50,000 - $70,000"
    )
    responsibilities: Optional[List[str]] = Field(None, description="List of job responsibilities", example=["Develop software", "Collaborate with team"])
    skills_required: List[str] = Field(..., min_length=1, description="List of required skills", example=["Python", "SQL"])
    application_deadline: date = Field(..., description="Deadline for applications", example="2025-12-31")
    industry: Optional[str] = Field(None, description="Industry sector", example="Technology")
    remote_option: Optional[RemoteOption] = Field(None, description="Remote work option", example=RemoteOption.HYBRID)
    experience_level: Optional[ExperienceLevel] = Field(None, description="Experience level required", example=ExperienceLevel.MID)
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for application", example="hr@company.com")
    application_url: Optional[HttpUrl] = Field(None, description="External URL for applying", example="https://company.com/apply")
    posted_date: Optional[date] = Field(None, description="Date job was posted", example="2025-08-09")
    updated_date: Optional[date] = Field(None, description="Date job was last updated", example="2025-08-09")
    number_of_openings: Optional[int] = Field(1, ge=1, description="Number of openings", example=2)

    @validator("skills_required", each_item=True)
    def check_non_empty_strings(cls, v):
        if not v.strip():
            raise ValueError("Skills cannot be empty")
        return v.strip()

    @validator("skills_required")
    def remove_duplicates(cls, v):
        return list(dict.fromkeys(v))

    @validator("application_deadline")
    def check_future_date(cls, v):
        if v < date.today():
            raise ValueError("Application deadline must be in the future")
        return v


class JobCreate(JobBase):
    posted_date: date = Field(default_factory=date.today, description="Date job was posted")


class JobUpdate(JobBase):
    id: int = Field(..., description="ID of the job to update", example=1)


class JobOut(JobBase):
    id: int = Field(..., description="Unique job ID", example=1)

    class Config:
        from_attributes = True