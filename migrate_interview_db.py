"""
Database Migration Script for Interview System
Creates all necessary tables for the AI interview chatbot
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, MetaData
from app.models.interview import InterviewSession, QuestionBank, InterviewFeedback
from app.models.user import User
from database.db_setup import Base, get_database_url

def create_interview_tables():
    """Create all interview-related tables"""
    try:
        # Get database URL
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        print("🔧 Creating interview system tables...")
        
        # Create all tables defined in models
        Base.metadata.create_all(engine)
        
        print("✅ Successfully created interview tables:")
        print("   - interview_sessions")
        print("   - question_bank")
        print("   - interview_feedback")
        print("   - Updated user relationships")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating interview tables: {str(e)}")
        return False

def seed_question_bank():
    """Seed the question bank with sample questions"""
    from sqlalchemy.orm import sessionmaker
    from app.models.interview import QuestionBank, InterviewDomain, DifficultyLevel
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🌱 Seeding question bank with sample questions...")
        
        # Sample questions for different domains and difficulties
        sample_questions = [
            # Python - Fresher
            {
                "domain": InterviewDomain.PYTHON,
                "difficulty": DifficultyLevel.FRESHER,
                "question": "What is the difference between a list and a tuple in Python?",
                "expected_answer": "Lists are mutable, tuples are immutable. Lists use [], tuples use ().",
                "question_type": "conceptual"
            },
            {
                "domain": InterviewDomain.PYTHON,
                "difficulty": DifficultyLevel.FRESHER,
                "question": "Write a Python function to check if a number is even or odd.",
                "expected_answer": "def is_even(n): return n % 2 == 0",
                "question_type": "coding"
            },
            
            # Python - Intermediate
            {
                "domain": InterviewDomain.PYTHON,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "question": "Explain Python decorators with an example.",
                "expected_answer": "Decorators modify function behavior. @decorator syntax.",
                "question_type": "conceptual"
            },
            {
                "domain": InterviewDomain.PYTHON,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "question": "Implement a binary search algorithm in Python.",
                "expected_answer": "Recursive or iterative approach with O(log n) complexity.",
                "question_type": "coding"
            },
            
            # Data Science - Fresher
            {
                "domain": InterviewDomain.DATA_SCIENCE,
                "difficulty": DifficultyLevel.FRESHER,
                "question": "What is the difference between supervised and unsupervised learning?",
                "expected_answer": "Supervised uses labeled data, unsupervised finds patterns in unlabeled data.",
                "question_type": "conceptual"
            },
            
            # Data Science - Intermediate
            {
                "domain": InterviewDomain.DATA_SCIENCE,
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "question": "Explain the bias-variance tradeoff in machine learning.",
                "expected_answer": "Balance between model complexity and generalization ability.",
                "question_type": "conceptual"
            },
            
            # JavaScript - Fresher
            {
                "domain": InterviewDomain.JAVASCRIPT,
                "difficulty": DifficultyLevel.FRESHER,
                "question": "What is the difference between var, let, and const in JavaScript?",
                "expected_answer": "var: function scope, let/const: block scope, const: immutable.",
                "question_type": "conceptual"
            }
        ]
        
        # Add questions to database
        for q_data in sample_questions:
            question = QuestionBank(
                domain=q_data["domain"],
                difficulty=q_data["difficulty"],
                question=q_data["question"],
                expected_answer=q_data["expected_answer"],
                question_type=q_data["question_type"]
            )
            session.add(question)
        
        session.commit()
        session.close()
        
        print(f"✅ Successfully seeded {len(sample_questions)} sample questions")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding question bank: {str(e)}")
        return False

def verify_tables():
    """Verify that all tables were created successfully"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Get table names
        metadata = MetaData()
        metadata.reflect(bind=engine)
        tables = list(metadata.tables.keys())
        
        print("📋 Existing database tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        # Check for interview tables
        interview_tables = [
            'interview_sessions',
            'question_bank', 
            'interview_feedback'
        ]
        
        missing_tables = [table for table in interview_tables if table not in tables]
        
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
            return False
        else:
            print("✅ All interview tables exist")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying tables: {str(e)}")
        return False

def main():
    """Run the complete migration process"""
    print("🚀 Starting Interview System Database Migration")
    print("=" * 50)
    
    # Step 1: Create tables
    if not create_interview_tables():
        print("❌ Migration failed at table creation")
        return False
    
    print()
    
    # Step 2: Verify tables
    if not verify_tables():
        print("❌ Migration failed at table verification")
        return False
    
    print()
    
    # Step 3: Seed question bank
    if not seed_question_bank():
        print("⚠️  Migration completed but seeding failed")
        return True  # Tables created successfully
    
    print()
    print("🎉 Interview System Migration Completed Successfully!")
    print("=" * 50)
    print("✅ Database is ready for interview operations")
    print("🔗 You can now:")
    print("   - Start the FastAPI server: uvicorn main:app --reload")
    print("   - Test the Streamlit UI: streamlit run interview_chatbot_ui.py")
    print("   - Use the interview API endpoints")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
