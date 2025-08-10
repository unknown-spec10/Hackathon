# Import all models to ensure relationships are properly resolved
from app.models.user import User
from app.models.job import Job
from app.models.course import Course
from app.models.profile import Organization
from app.models.resume import Resume, JobRecommendation, CourseRecommendation

__all__ = [
    "User",
    "Job", 
    "Course",
    "Organization",
    "Resume",
    "JobRecommendation",
    "CourseRecommendation"
]