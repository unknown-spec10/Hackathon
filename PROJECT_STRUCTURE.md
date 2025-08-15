# Hackathon Resume Processing API

## Project Structure

```
hackathon/
├── main.py                     # FastAPI application entry point
├── streamlit_app.py           # Frontend UI application
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── hackathon.db              # SQLite database
│
├── app/                       # Main application package
│   ├── core/                  # Core configuration
│   │   ├── config.py
│   │   └── settings.py
│   │
│   ├── models/                # Database models
│   │   ├── user.py
│   │   ├── resume.py
│   │   ├── job.py
│   │   ├── course.py
│   │   └── profile.py
│   │
│   ├── schemas/               # Pydantic schemas
│   │   ├── user_schema.py
│   │   ├── resume_schema.py
│   │   ├── job_schema.py
│   │   └── course_schema.py
│   │
│   ├── routes/                # API route handlers
│   │   ├── auth_routes.py
│   │   ├── resume_routes.py
│   │   ├── job_routes.py
│   │   ├── course_routes.py
│   │   └── profile_routes.py
│   │
│   ├── services/              # Business logic services
│   │   ├── langgraph_resume_parser.py    # AI-powered resume parsing
│   │   ├── langextract_resume_processor.py # LangExtract integration
│   │   ├── pdf_processor.py              # PDF text extraction
│   │   ├── nlp_insights.py               # NLP analysis
│   │   ├── job_recommender.py            # Job recommendation engine
│   │   └── course_recommender.py         # Course recommendation engine
│   │
│   ├── repositories/          # Data access layer
│   │   ├── user_repo.py
│   │   ├── job_repo.py
│   │   └── profile_repo.py
│   │
│   └── utils/                 # Utility functions
│       ├── auth.py
│       ├── auth_deps.py
│       └── deps.py
│
├── database/                  # Database setup and management
│   ├── db_setup.py
│   ├── create_tables.py
│   └── seed.py
│
└── config/                    # Configuration files
    └── nlp_insights_config.json
```

## Key Features

1. **Resume Processing**: LangGraph + LangExtract integration for superior extraction
2. **AI Recommendations**: Job and course recommendations based on skills
3. **User Management**: Authentication and profile management
4. **Interactive UI**: Streamlit-based frontend
5. **RESTful API**: FastAPI backend with comprehensive endpoints

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI/ML**: LangGraph, Google LangExtract, Groq API, PyMuPDF
- **Frontend**: Streamlit
- **Authentication**: JWT tokens
- **Database**: SQLite with migrations

## API Endpoints

- `/auth/*` - Authentication (login, register)
- `/resume/*` - Resume processing and management
- `/jobs/*` - Job listings and recommendations
- `/courses/*` - Course listings and recommendations
- `/profile/*` - User profile management
- `/stats/*` - Analytics and statistics
