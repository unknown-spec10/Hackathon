from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date
from enum import Enum


class CourseMode(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    HYBRID = "Hybrid"


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, description="Course name", example="Introduction to Python")
    duration: str = Field(
        ..., min_length=1, pattern=r"^\d+\s*(days|weeks|months)$", description="Course duration (e.g., '3 months')", example="3 months"
    )
    mode: CourseMode = Field(..., description="Course mode: Online / Offline / Hybrid", example=CourseMode.ONLINE)
    fees: Optional[float] = Field(None, description="Course fees in numeric format (optional)", example=1000.0)
    description: str = Field(..., min_length=1, description="Course description", example="Learn Python programming basics")
    skills_required: List[str] = Field(..., min_length=1, description="List of required skills", example=["Basic programming"])
    application_deadline: date = Field(..., description="Application deadline for the course", example="2025-12-31")
    prerequisites: List[str] = Field(..., min_length=1, description="List of prerequisite courses", example=["None"])

    @validator("skills_required", "prerequisites", each_item=True)
    def check_non_empty_strings(cls, v):
        if not v.strip():
            raise ValueError("List items cannot be empty")
        return v.strip()

    @validator("skills_required", "prerequisites")
    def remove_duplicates(cls, v):
        return list(dict.fromkeys(v))

    @validator("application_deadline")
    def check_future_date(cls, v):
        if v < date.today():
            raise ValueError("Application deadline must be in the future")
        return v


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    id: int = Field(..., description="ID of the course to update", example=1)


class CourseOut(CourseBase):
    id: int = Field(..., description="Unique course identifier", example=1)

    class Config:
        from_attributes = True