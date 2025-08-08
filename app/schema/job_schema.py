from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class JobBase(BaseModel):
    title: str
    job_type: str  # Full-time / Internship / Contract
    location: str
    salary_range: str
    responsibilities: Optional[str]
    skills_required: List[str]
    application_deadline: date
    visibility: Optional[str] = "public"

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    id: int

class JobOut(JobBase):
    id: int
