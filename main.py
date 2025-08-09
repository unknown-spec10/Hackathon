from fastapi import FastAPI
from database.db_setup import Base, engine
from app.route import auth_routes, course_routes, job_routes, profile_routes, stat_route, organization_routes

app = FastAPI(title="Hackathon API")

# Create tables (for demo/dev)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth_routes.router)
app.include_router(course_routes.router)
app.include_router(job_routes.router)
app.include_router(profile_routes.router)
app.include_router(stat_route.router)
app.include_router(organization_routes.router)

@app.get("/")
def root():
	return {"status": "ok"}
