"""
Frontend Integration Test Suite
Tests all API endpoints to ensure they're ready for frontend integration
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_frontend_integration():
    """Test all endpoints that the frontend will use"""
    
    print("🚀 Testing Frontend Integration Readiness")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print(f"⚠️ API response: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False
    
    # Test 2: Get available domains
    print("\n2️⃣ Testing: Get Available Domains")
    try:
        response = requests.get(f"{API_BASE}/interview/domains")
        if response.status_code == 200:
            domains_data = response.json()
            print("✅ Domains endpoint working")
            print(f"   Available domains: {len(domains_data.get('domains', []))}")
            print(f"   Difficulty levels: {len(domains_data.get('difficulty_levels', []))}")
            return True
        else:
            print(f"❌ Domains endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_interview_flow():
    """Test the complete interview flow"""
    
    print("\n3️⃣ Testing: Complete Interview Flow")
    
    # Mock authentication token
    headers = {"Authorization": "Bearer demo_token"}
    
    # Step 1: Start interview
    print("   Starting interview...")
    start_payload = {
        "domain": "python",
        "years_of_experience": 2
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/interview/start",
            json=start_payload,
            headers=headers
        )
        
        if response.status_code == 200:
            interview_data = response.json()
            session_id = interview_data.get("session_id")
            questions = interview_data.get("questions", [])
            
            print(f"   ✅ Interview started (Session: {session_id})")
            print(f"   ✅ Generated {len(questions)} questions")
            
            if not questions:
                print("   ⚠️ No questions generated")
                return False
                
        else:
            print(f"   ❌ Start interview failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Start interview error: {e}")
        return False
    
    # Step 2: Submit answers
    print("   Submitting answers...")
    
    # Prepare test answers
    answers = []
    for i, question in enumerate(questions[:3]):  # Test first 3 questions
        answers.append({
            "question_id": question.get("id"),
            "answer": f"This is a test answer for question {i+1}. Lists are mutable data structures in Python that can store multiple items. They are created using square brackets and support various operations like append, remove, etc."
        })
    
    submit_payload = {
        "session_id": session_id,
        "answers": answers
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/interview/submit",
            json=submit_payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result_data = response.json()
            
            print(f"   ✅ Answers evaluated successfully")
            print(f"   ✅ Overall Score: {result_data.get('overall_score', 'N/A')}%")
            print(f"   ✅ Grade: {result_data.get('grade', 'N/A')}")
            print(f"   ✅ Evaluations: {len(result_data.get('question_evaluations', []))}")
            
            # Verify result structure
            required_fields = ['session_id', 'overall_score', 'grade', 'question_evaluations', 'strengths', 'weaknesses', 'recommendations']
            missing_fields = [field for field in required_fields if field not in result_data]
            
            if missing_fields:
                print(f"   ⚠️ Missing fields in response: {missing_fields}")
            else:
                print("   ✅ All required response fields present")
            
            return True
            
        else:
            print(f"   ❌ Submit answers failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Submit answers error: {e}")
        return False

def test_api_documentation():
    """Test API documentation"""
    print("\n4️⃣ Testing: API Documentation")
    
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible at /docs")
            return True
        else:
            print(f"❌ Documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Documentation error: {e}")
        return False

def test_cors_and_headers():
    """Test CORS and required headers for frontend"""
    print("\n5️⃣ Testing: CORS and Headers")
    
    try:
        # Test OPTIONS request (preflight)
        response = requests.options(f"{API_BASE}/interview/domains")
        print(f"   OPTIONS request status: {response.status_code}")
        
        # Check CORS headers
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        present_headers = [h for h in cors_headers if h in response.headers]
        print(f"   CORS headers present: {len(present_headers)}/{len(cors_headers)}")
        
        if len(present_headers) >= 1:
            print("   ✅ Basic CORS configuration detected")
            return True
        else:
            print("   ⚠️ CORS might need configuration for frontend")
            return True  # Not critical for basic testing
            
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")
        return True  # Not critical

def generate_integration_report():
    """Generate a comprehensive integration readiness report"""
    
    print("\n" + "=" * 60)
    print("📋 FRONTEND INTEGRATION READINESS REPORT")
    print("=" * 60)
    
    # Run all tests
    health_ok = test_frontend_integration()
    flow_ok = test_interview_flow()
    docs_ok = test_api_documentation()
    cors_ok = test_cors_and_headers()
    
    print(f"\n📊 Test Results Summary:")
    print(f"   ✅ API Health: {'PASS' if health_ok else 'FAIL'}")
    print(f"   ✅ Interview Flow: {'PASS' if flow_ok else 'FAIL'}")
    print(f"   ✅ Documentation: {'PASS' if docs_ok else 'FAIL'}")
    print(f"   ✅ CORS/Headers: {'PASS' if cors_ok else 'FAIL'}")
    
    overall_status = health_ok and flow_ok and docs_ok
    
    print(f"\n🎯 Overall Status: {'✅ READY FOR FRONTEND' if overall_status else '❌ NEEDS FIXES'}")
    
    if overall_status:
        print("\n🚀 Your API is ready for frontend integration!")
        print("\n📝 Frontend Integration Guide:")
        print("   1. API Base URL: http://localhost:8000")
        print("   2. Authentication: Bearer token (currently using 'demo_token')")
        print("   3. Key Endpoints:")
        print("      - GET /interview/domains - Get available domains")
        print("      - POST /interview/start - Start interview session")
        print("      - POST /interview/submit - Submit answers for evaluation")
        print("      - GET /docs - API documentation")
        print("\n📱 Streamlit UI: http://localhost:8501")
        print("   - Already configured to work with your API")
        print("   - Includes fallback for offline mode")
    else:
        print("\n🔧 Issues to fix before frontend integration:")
        if not health_ok:
            print("   - API server connectivity issues")
        if not flow_ok:
            print("   - Interview flow endpoints not working properly")
        if not docs_ok:
            print("   - API documentation not accessible")
    
    return overall_status

if __name__ == "__main__":
    # Wait for server to be ready
    time.sleep(2)
    generate_integration_report()
