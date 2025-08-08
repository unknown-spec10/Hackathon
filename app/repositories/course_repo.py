from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course_schema import CourseCreate

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
