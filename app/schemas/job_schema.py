from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional
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
    title: str = Field(..., min_length=1, description="Job title")
    company_name: Optional[str] = Field(None, description="Company name")
    job_type: JobType = Field(..., description="Job type Full-time / Internship)")
    location: str = Field(..., min_length=1, description="Job location")
    salary_range: str = Field(..., min_length=1, description="Salary range")
    responsibilities: Optional[str] = Field(None, description="Job responsibilities")
    skills_required: List[str] = Field(..., min_length=1, description="List of required skills")
    application_deadline: date = Field(..., description="Deadline for applications")
    industry: Optional[str] = Field(None, description="Industry sector")
    remote_option: Optional[RemoteOption] = Field(None, description="Remote work option")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Experience level required")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for application")
    application_url: Optional[HttpUrl] = Field(None, description="External URL for applying")
    posted_date: Optional[date] = Field(None, description="Date job was posted")
    updated_date: Optional[date] = Field(None, description="Date job was last updated")
    number_of_openings: Optional[int] = Field(1, ge=1, description="Number of openings")


class JobCreate(JobBase):
    pass


class JobUpdate(JobBase):
    id: int = Field(..., description="ID of the job to update")


class JobOut(JobBase):
    id: int = Field(..., description="Unique job ID")

    model_config = {"from_attributes": True}

class JobResponse(JobBase):
    id: int = Field(..., description="Unique job ID")

    model_config = {"from_attributes": True}
