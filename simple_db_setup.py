"""
Minimal Interview Database Setup
Creates only the interview tables needed for the chatbot
"""
from sqlalchemy import create_engine
from database.db_setup import Base, SQLALCHEMY_DATABASE_URL

# Import only the models we need
from app.models.user import User
from app.models.interview import InterviewSession, QuestionBank, InterviewFeedback

def main():
    """Create interview database tables"""
    print("🚀 Setting up interview database...")
    
    try:
        # Create engine
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        # Create all tables (will only create missing ones)
        Base.metadata.create_all(engine)
        
        print("✅ Database setup completed!")
        print("Created tables:")
        print("   - users (if not exists)")
        print("   - interview_sessions")
        print("   - question_bank")
        print("   - interview_feedback")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Current database tables: {len(tables)}")
        for table in sorted(tables):
            print(f"   - {table}")
        
        print("\n🎉 Interview system is ready to use!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
