from pydantic import BaseModel, Field, validator
from typing import Dict


class JobStats(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job", example=1)
    views: int = Field(0, ge=0, description="Number of views on the job post", example=100)
    applications_received: int = Field(0, ge=0, description="Total applications received", example=50)
    applicants_by_profession: Dict[str, int] = Field(
        default_factory=dict, description="Mapping of profession to applicant count", example={"Engineer": 10, "Designer": 5}
    )
    applicants_by_skills: Dict[str, int] = Field(
        default_factory=dict, description="Mapping of skill to applicant count", example={"Python": 8, "SQL": 6}
    )

    @validator("applicants_by_profession", "applicants_by_skills", pre=True)
    def check_dictionary(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Must be a dictionary")
        return {k.strip(): v for k, v in v.items() if k.strip()}

    @validator("applicants_by_profession", "applicants_by_skills")
    def check_non_negative_values(cls, v):
        for key, value in v.items():
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Value for {key} must be a non-negative integer")
        return v

    class Config:
        from_attributes = True


class JobStatsCreate(JobStats):
    pass


class JobStatsUpdate(JobStats):
    job_id: int = Field(..., description="Unique identifier for the job", example=1)


class CourseStats(BaseModel):
    course_id: int = Field(..., description="Unique identifier for the course", example=1)
    views: int = Field(0, ge=0, description="Number of views on the course page", example=200)
    enrollments_received: int = Field(0, ge=0, description="Total enrollments received", example=30)
    applicants_by_education: Dict[str, int] = Field(
        default_factory=dict, description="Mapping of education level to applicant count", example={"Bachelor's": 20, "Master's": 10}
    )
    applicants_by_skills: Dict[str, int] = Field(
        default_factory=dict, description="Mapping of skill to applicant count", example={"Python": 15, "Java": 5}
    )

    @validator("applicants_by_education", "applicants_by_skills", pre=True)
    def check_dictionary(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Must be a dictionary")
        return {k.strip(): v for k, v in v.items() if k.strip()}

    @validator("applicants_by_education", "applicants_by_skills")
    def check_non_negative_values(cls, v):
        for key, value in v.items():
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Value for {key} must be a non-negative integer")
        return v

    class Config:
        from_attributes = True


class CourseStatsCreate(CourseStats):
    pass


class CourseStatsUpdate(CourseStats):
    course_id: int = Field(..., description="Unique identifier for the course", example=1)