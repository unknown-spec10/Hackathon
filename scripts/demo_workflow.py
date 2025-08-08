"""
End-to-end demo workflow using FastAPI TestClient.
"""
import os
import sys

# Ensure project root on sys.path so 'app' and 'database' resolve when running this script directly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Force a local SQLite file DB for the demo so it doesn't require Postgres
demo_db_path = os.path.join(ROOT, "demo_workflow.db")
if os.path.exists(demo_db_path):
    try:
        os.remove(demo_db_path)
        print("[SETUP] Removed existing demo DB at:", demo_db_path)
    except OSError:
        pass
db_url = f"sqlite:///{demo_db_path.replace('\\', '/')}"
os.environ["DATABASE_URL"] = db_url

from fastapi.testclient import TestClient
from main import app

print("[SETUP] Using DATABASE_URL=", os.environ.get("DATABASE_URL"))

client = TestClient(app)


def print_step(title):
    print("\n=====", title, "=====")


def assert_ok(response, context=""):
    if not (200 <= response.status_code < 400):
        print(f"[ERROR] {context} -> {response.status_code}: {response.text}")
    # Will raise HTTPError if status >= 400
    response.raise_for_status()


# 1) Signup
print_step("Signup new user")
# unique email to avoid collisions on repeated runs
from datetime import datetime
unique_email = f"demo+{datetime.utcnow().strftime('%Y%m%d%H%M%S')}@example.com"
signup_payload = {
    "email": unique_email,
    "password": "secret123",
    "username": "demo",
}
r = client.post("/auth/signup", json=signup_payload)
assert_ok(r, "signup")
user = r.json()
print("[SIGNUP] User created:", user)

# 2) Login
print_step("Login with user credentials")
login_form = {"username": signup_payload["email"], "password": signup_payload["password"]}
r = client.post("/auth/login", data=login_form)
assert_ok(r, "login")
token = r.json()["access_token"]
print("[LOGIN] Access token:", token[:30] + "..." if token else None)

headers = {"Authorization": f"Bearer {token}"}

# 3) Who am I
print_step("Get current user")
r = client.get("/auth/me", headers=headers)
assert_ok(r, "me")
print("[ME]", r.json())

# 4) Create a course
print_step("Create course")
course_payload = {
    "name": "Intro to APIs",
    "duration": "4 weeks",
    "mode": "Online",
    "fees": "Free",
    "description": "Learn to build APIs",
    "skills_required": ["Python"],
    "application_deadline": "2025-12-31",
    "prerequisites": ["Basics of Python"],
}
r = client.post("/courses/", json=course_payload)
assert_ok(r, "create course")
course = r.json()
print("[COURSE] Created:", course)

# 5) Get all courses
print_step("List courses")
r = client.get("/courses/")
assert_ok(r, "list courses")
print("[COURSE] List:", r.json())

# 6) Get one course (increments views)
print_step("Get course by id")
r = client.get(f"/courses/{course['id']}")
assert_ok(r, "get course")
print("[COURSE] Details:", r.json())

# 7) Create a job
print_step("Create job")
job_payload = {
    "title": "Backend Engineer",
    "job_type": "Full-time",
    "location": "Remote",
    "salary_range": "$80k-$120k",
    "responsibilities": "Build APIs",
    "skills_required": ["Python", "FastAPI", "SQL"],
    "application_deadline": "2025-11-30",
    "industry": "Software",
    "remote_option": "Remote",
    "experience_level": "Mid",
    "number_of_openings": 2
}
r = client.post("/jobs/", json=job_payload)
assert_ok(r, "create job")
job = r.json()
print("[JOB] Created:", job)

# 8) List jobs
print_step("List jobs")
r = client.get("/jobs/")
assert_ok(r, "list jobs")
print("[JOB] List:", r.json())

# 9) Get job by id (increments views)
print_step("Get job by id")
r = client.get(f"/jobs/{job['id']}")
assert_ok(r, "get job")
print("[JOB] Details:", r.json())

print("\n[COMPLETE] Demo workflow finished successfully.")
