from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.course_schema import CourseCreate
from app.repositories import course_repo
from app.utils.deps import get_db

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/")
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    return course_repo.create_course(db, course)

@router.get("/")
def get_all_courses(db: Session = Depends(get_db)):
    return course_repo.get_all_courses(db)

@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = course_repo.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}")
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db)):
    updated = course_repo.update_course(db, course_id, course)
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    success = course_repo.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"msg": "Course deleted"}
