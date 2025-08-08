# 🚀 Hackathon API

A comprehensive FastAPI-based REST API for job and course management platform, built for hackathon projects.

## 📋 Features

- **Authentication**: JWT-based user authentication with bcrypt password hashing
- **User Management**: User registration, login, and profile management
- **Course Management**: Create, read, update, delete courses with skills tracking
- **Job Management**: Comprehensive job posting system with various job types
- **Organization Profiles**: Company and institution profile management
- **Statistics**: View tracking and analytics for jobs and courses
- **Modern UI**: Streamlit-based web interface for testing (Direct Function Calls)

## 🏗️ Architecture

- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Authentication**: JWT with bcrypt
- **UI**: Streamlit web interface (Direct Function Calls - No HTTP Server Required)
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

For development, the API uses SQLite by default. For production, set up PostgreSQL and update the `DATABASE_URL` in `app/core/settings.py`.

### 3. Start the Streamlit UI (Recommended)

```bash
python start_direct_ui.py
```

The UI will be available at: http://localhost:8501

**No API server required!** The UI uses direct function calls to test all functionality.

### 4. Start the API Server (Optional)

```bash
python start_server.py
```

The API will be available at:
- **API Root**: http://localhost:8000/
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user (requires authentication)

### Courses
- `GET /courses/` - List all courses
- `POST /courses/` - Create a new course
- `GET /courses/{id}` - Get specific course
- `PUT /courses/{id}` - Update course
- `DELETE /courses/{id}` - Delete course

### Jobs
- `GET /jobs/` - List all jobs
- `POST /jobs/` - Create a new job
- `GET /jobs/{id}` - Get specific job
- `PUT /jobs/{id}` - Update job
- `DELETE /jobs/{id}` - Delete job

### Organizations
- `GET /profile/{org_id}` - Get organization profile
- `PUT /profile/{org_id}` - Update organization profile

### Statistics
- `GET /stats/jobs/{job_id}` - Get job statistics
- `GET /stats/courses/{course_id}` - Get course statistics

## 🧪 Testing

### Test with Streamlit UI (Recommended)

```bash
python start_direct_ui.py
```

Then open http://localhost:8501 in your browser and use the interactive UI to test all functionality.

### Test the API Server

```bash
python test_server.py
```

### Test the API with HTTP Server

1. Start the API server: `python start_server.py`
2. Open http://localhost:8000/docs in your browser
3. Use the interactive API documentation

## 📁 Project Structure

```
├── app/
│   ├── core/          # Settings and configuration
│   ├── models/        # SQLAlchemy models
│   ├── repositories/  # Data access layer
│   ├── route/         # API endpoints
│   ├── schemas/       # Pydantic schemas
│   ├── service/       # Business logic
│   └── utils/         # Auth utilities
├── database/          # DB setup and seeding
├── tests/            # Test suite
├── streamlit_ui_direct.py   # Streamlit UI (Direct Functions)
├── start_direct_ui.py       # UI startup script
├── start_server.py   # API server startup
└── test_server.py    # API testing script
```

## 🔧 Development

### Database Models

- **User**: User accounts with email/password authentication
- **Organization**: Companies and institutions
- **Course**: Educational courses with skills and prerequisites
- **Job**: Job postings with comprehensive details

### Key Features

- **View Tracking**: Both jobs and courses track view counts
- **Skills Management**: JSON-based skills tracking
- **Authentication**: JWT token-based security
- **Validation**: Comprehensive Pydantic schema validation
- **Error Handling**: Proper HTTP status codes and error messages
- **Direct Function Testing**: Streamlit UI that bypasses HTTP server

## 🎯 Example Usage

### Using the Streamlit UI

1. Start the UI: `python start_direct_ui.py`
2. Open http://localhost:8501
3. Use the sidebar to navigate between different functions
4. Test all API functionality through the interactive interface

### Using the API Server

```bash
# Create a User
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "username": "testuser"
  }'

# Create a Course
curl -X POST "http://localhost:8000/courses/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Introduction to APIs",
    "duration": "4 weeks",
    "mode": "Online",
    "fees": "Free",
    "description": "Learn to build APIs with FastAPI",
    "skills_required": ["Python", "FastAPI"],
    "application_deadline": "2025-12-31",
    "prerequisites": ["Basics of Python"]
  }'

# Create a Job
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Backend Engineer",
    "job_type": "Full-time",
    "location": "Remote",
    "salary_range": "$80k-$120k",
    "skills_required": ["Python", "FastAPI", "SQL"],
    "application_deadline": "2025-11-30",
    "industry": "Software",
    "remote_option": "Remote",
    "experience_level": "Mid",
    "number_of_openings": 2
  }'
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hackathon_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
```

### Database Setup

For development, SQLite is used by default. For production:

1. Install PostgreSQL
2. Create a database
3. Update `DATABASE_URL` in settings
4. Run database migrations

## 📈 Statistics

The API tracks:
- **Views**: Number of times jobs/courses are viewed
- **Applications**: Job applications and course enrollments
- **Skills Matching**: Skills-based analytics
- **Education Matching**: Education level analytics

## 🔒 Security

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Pydantic schema validation
- **Error Handling**: Secure error responses

## 🎉 Success!

The Hackathon API is now fully functional with:

✅ **Streamlit UI**: Running on http://localhost:8501 (Direct Functions)  
✅ **API Server**: Available on http://localhost:8000 (Optional)  
✅ **Documentation**: Available at http://localhost:8000/docs  
✅ **Database**: SQLite for development  
✅ **Authentication**: JWT-based security  
✅ **Testing**: Comprehensive test suite  
✅ **No HTTP Server Required**: Direct function calls for testing  

**Recommended Workflow:**
1. Start the Streamlit UI: `python start_direct_ui.py`
2. Open http://localhost:8501
3. Test all functionality through the beautiful web interface
4. No need to start the API server for testing!

Happy coding! 🚀

