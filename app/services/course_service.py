from sqlalchemy.orm import Session
from typing import List
from app.models.course import Course
from app.schemas.course_schema import CourseCreate


def create_course(db: Session, course_data: CourseCreate) -> Course:
    """Create a new course in the database"""
    course = Course(
        name=course_data.name,
        provider=course_data.provider,
        duration=course_data.duration,
        mode=course_data.mode,
        fees=course_data.fees,
        description=course_data.description,
        skills_required=course_data.skills_required,
        application_deadline=course_data.application_deadline,
        prerequisites=course_data.prerequisites
    )
    
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def list_courses(db: Session) -> List[Course]:
    """Get all courses from the database"""
    return db.query(Course).all()


def get_course(db: Session, course_id: int) -> Course:
    """Get a specific course by ID"""
    return db.query(Course).filter(Course.id == course_id).first()
