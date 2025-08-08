def get_job_stats(db, job_id: int):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    
    applications = db.query(Application).filter(Application.job_id == job_id).all()
    total_views = job.views  # assuming we track this in Job model
    
    matched_skills = {}  # Dummy logic — expand later
    for app in applications:
        # compare applicant skills with job.required_skills
        pass
    
    return {
        "views": total_views,
        "applications": len(applications),
        "skill_match": matched_skills
    }

def get_course_stats(db, course_id: int):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return None
    
    applications = db.query(CourseApplication).filter(CourseApplication.course_id == course_id).all()
    total_views = course.views

    education_match = {}  # Dummy logic — match based on applicant.education

    return {
        "views": total_views,
        "enrollments": len(applications),
        "education_match": education_match
    }
