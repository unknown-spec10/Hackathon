# 🎯 API Endpoints Summary

## ✅ FastAPI Server Ready
- **Server URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Total Routes**: 27 endpoints

## 🔐 Authentication Endpoints
- `POST /auth/register` - User registration (B2B/B2C)
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile

## 👥 B2B Endpoints (Companies & Institutions)

### 📋 Job Management
- `GET /jobs/` - List all jobs
- `POST /jobs/` - Create job posting (requires auth)
- `GET /jobs/{job_id}` - Get specific job
- `PUT /jobs/{job_id}` - Update job (requires auth)
- `DELETE /jobs/{job_id}` - Delete job (requires auth)

### 🎓 Course Management
- `GET /courses/` - List all courses
- `POST /courses/` - Create course (requires auth)
- `GET /courses/{course_id}` - Get specific course
- `PUT /courses/{course_id}` - Update course (requires auth)
- `DELETE /courses/{course_id}` - Delete course (requires auth)

### 🏢 Profile Management
- `GET /profile/{org_id}` - Get organization profile
- `PUT /profile/{org_id}` - Update organization profile (requires auth)

## 👤 B2C Endpoints (Individuals)

### 📄 Resume Processing (AI-Powered)
- `POST /resume/upload` - Upload & process resume with LangGraph + Groq AI
- `GET /resume/` - Get user's resumes
- `GET /resume/{resume_id}` - Get detailed resume information
- `DELETE /resume/{resume_id}` - Delete resume
- `GET /resume/recommendations` - Get AI job/course recommendations
- `GET /resume/{resume_id}/job-recommendations` - Get job recommendations for specific resume
- `GET /resume/{resume_id}/course-recommendations` - Get course recommendations for specific resume
- `POST /resume/search-jobs` - Search jobs with AI matching

## 📊 Analytics Endpoints
- `GET /stats/jobs/{job_id}` - Get job statistics
- `GET /stats/courses/{course_id}` - Get course statistics

## 🤖 AI Features
- **Resume Parsing**: LangGraph workflow + Groq LLM (mixtral-8x7b-32768)
- **Job Recommendations**: AI-powered skill matching
- **Course Recommendations**: Skill gap analysis
- **Confidence Scoring**: AI confidence in parsing accuracy

## 🎮 Testing Options

### Option 1: Streamlit UI (Recommended)
```bash
streamlit run app_ui.py
```
- Full B2B/B2C user flows
- AI resume processing
- File uploads
- Recommendations testing
- No API calls needed (direct function calls)

### Option 2: API Documentation
- Visit http://localhost:8000/docs
- Interactive Swagger UI
- Test all endpoints directly
- Authentication flow testing

### Option 3: cURL Examples

#### Register B2C User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "user_type": "B2C",
    "username": "testuser"
  }'
```

#### Upload Resume (requires auth token)
```bash
curl -X POST "http://localhost:8000/resume/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"
```

#### Get Recommendations (requires auth token)
```bash
curl -X GET "http://localhost:8000/resume/recommendations" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🚀 Ready for Testing!

**Recommended Workflow:**
1. ✅ **FastAPI Server**: Running on http://localhost:8000
2. 🎮 **Streamlit UI**: Run `streamlit run app_ui.py` for comprehensive testing
3. 📚 **API Docs**: Visit http://localhost:8000/docs for endpoint exploration

All 27 API endpoints are ready for testing via Streamlit UI! 🎉
