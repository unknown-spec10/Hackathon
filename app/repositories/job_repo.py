from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job_schema import JobCreate

def create_job(db: Session, job_data: JobCreate):
    job = Job(**job_data.dict())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_all_jobs(db: Session):
    return db.query(Job).all()

def get_job_by_id(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()

def update_job(db: Session, job_id: int, job_data: JobCreate):
    job = get_job_by_id(db, job_id)
    if not job:
        return None
    for key, value in job_data.dict().items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job

def delete_job(db: Session, job_id: int):
    job = get_job_by_id(db, job_id)
    if job:
        db.delete(job)
        db.commit()
        return True
    return False
