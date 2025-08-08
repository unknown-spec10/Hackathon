from fastapi import FastAPI
from database.db_setup import Base, engine
from app.route import auth_routes, course_routes, job_routes, profile_routes, stat_route

app = FastAPI(title="Hackathon API")

# Create tables (for demo/dev) - commented out to avoid startup DB connection issues
# Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth_routes.router)
app.include_router(course_routes.router)
app.include_router(job_routes.router)
app.include_router(profile_routes.router)
app.include_router(stat_route.router)

@app.get("/")
def root():
	return {"status": "ok"}
