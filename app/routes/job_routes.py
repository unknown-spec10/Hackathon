from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.job_schema import JobCreate, JobResponse
from app.utils.auth_deps import get_current_user
from app.repositories.job_repo import JobRepository

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=List[JobResponse])
async def get_jobs():
    """Get all jobs"""
    job_repo = JobRepository()
    jobs = job_repo.get_all_jobs()
    return [JobResponse.from_orm(job) for job in jobs]

@router.post("/", response_model=JobResponse)
async def create_job(job: JobCreate, current_user = Depends(get_current_user)):
    """Create a new job"""
    job_repo = JobRepository()
    new_job = job_repo.create_job(job.dict())
    return JobResponse.from_orm(new_job)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    """Get specific job by ID"""
    job_repo = JobRepository()
    job = job_repo.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return JobResponse.from_orm(job)

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, job: JobCreate, current_user = Depends(get_current_user)):
    """Update a job"""
    job_repo = JobRepository()
    updated_job = job_repo.update_job(job_id, job.dict())
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return JobResponse.from_orm(updated_job)

@router.delete("/{job_id}")
async def delete_job(job_id: int, current_user = Depends(get_current_user)):
    """Delete a job"""
    job_repo = JobRepository()
    success = job_repo.delete_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return {"message": "Job deleted successfully"}
