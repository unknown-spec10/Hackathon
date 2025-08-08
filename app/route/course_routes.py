from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.course_schema import CourseCreate
from app.service import course_service
from app.utils.deps import get_db
from app.utils.auth_deps import require_b2b_user
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/")
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    return course_service.create_course(db, course)

@router.get("/")
def get_all_courses(db: Session = Depends(get_db)):
    return course_service.list_courses(db)

@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    return course_service.get_course(db, course_id)

@router.put("/{course_id}")
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    return course_service.update_course(db, course_id, course)

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    return course_service.delete_course(db, course_id)
