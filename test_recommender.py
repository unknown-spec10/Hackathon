from database.db_setup import get_db, Base, engine
# Import all models to ensure relationships are properly resolved
from app.models import User, Job, Course, Resume
from app.services.job_recommender import JobRecommender
from app.services.course_recommender import CourseRecommender
from app.schemas.job_schema import JobCreate
from app.schemas.course_schema import CourseCreate
from app.services import job_service, course_service
from datetime import date

# Test data
test_resume_data = {
    'skills': ['Python', 'FastAPI', 'SQL', 'Machine Learning'],
    'experience': [
        {
            'title': 'Software Engineer',
            'start_date': '2022',
            'end_date': '2024',
            'description': 'Developed web applications using Python and FastAPI'
        }
    ],
    'education': [
        {
            'degree': 'Bachelor of Computer Science'
        }
    ],
    'summary': 'Experienced software engineer with expertise in Python and backend development'
}

def create_test_data(db):
    """Create some test jobs and courses"""
    print("Creating test data...")
    
    # Create test jobs
    test_jobs = [
        JobCreate(
            title="Senior Python Developer",
            company_name="TechCorp Inc",
            job_type="Full-time",
            location="Remote",
            salary_range="$100k-$140k",
            responsibilities="Develop backend services with Python and FastAPI",
            skills_required=["Python", "FastAPI", "SQL", "Docker"],
            application_deadline=date(2025, 12, 31),
            industry="Software",
            remote_option="Remote",
            experience_level="Senior",
            number_of_openings=2
        ),
        JobCreate(
            title="Machine Learning Engineer",
            company_name="AI Solutions Ltd",
            job_type="Full-time", 
            location="San Francisco",
            salary_range="$120k-$160k",
            responsibilities="Build ML models and data pipelines",
            skills_required=["Python", "Machine Learning", "TensorFlow", "SQL"],
            application_deadline=date(2025, 11, 30),
            industry="AI/ML",
            remote_option="Hybrid",
            experience_level="Mid",
            number_of_openings=1
        ),
        JobCreate(
            title="Frontend Developer",
            company_name="WebDev Studio",
            job_type="Full-time",
            location="New York", 
            salary_range="$80k-$110k",
            responsibilities="Build modern web applications",
            skills_required=["JavaScript", "React", "CSS", "HTML"],
            application_deadline=date(2025, 10, 31),
            industry="Web Development",
            remote_option="On-site",
            experience_level="Mid",
            number_of_openings=3
        )
    ]
    
    # Create test courses
    test_courses = [
        CourseCreate(
            name="Advanced Python for Web Development",
            provider="Tech University",
            duration="8 weeks",
            mode="Online",
            fees="$299",
            description="Master Python web development with FastAPI and Django",
            skills_required=["Python", "FastAPI", "Django", "REST APIs"],
            application_deadline=date(2025, 9, 30),
            prerequisites=["Basic Python"]
        ),
        CourseCreate(
            name="Machine Learning Fundamentals",
            provider="Data Science Institute",
            duration="12 weeks",
            mode="Online",
            fees="$599",
            description="Learn ML algorithms and practical implementation",
            skills_required=["Python", "Machine Learning", "Statistics", "Pandas"],
            application_deadline=date(2025, 10, 15),
            prerequisites=["Python basics", "Mathematics"]
        ),
        CourseCreate(
            name="Full Stack JavaScript Development",
            provider="Code Academy Pro",
            duration="16 weeks",
            mode="Hybrid",
            fees="$899",
            description="Complete JavaScript development from frontend to backend",
            skills_required=["JavaScript", "React", "Node.js", "MongoDB"],
            application_deadline=date(2025, 11, 1),
            prerequisites=["HTML", "CSS"]
        )
    ]
    
    # Add jobs to database
    for job_data in test_jobs:
        job_service.create_job(db, job_data)
    
    # Add courses to database  
    for course_data in test_courses:
        course_service.create_course(db, course_data)
    
    db.commit()
    print(f"✅ Created {len(test_jobs)} test jobs and {len(test_courses)} test courses")

try:
    # Create tables if they don't exist
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    db = next(get_db())
    
    # Check if we need to create test data
    job_count = db.query(Job).count()
    course_count = db.query(Course).count()
    
    if job_count == 0 or course_count == 0:
        create_test_data(db)
    
    job_recommender = JobRecommender()
    course_recommender = CourseRecommender()
    
    # Test job recommendations
    print("\nTesting job recommendations...")
    all_jobs = db.query(Job).all()
    print(f"Found {len(all_jobs)} jobs in database")
    
    if all_jobs:
        job_recommendations = job_recommender.get_recommendations(test_resume_data, all_jobs)
        
        print(f"Found {len(job_recommendations)} job recommendations")
        
        for i, rec in enumerate(job_recommendations):
            print(f"\n{i+1}. {rec['job'].title}")
            if hasattr(rec['job'], 'company_name') and rec['job'].company_name:
                print(f"   Company: {rec['job'].company_name}")
            print(f"   Match Score: {rec['score']:.3f}")
            print(f"   Matching Skills: {rec['matching_skills']}")
            print(f"   Reason: {rec['reasons'][0] if rec['reasons'] else 'N/A'}")
    else:
        print("No jobs in database to test with")
    
    # Test course recommendations
    print("\n" + "="*50)
    print("Testing course recommendations...")
    all_courses = db.query(Course).all()
    print(f"Found {len(all_courses)} courses in database")
    
    if all_courses:
        course_recommendations = course_recommender.get_recommendations(test_resume_data, all_courses)
        
        print(f"Found {len(course_recommendations)} course recommendations")
        
        for i, rec in enumerate(course_recommendations):
            print(f"\n{i+1}. {rec['course'].name}")
            if hasattr(rec['course'], 'provider') and rec['course'].provider:
                print(f"   Provider: {rec['course'].provider}")
            print(f"   Relevance Score: {rec['score']:.3f}")
            print(f"   Skills Addressed: {rec['skill_gaps_addressed']}")
            print(f"   Career Impact: {rec['career_impact']}")
    else:
        print("No courses in database to test with")
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
