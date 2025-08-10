# Hackathon API - AI-Powered Resume Processing Platform

## 🏗️ Architecture Overview

**Core Workflow**: Resume Upload → PDF Processing → AI Parsing → Career Insights → Job/Course Recommendations

- **Backend**: FastAPI with SQLAlchemy ORM
- **AI Engine**: LangGraph + Groq (llama3-70b-8192) for resume parsing
- **NLP Analysis**: Dynamic keyword generation with career insights
- **Frontend**: Streamlit for testing and demonstration
- **Database**: SQLite (development) / PostgreSQL (production)

## 📁 Project Structure

```
├── app/                          # Core application
│   ├── models/                   # Database models (User, Resume, Job, Course)
│   ├── routes/                   # API endpoints
│   ├── services/                 # Business logic
│   │   ├── langgraph_resume_parser.py    # AI-powered resume parsing
│   │   ├── nlp_insights.py              # Career insights & analysis
│   │   ├── pdf_processor.py             # PDF text extraction
│   │   ├── job_recommender.py           # Job matching engine
│   │   └── course_recommender.py        # Course recommendations
│   ├── schemas/                  # Pydantic models for API
│   └── utils/                    # Authentication & utilities
├── database/                     # Database setup and utilities
├── tests/                        # Test suites
├── config/                       # Configuration files
├── streamlit_ui_clean.py         # Main UI application
├── main.py                       # FastAPI application entry point
└── requirements.txt              # Dependencies with specific versions
```

## 🚀 Quick Start

### Local Development
1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Environment**
   ```bash
   cp .env.example .env
   # Add your GROQ_API_KEY
   ```

3. **Initialize Database**
   ```bash
   python database/db_setup.py
   python database/seed.py
   ```

4. **Run Applications**
   ```bash
   # FastAPI Backend
   uvicorn main:app --reload --port 8000
   
   # Streamlit Frontend
   streamlit run streamlit_ui_clean.py --server.port 8501
   ```

### 🌐 Streamlit Cloud Deployment

**Ready for one-click deployment!**

1. **Deploy to Streamlit Cloud**
   - Push to GitHub
   - Connect repository to [share.streamlit.io](https://share.streamlit.io)
   - Set main file: `streamlit_ui_clean.py`

2. **Add Secrets in Streamlit Cloud**
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
   GROQ_API_URL = "https://api.groq.com/v1"
   PROJECT_NAME = "AI Interview & Resume Analyzer"
   SECRET_KEY = "your_secure_secret_key_for_production"
   DATABASE_URL = "sqlite:///./hackathon.db"
   ```

3. **Access Your App**
   - Live URL: `https://your-app-name.streamlit.app`
   - Auto-deploys on GitHub push

📖 **Full deployment guide**: See `STREAMLIT_CLOUD_DEPLOYMENT.md`

## 🔑 Key Features

### AI Resume Processing
- **LangGraph Workflow**: Multi-stage parsing pipeline
- **Groq Integration**: Fast AI inference with llama3-70b-8192
- **Dynamic Keyword Generation**: AI-powered skill extraction
- **Career Insights**: Personality traits, trajectory analysis, recommendations

### Intelligent Matching
- **Job Recommendations**: Skill-based matching with gap analysis
- **Course Suggestions**: Learning path recommendations
- **Score Calculation**: Confidence-based ranking system

### User Management
- **Multi-role System**: Job Seekers, Employers, Course Providers
- **Organization Support**: Company-based user management
- **Authentication**: JWT-based secure access

## 🧪 Testing

```bash
# Run specific test suites
python -m pytest tests/test_nlp_insights.py
python -m pytest tests/test_ai_dynamic_keywords.py
python -m pytest tests/test_complete_workflow_insights.py
```

## 📊 API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /resume/upload` - Resume upload and processing
- `GET /resume/{id}/jobs` - Job recommendations
- `GET /resume/{id}/courses` - Course recommendations
- `GET /stats/overview` - System statistics

## 🎯 Recent Improvements

- ✅ Dynamic AI keyword generation
- ✅ Enhanced career trajectory analysis
- ✅ Improved serialization handling
- ✅ Streamlined codebase organization
- ✅ Updated dependencies with specific versions

## 🔧 Configuration

Key environment variables:
- `GROQ_API_KEY`: Groq API key for AI processing
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: JWT token signing key

## 📈 Performance

- **Resume Processing**: ~2-3 seconds per resume
- **AI Analysis**: 7-day TTL caching for keywords
- **Database**: Optimized queries with proper indexing
- **API Response**: <200ms for standard operations
