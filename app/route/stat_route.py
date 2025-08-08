from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.deps import get_db
from app.repositories import stat_repo

router = APIRouter(prefix="/stats", tags=["Stats"])

# Job Stats
@router.get("/jobs/{job_id}")
def job_stats(job_id: int, db: Session = Depends(get_db)):
    stats = stat_repo.get_job_stats(db, job_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Job not found")
    return stats

# Course Stats
@router.get("/courses/{course_id}")
def course_stats(course_id: int, db: Session = Depends(get_db)):
    stats = stat_repo.get_course_stats(db, course_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Course not found")
    return stats
