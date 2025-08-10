# Import all models to ensure relationships are properly resolved
from app.models.user import User
from app.models.job import Job
from app.models.course import Course
from app.models.profile import Organization
from app.models.resume import Resume, JobRecommendation, CourseRecommendation
from app.models.interview import InterviewSession, QuestionBank, InterviewFeedback, DifficultyLevel, InterviewDomain

__all__ = [
    "User",
    "Job", 
    "Course",
    "Organization",
    "Resume",
    "JobRecommendation",
    "CourseRecommendation",
    "InterviewSession",
    "QuestionBank", 
    "InterviewFeedback",
    "DifficultyLevel",
    "InterviewDomain"
]