from sqlalchemy.orm import Session
from typing import List
from app.models.job import Job
from app.schemas.job_schema import JobCreate


def create_job(db: Session, job_data: JobCreate) -> Job:
    """Create a new job in the database"""
    job = Job(
        title=job_data.title,
        company_name=job_data.company_name,
        job_type=job_data.job_type,
        location=job_data.location,
        salary_range=job_data.salary_range,
        responsibilities=job_data.responsibilities,
        skills_required=job_data.skills_required,
        application_deadline=job_data.application_deadline,
        industry=job_data.industry,
        remote_option=job_data.remote_option,
        experience_level=job_data.experience_level,
        contact_email=job_data.contact_email,
        application_url=str(job_data.application_url) if job_data.application_url else None,
        posted_date=job_data.posted_date,
        updated_date=job_data.updated_date,
        number_of_openings=job_data.number_of_openings
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> List[Job]:
    """Get all jobs from the database"""
    return db.query(Job).all()


def get_job(db: Session, job_id: int) -> Job:
    """Get a specific job by ID"""
    return db.query(Job).filter(Job.id == job_id).first()
