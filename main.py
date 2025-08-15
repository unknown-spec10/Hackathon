"""Hackathon API Main Application"""
from fastapi import FastAPI
from database.db_setup import Base, engine
from app.routes import auth_routes, course_routes, job_routes, profile_routes, stat_route, resume_routes

import logging
app = FastAPI(title="Hackathon API")

@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    logging.info("FastAPI startup event triggered.")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("FastAPI shutdown event triggered.")

app.include_router(auth_routes.router)
app.include_router(course_routes.router)
app.include_router(job_routes.router)
app.include_router(profile_routes.router)
app.include_router(stat_route.router)
app.include_router(resume_routes.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Hackathon API is running"}
