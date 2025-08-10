from pydantic import BaseModel, Field
from typing import Dict


class JobStats(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job")
    views: int = Field(0, description="Number of views on the job post")
    applications_received: int = Field(0, description="Total applications received")
    applicants_by_profession: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of profession to applicant count"
    )
    applicants_by_skills: Dict[str, int] = Field(
        ge=0,
        default_factory=dict,
        description="Mapping of skill to applicant count"
    )


class CourseStats(BaseModel):
    course_id: int = Field(..., description="Unique identifier for the course")
    views: int = Field(0, description="Number of views on the course page")
    enrollments_received: int = Field(0, description="Total enrollments received")
    applicants_by_education: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of education level to applicant count"
    )
    applicants_by_skills: Dict[str, int] = Field(
        ge=0,
        default_factory=dict,
        description="Mapping of skill to applicant count"
    )

class JobStatsResponse(JobStats):
    model_config = {"from_attributes": True}

class CourseStatsResponse(CourseStats):
    model_config = {"from_attributes": True}
