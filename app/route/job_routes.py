from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.job_schema import JobCreate
from app.service import job_service
from app.utils.deps import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, job)

@router.get("/")
def get_all_jobs(db: Session = Depends(get_db)):
    return job_service.list_jobs(db)

@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.get_job(db, job_id)

@router.put("/{job_id}")
def update_job(job_id: int, job: JobCreate, db: Session = Depends(get_db)):
    return job_service.update_job(db, job_id, job)

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.delete_job(db, job_id)
