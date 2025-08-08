from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.course_schema import CourseCreate
from app.repositories import course_repo


def create_course(db: Session, payload: CourseCreate):
    # Simple validation: dates and minimal checks are already in Pydantic schema
    return course_repo.create_course(db, payload)


def list_courses(db: Session):
    return course_repo.get_all_courses(db)


def get_course(db: Session, course_id: int):
    course = course_repo.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.views = (course.views or 0) + 1
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course_id: int, payload: CourseCreate):
    updated = course_repo.update_course(db, course_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated


def delete_course(db: Session, course_id: int):
    ok = course_repo.delete_course(db, course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"msg": "Course deleted"}
