from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course_schema import CourseCreate
from app.utils.deps import get_db

class CourseRepository:
    def __init__(self):
        self.db = next(get_db())
    
    def create_course(self, course_data: dict):
        """Create a new course"""
        course = Course(**course_data)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def get_all_courses(self):
        """Get all courses"""
        return self.db.query(Course).all()
    
    def get_course_by_id(self, course_id: int):
        """Get course by ID"""
        return self.db.query(Course).filter(Course.id == course_id).first()
    
    def update_course(self, course_id: int, course_data: dict):
        """Update a course"""
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if course:
            for key, value in course_data.items():
                setattr(course, key, value)
            self.db.commit()
            self.db.refresh(course)
            return course
        return None
    
    def delete_course(self, course_id: int):
        """Delete a course"""
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if course:
            self.db.delete(course)
            self.db.commit()
            return True
        return False

# Legacy functions for backward compatibility
def create_course(db: Session, course_data: CourseCreate):
    course = Course(**course_data.dict())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def get_all_courses(db: Session):
    return db.query(Course).all()

def get_course_by_id(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()

def update_course(db: Session, course_id: int, course_data: CourseCreate):
    course = get_course_by_id(db, course_id)
    if not course:
        return None
    for key, value in course_data.dict().items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course

def delete_course(db: Session, course_id: int):
    course = get_course_by_id(db, course_id)
    if course:
        db.delete(course)
        db.commit()
        return True
    return False
