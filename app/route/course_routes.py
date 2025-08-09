from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.course_schema import CourseCreate
from app.service import course_service
from app.utils.deps import get_db
from app.utils.auth_deps import require_b2b_user
from app.models.user import User
from app.models.profile import Organization, OrgTypeEnum

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/")
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    """Create a course - only for Institution type organizations"""
    # Check if user's organization is an Institution
    if current_user.org_id:
        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if not org or org.org_type != OrgTypeEnum.INSTITUTION:
            raise HTTPException(
                status_code=403, 
                detail="Only Institution type organizations can set courses. Companies can post jobs."
            )
    else:
        raise HTTPException(status_code=403, detail="B2B user must have an associated organization")
    
    return course_service.create_course(db, course)

@router.get("/")
def get_all_courses(db: Session = Depends(get_db)):
    return course_service.list_courses(db)

@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    return course_service.get_course(db, course_id)

@router.put("/{course_id}")
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    """Update a course - only for Institution type organizations"""
    # Check organization permissions
    if current_user.org_id:
        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if not org or org.org_type != OrgTypeEnum.INSTITUTION:
            raise HTTPException(
                status_code=403, 
                detail="Only Institution type organizations can modify courses"
            )
    else:
        raise HTTPException(status_code=403, detail="B2B user must have an associated organization")
    
    return course_service.update_course(db, course_id, course)

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    """Delete a course - only for Institution type organizations"""
    # Check organization permissions
    if current_user.org_id:
        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if not org or org.org_type != OrgTypeEnum.INSTITUTION:
            raise HTTPException(
                status_code=403, 
                detail="Only Institution type organizations can delete courses"
            )
    else:
        raise HTTPException(status_code=403, detail="B2B user must have an associated organization")
    
    return course_service.delete_course(db, course_id)
