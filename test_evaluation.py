"""
Simple test to verify the interview evaluation is working properly
"""
import asyncio
import json
from app.services.interview_service import InterviewOrchestrator
from app.models.interview import InterviewDomain
from app.core.settings import settings

async def test_interview_evaluation():
    """Test the complete interview flow"""
    
    print("🧪 Testing Interview Evaluation System")
    print("=" * 50)
    
    # Check if API key is configured
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key":
        print("❌ GROQ_API_KEY not configured properly")
        return
    
    print(f"✅ Using API key: {settings.GROQ_API_KEY[:10]}...")
    
    # Initialize orchestrator
    orchestrator = InterviewOrchestrator(settings.GROQ_API_KEY)
    
    try:
        # Step 1: Generate questions
        print("\n1️⃣ Generating questions...")
        difficulty, questions = await orchestrator.generate_interview_questions(
            domain=InterviewDomain.PYTHON,
            years_experience=2
        )
        
        print(f"✅ Generated {len(questions)} questions")
        print(f"📊 Difficulty: {difficulty.value}")
        
        # Show first question
        if questions:
            first_q = questions[0]
            print(f"\n📝 Sample Question:")
            print(f"   Q: {first_q['question']}")
            print(f"   Type: {first_q.get('type', 'N/A')}")
            print(f"   Ideal Answer: {first_q.get('ideal_answer', 'N/A')[:100]}...")
        
        # Step 2: Test evaluation with sample answers
        print("\n2️⃣ Testing evaluation...")
        
        # Prepare test answers (good and bad)
        test_answers = [
            {
                "question_id": 1,
                "answer": "Lists are mutable and can be changed after creation. Tuples are immutable and cannot be modified. Lists use [] and tuples use ()."
            },
            {
                "question_id": 2,
                "answer": "I don't know"
            }
        ]
        
        # Evaluate answers
        result = await orchestrator.evaluate_interview(
            questions=questions[:2],  # Test with first 2 questions
            answers=test_answers,
            domain=InterviewDomain.PYTHON,
            difficulty=difficulty,
            years_experience=2
        )
        
        print(f"✅ Evaluation complete!")
        print(f"📊 Overall Score: {result.overall_score}%")
        print(f"🎓 Grade: {result.grade}")
        print(f"📈 Accuracy Rate: {result.accuracy_rate}%")
        
        # Show individual question scores
        print(f"\n📋 Question-wise Results:")
        for eval in result.question_evaluations:
            print(f"   Q{eval.question_id}: {eval.score}/10 - {eval.feedback[:50]}...")
        
        # Show recommendations
        print(f"\n💪 Strengths: {result.strengths}")
        print(f"📚 Weaknesses: {result.weaknesses}")
        print(f"🎯 Recommendations: {result.recommendations}")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_interview_evaluation())
