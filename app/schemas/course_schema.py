from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum


class CourseMode(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    HYBRID = "Hybrid"


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, description="Course name")
    duration: str = Field(..., min_length=1, description="Course duration (e.g., '3 months')")
    mode: CourseMode = Field(..., description="Course mode: Online / Offline / Hybrid")
    fees: Optional[str] = Field(None, min_length=1, description="Course fees (optional)")
    description: str = Field(..., min_length=1, description="Course description")
    skills_required: List[str] = Field(..., min_length=1, description="List of required skills")
    application_deadline: date = Field(..., description="Application deadline for the course")
    prerequisites: List[str] = Field(..., min_length=1, description="List of prerequisite courses")

class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    id: int = Field(..., description="ID of the course to update")


class CourseOut(CourseBase):
    id: int = Field(..., description="Unique course identifier")

    model_config = {"from_attributes": True}