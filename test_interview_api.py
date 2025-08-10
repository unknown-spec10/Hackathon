"""
Test Script for AI Interview Chatbot System
Tests all the interview API endpoints
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_interview_system():
    """Test the complete interview workflow"""
    
    print("🧪 Testing AI Interview Chatbot System")
    print("=" * 50)
    
    # Test 1: Get available domains
    print("\n1️⃣ Testing: Get Available Domains")
    try:
        response = requests.get(f"{API_BASE}/interview/domains")
        if response.status_code == 200:
            domains_data = response.json()
            print("✅ Success! Available domains:")
            for domain in domains_data.get('domains', []):
                print(f"   - {domain}")
            print(f"Difficulty levels: {domains_data.get('difficulty_levels', [])}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Start an interview
    print("\n2️⃣ Testing: Start Interview")
    try:
        start_data = {
            "domain": "python",
            "years_of_experience": 3
        }
        
        response = requests.post(
            f"{API_BASE}/interview/start",
            json=start_data,
            headers={"Authorization": "Bearer demo_token"}
        )
        
        if response.status_code == 200:
            interview_data = response.json()
            session_id = interview_data.get('session_id')
            questions = interview_data.get('questions', [])
            
            print(f"✅ Success! Interview started:")
            print(f"   Session ID: {session_id}")
            print(f"   Generated {len(questions)} questions")
            print(f"   Difficulty: {interview_data.get('difficulty')}")
            
            # Show first question
            if questions:
                print(f"\n📝 Sample Question:")
                print(f"   Q: {questions[0].get('question', 'N/A')}")
                print(f"   Type: {questions[0].get('type', 'N/A')}")
            
            return session_id, questions
            
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return None, []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, []
    
def test_answer_submission(session_id, questions):
    """Test answer submission and evaluation"""
    if not session_id or not questions:
        print("\n⏭️ Skipping answer submission test (no session/questions)")
        return
    
    print("\n3️⃣ Testing: Submit Answers")
    try:
        # Prepare sample answers
        answers = []
        for i, question in enumerate(questions[:3]):  # Test with first 3 questions
            answers.append({
                "question_id": question.get('id'),
                "answer": f"Sample answer for question {i+1}: This is a detailed response showing understanding of the concept."
            })
        
        submit_data = {
            "session_id": session_id,
            "answers": answers
        }
        
        response = requests.post(
            f"{API_BASE}/interview/submit",
            json=submit_data,
            headers={"Authorization": "Bearer demo_token"}
        )
        
        if response.status_code == 200:
            result_data = response.json()
            
            print("✅ Success! Interview evaluated:")
            print(f"   Overall Score: {result_data.get('overall_score', 'N/A')}%")
            print(f"   Grade: {result_data.get('grade', 'N/A')}")
            print(f"   Questions Evaluated: {len(result_data.get('question_evaluations', []))}")
            
            # Show sample evaluation
            evaluations = result_data.get('question_evaluations', [])
            if evaluations:
                eval_sample = evaluations[0]
                print(f"\n📊 Sample Evaluation:")
                print(f"   Score: {eval_sample.get('score', 'N/A')}/10")
                print(f"   Feedback: {eval_sample.get('feedback', 'N/A')[:100]}...")
            
            # Show recommendations
            recommendations = result_data.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Recommendations ({len(recommendations)}):")
                for rec in recommendations[:2]:  # Show first 2
                    print(f"   - {rec}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_api_documentation():
    """Test API documentation endpoint"""
    print("\n4️⃣ Testing: API Documentation")
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("✅ Success! API documentation available at: http://localhost:8000/docs")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Starting API Tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Test domains endpoint
    test_interview_system()
    
    # Start an interview and test submission
    session_id, questions = test_interview_system()
    test_answer_submission(session_id, questions)
    
    # Test documentation
    test_api_documentation()
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\n📋 Next Steps:")
    print("1. ✅ FastAPI server running at: http://localhost:8000")
    print("2. ✅ Streamlit UI running at: http://localhost:8501")
    print("3. ✅ API docs available at: http://localhost:8000/docs")
    print("4. 🧪 Test the complete flow in the Streamlit interface")
    print("5. 🔧 Connect real LLM API (currently using mock responses)")

if __name__ == "__main__":
    main()
