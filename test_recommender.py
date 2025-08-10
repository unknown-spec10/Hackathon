from database.db_setup import get_db
from app.services.job_recommender import JobRecommender

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

try:
    db = next(get_db())
    job_recommender = JobRecommender()
    
    print("Testing job recommendations...")
    recommendations = job_recommender.get_recommendations(test_resume_data, db, limit=5)
    
    print(f"Found {len(recommendations)} recommendations")
    
    for i, rec in enumerate(recommendations):
        print(f"\n{i+1}. {rec.title} at {rec.company}")
        print(f"   Match Score: {rec.match_score:.3f}")
        print(f"   Matching Skills: {rec.matching_skills}")
        print(f"   Reason: {rec.recommendation_reason}")
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
