from fastapi import APIRouter, HTTPException, status
from app.schemas.stat_schema import JobStatsResponse, CourseStatsResponse
from app.repositories.stat_repo import StatRepository

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/jobs/{job_id}", response_model=JobStatsResponse)
async def get_job_stats(job_id: int):
    """Get job statistics"""
    stat_repo = StatRepository()
    stats = stat_repo.get_job_stats(job_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job statistics not found"
        )
    return JobStatsResponse.from_orm(stats)

@router.get("/courses/{course_id}", response_model=CourseStatsResponse)
async def get_course_stats(course_id: int):
    """Get course statistics"""
    stat_repo = StatRepository()
    stats = stat_repo.get_course_stats(course_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course statistics not found"
        )
    return CourseStatsResponse.from_orm(stats)
