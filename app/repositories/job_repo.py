from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job_schema import JobCreate
from app.utils.deps import get_db

class JobRepository:
    def __init__(self):
        self.db = next(get_db())
    
    def create_job(self, job_data: dict):
        """Create a new job"""
        job = Job(**job_data)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_all_jobs(self):
        """Get all jobs"""
        return self.db.query(Job).all()
    
    def get_job_by_id(self, job_id: int):
        """Get job by ID"""
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def update_job(self, job_id: int, job_data: dict):
        """Update a job"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            for key, value in job_data.items():
                setattr(job, key, value)
            self.db.commit()
            self.db.refresh(job)
            return job
        return None
    
    def delete_job(self, job_id: int):
        """Delete a job"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False

# Legacy functions for backward compatibility
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
