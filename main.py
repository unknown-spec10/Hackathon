"""
Hackathon API Main Application
FastAPI backend with user management, resume processing, and AI recommendations.
"""
from fastapi import FastAPI
from database.db_setup import Base, engine
from app.routes import auth_routes, course_routes, job_routes, profile_routes, stat_route, resume_routes

app = FastAPI(title="Hackathon API")

# Database tables creation (handled by setup scripts)
# Base.metadata.create_all(bind=engine)

# API route registration
app.include_router(auth_routes.router)
app.include_router(course_routes.router)
app.include_router(job_routes.router)
app.include_router(profile_routes.router)
app.include_router(stat_route.router)
app.include_router(resume_routes.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Hackathon API is running"}
