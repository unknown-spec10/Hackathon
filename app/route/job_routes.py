from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.job_schema import JobCreate
from app.repositories import job_repo
from app.utils.deps import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    return job_repo.create_job(db, job)

@router.get("/")
def get_all_jobs(db: Session = Depends(get_db)):
    return job_repo.get_all_jobs(db)

@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_repo.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}")
def update_job(job_id: int, job: JobCreate, db: Session = Depends(get_db)):
    updated = job_repo.update_job(db, job_id, job)
    if not updated:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    success = job_repo.delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"msg": "Job deleted"}
