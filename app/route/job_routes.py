from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.job_schema import JobCreate
from app.service import job_service
from app.utils.deps import get_db
from app.utils.auth_deps import require_b2b_user
from app.models.user import User
from app.models.profile import Organization, OrgTypeEnum

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/")
def create_job(job: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    """Create a job - only for Company type organizations"""
    # Check if user's organization is a Company
    if current_user.org_id:
        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if not org or org.org_type != OrgTypeEnum.COMPANY:
            raise HTTPException(
                status_code=403, 
                detail="Only Company type organizations can post jobs. Institutions can set courses."
            )
    else:
        raise HTTPException(status_code=403, detail="B2B user must have an associated organization")
    
    return job_service.create_job(db, job)

@router.get("/")
def get_all_jobs(db: Session = Depends(get_db)):
    return job_service.list_jobs(db)

@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.get_job(db, job_id)

@router.put("/{job_id}")
def update_job(job_id: int, job: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    """Update a job - only for Company type organizations"""
    # Check organization permissions
    if current_user.org_id:
        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if not org or org.org_type != OrgTypeEnum.COMPANY:
            raise HTTPException(
                status_code=403, 
                detail="Only Company type organizations can modify jobs"
            )
    else:
        raise HTTPException(status_code=403, detail="B2B user must have an associated organization")
    
    return job_service.update_job(db, job_id, job)

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_b2b_user)):
    """Delete a job - only for Company type organizations"""
    # Check organization permissions
    if current_user.org_id:
        org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
        if not org or org.org_type != OrgTypeEnum.COMPANY:
            raise HTTPException(
                status_code=403, 
                detail="Only Company type organizations can delete jobs"
            )
    else:
        raise HTTPException(status_code=403, detail="B2B user must have an associated organization")
    
    return job_service.delete_job(db, job_id)
