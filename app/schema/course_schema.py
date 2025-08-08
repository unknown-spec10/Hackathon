from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class CourseBase(BaseModel):
    name: str
    duration: str
    mode: str  # Online / Offline / Hybrid
    fees: Optional[str]
    description: str
    skills_required: List[str]
    application_deadline: date
    visibility: Optional[str] = "public"

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    id: int

class CourseOut(CourseBase):
    id: int
