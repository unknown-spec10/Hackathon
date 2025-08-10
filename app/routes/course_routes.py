from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.course_schema import CourseCreate, CourseResponse
from app.utils.auth_deps import get_current_user
from app.repositories.course_repo import CourseRepository

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=List[CourseResponse])
async def get_courses():
    """Get all courses"""
    course_repo = CourseRepository()
    courses = course_repo.get_all_courses()
    return [CourseResponse.from_orm(course) for course in courses]

@router.post("/", response_model=CourseResponse)
async def create_course(course: CourseCreate, current_user = Depends(get_current_user)):
    """Create a new course"""
    course_repo = CourseRepository()
    new_course = course_repo.create_course(course.dict())
    return CourseResponse.from_orm(new_course)

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int):
    """Get specific course by ID"""
    course_repo = CourseRepository()
    course = course_repo.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return CourseResponse.from_orm(course)

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(course_id: int, course: CourseCreate, current_user = Depends(get_current_user)):
    """Update a course"""
    course_repo = CourseRepository()
    updated_course = course_repo.update_course(course_id, course.dict())
    if not updated_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return CourseResponse.from_orm(updated_course)

@router.delete("/{course_id}")
async def delete_course(course_id: int, current_user = Depends(get_current_user)):
    """Delete a course"""
    course_repo = CourseRepository()
    success = course_repo.delete_course(course_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return {"message": "Course deleted successfully"}
