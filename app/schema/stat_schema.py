from pydantic import BaseModel
from typing import Dict

class JobStats(BaseModel):
    job_id: int
    views: int
    applications_received: int
    applicants_by_profession: Dict[str, int]
    applicants_by_skills: Dict[str, int]

class CourseStats(BaseModel):
    course_id: int
    views: int
    enrollments_received: int
    applicants_by_education: Dict[str, int]
    applicants_by_skills: Dict[str, int]
