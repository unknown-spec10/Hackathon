# 🚀 Job & Course Platform with AI Resume Processing

A comprehensive FastAPI-based platform for job and course management with intelligent B2C resume processing using LangGraph and AI recommendations.

## 📋 Features

- **Role-Based Authentication**: Separate B2B (companies/institutions) and B2C (individuals) user flows
- **AI Resume Processing**: LangGraph + Groq AI-powered resume parsing and analysis
- **Intelligent Recommendations**: AI-powered job and course recommendations based on resume analysis
- **B2B Features**: Companies can post jobs, institutions can create courses
- **B2C Features**: Individuals can upload resumes, get recommendations, apply for jobs/courses
- **Modern UI**: Streamlit-based comprehensive testing interface

## 🏗️ Architecture

- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite for development
- **Authentication**: JWT with bcrypt + Role-based access (B2B/B2C)
- **AI Engine**: LangGraph workflows with Groq LLM (mixtral-8x7b-32768)
- **PDF Processing**: PDFPlumber for resume text extraction
- **UI**: Streamlit comprehensive testing interface
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file with your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database

```bash
python create_tables.py
```

### 4. Start the Application

**Option 1: Streamlit UI (Recommended for Testing)**
```bash
streamlit run app_ui.py
```
Access at: http://localhost:8501

**Option 2: FastAPI Server**
```bash
python start_server.py
```
Access at: http://localhost:8000

## 🎯 User Flows

### B2B Users (Companies & Institutions)
1. **Register as B2B** → Access company/institution features
2. **Post Jobs** (Companies) → Create job listings with requirements
3. **Create Courses** (Institutions) → Setup educational programs
4. **View Analytics** → Track job/course performance

### B2C Users (Individuals)
1. **Register as B2C** → Access individual features
2. **Upload Resume** → AI-powered parsing with LangGraph + Groq
3. **Get Recommendations** → AI suggests matching jobs and courses
4. **Apply & Enroll** → Submit applications and course enrollments

## 🤖 AI Resume Processing

### LangGraph Workflow
- **State Management**: Tracks parsing progress and data
- **Multi-Step Processing**: Extract → Analyze → Structure → Validate
- **Error Handling**: Robust error recovery and retry logic
- **Confidence Scoring**: AI confidence in parsing accuracy

### Groq AI Integration
- **Model**: mixtral-8x7b-32768 (fast inference)
- **Features**: Text extraction, skill identification, experience analysis
- **Output**: Structured resume data with confidence scores

## 📁 Project Structure

```
├── app/
│   ├── core/                    # Settings and configuration
│   ├── models/                  # SQLAlchemy models (User, Job, Course, Resume)
│   ├── repositories/            # Data access layer
│   ├── schemas/                 # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── langgraph_resume_parser.py  # AI resume parsing
│   │   ├── job_recommender.py          # Job recommendation engine
│   │   ├── course_recommender.py       # Course recommendation engine
│   │   └── pdf_processor.py            # PDF text extraction
│   ├── uploads/resumes/        # Resume file storage
│   └── utils/                  # Authentication utilities
├── database/                   # Database setup and seeding
├── app_ui.py                  # Main Streamlit UI application
├── main.py                    # FastAPI application
├── start_server.py           # API server startup
├── create_tables.py          # Database initialization
└── clear_database.py         # Database cleanup utility
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration (B2B/B2C)
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile

### B2B Endpoints
- `POST /jobs/` - Create job posting (companies)
- `POST /courses/` - Create course (institutions)
- `GET /jobs/company/{company_id}` - Get company jobs
- `GET /courses/institution/{institution_id}` - Get institution courses

### B2C Endpoints
- `POST /resumes/upload` - Upload and process resume
- `GET /resumes/recommendations` - Get AI recommendations
- `POST /jobs/{job_id}/apply` - Apply for job
- `POST /courses/{course_id}/enroll` - Enroll in course

### General
- `GET /jobs/` - List all jobs
- `GET /courses/` - List all courses
- `GET /stats/` - Platform analytics

## 🎮 Testing with Streamlit UI

The comprehensive Streamlit UI provides:

1. **Authentication Testing**
   - B2B/B2C registration and login flows
   - Role-based feature access

2. **B2B Testing**
   - Job posting (companies)
   - Course creation (institutions)
   - Analytics dashboard

3. **B2C Testing**
   - Resume upload and AI processing
   - AI-powered recommendations
   - Application and enrollment

4. **Admin Features**
   - User management
   - System statistics
   - Database operations

## 🔍 AI Recommendation System

### Job Recommendations
- **Skill Matching**: Compare resume skills with job requirements
- **Experience Level**: Match career level with job seniority
- **Industry Alignment**: Consider industry preferences and experience
- **Location Preference**: Factor in location and remote options

### Course Recommendations
- **Skill Gap Analysis**: Identify missing skills for career growth
- **Career Path**: Suggest courses for desired career progression
- **Industry Trends**: Recommend trending skills in user's field
- **Learning Level**: Match course difficulty with user experience

## 🔒 Security & Authentication

- **Role-Based Access**: Separate B2B and B2C feature access
- **JWT Tokens**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt
- **File Upload Security**: Safe resume file handling
- **API Rate Limiting**: Prevent abuse

## 🚀 Getting Started Examples

### B2C User Journey
```python
# 1. Register as B2C user
# 2. Upload resume (PDF)
# 3. AI processes resume with LangGraph + Groq
# 4. Get personalized job/course recommendations
# 5. Apply for jobs or enroll in courses
```

### B2B User Journey
```python
# 1. Register as company/institution
# 2. Create job postings or courses
# 3. View applications and enrollments
# 4. Access analytics and insights
```

## 🎯 Success Metrics

✅ **AI Resume Processing**: LangGraph + Groq integration  
✅ **Role-Based Authentication**: B2B/B2C separation  
✅ **Intelligent Recommendations**: AI-powered matching  
✅ **Comprehensive UI**: Full-featured Streamlit interface  
✅ **File Processing**: PDF resume handling  
✅ **Database Integration**: Complete data persistence  
✅ **Error Handling**: Robust error management  

## 🔮 Future Enhancements

- **Real-time Notifications**: Job/course alerts
- **Advanced Analytics**: ML-powered insights
- **Video Resume Support**: Extended media processing
- **Integration APIs**: Third-party platform connections
- **Mobile App**: React Native application

---

**Start Testing**: `streamlit run app_ui.py` → http://localhost:8501

Happy coding! 🚀
