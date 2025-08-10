from database.db_setup import get_db
from app.models.job import Job
from datetime import date

try:
    db = next(get_db())
    jobs = db.query(Job).all()
    print(f'Total jobs in database: {len(jobs)}')
    
    # Check filtering logic
    current_date = date.today()
    active_jobs = db.query(Job).filter(Job.application_deadline >= current_date).all()
    print(f'Active jobs (deadline >= today): {len(active_jobs)}')
    
    if jobs:
        job = jobs[0]
        print(f'Sample job: {job.title}')
        print(f'Application deadline: {job.application_deadline}')
        print(f'Type of skills_required: {type(job.skills_required)}')
        print(f'Skills required: {job.skills_required}')
        print(f'Responsibilities: {job.responsibilities[:100] if job.responsibilities else "None"}...')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
