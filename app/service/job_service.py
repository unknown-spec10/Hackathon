from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.job_schema import JobCreate
from app.repositories import job_repo


def create_job(db: Session, payload: JobCreate):
    return job_repo.create_job(db, payload)


def list_jobs(db: Session):
    return job_repo.get_all_jobs(db)


def get_job(db: Session, job_id: int):
    job = job_repo.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.views = (job.views or 0) + 1
    db.commit()
    db.refresh(job)
    return job


def update_job(db: Session, job_id: int, payload: JobCreate):
    updated = job_repo.update_job(db, job_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated


def delete_job(db: Session, job_id: int):
    ok = job_repo.delete_job(db, job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"msg": "Job deleted"}
