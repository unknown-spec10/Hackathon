"""
Simple Interview Database Migration
Creates interview tables for the AI chatbot system
"""
from sqlalchemy import create_engine
from database.db_setup import Base, SQLALCHEMY_DATABASE_URL

# Import all models to ensure they're registered with Base
from app.models.user import User
from app.models.interview import InterviewSession, QuestionBank, InterviewFeedback
from app.models.profile import Profile
from app.models.job import Job
from app.models.course import Course
from app.models.resume import Resume

def main():
    """Create all database tables"""
    print("🚀 Creating interview database tables...")
    
    try:
        # Create engine
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("✅ Successfully created all database tables including:")
        print("   - interview_sessions")
        print("   - question_bank") 
        print("   - interview_feedback")
        print("   - All existing tables updated with relationships")
        
        print("\n🎉 Database migration completed successfully!")
        print("You can now run the interview chatbot system.")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")

if __name__ == "__main__":
    main()
