import os
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app

# Setup demo DB path and env
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
demo_db_path = os.path.join(ROOT, "demo_workflow.db")

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Remove existing DB before tests
    if os.path.exists(demo_db_path):
        try:
            os.remove(demo_db_path)
            print("[SETUP] Removed existing demo DB at:", demo_db_path)
        except OSError as e:
            print("[SETUP] Error removing demo DB:", e)
    os.environ["DATABASE_URL"] = f"sqlite:///{demo_db_path.replace('\\', '/')}"
    yield
    # Optionally clean up after tests if needed


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def signup_user(client):
    email = f"demo+{datetime.utcnow().strftime('%Y%m%d%H%M%S')}@example.com"
    payload = {"email": email, "password": "secret123", "full_name": "Demo User", "user_type": "B2C"}
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201, f"Signup failed: {response.text}"
    user = response.json()
    return user, payload


def login_user(client, email, password):
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json().get("access_token")
    assert token, "No access token returned"
    return token


def test_full_workflow(client):
    # Signup
    user, creds = signup_user(client)

    # Login
    token = login_user(client, creds["email"], creds["password"])
    headers = {"Authorization": f"Bearer {token}"}

    # Get current user (/me)
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200, f"/me failed: {r.text}"
    user_info = r.json()
    assert user_info["email"] == creds["email"]

    # Course CRUD
    course_payload = {
        "name": "Intro to APIs",
        "duration": "4 weeks",
        "mode": "Online",
        "fees": "Free",
        "description": "Learn to build APIs",
        "skills_required": ["Python"],
        "application_deadline": "2025-12-31"
    }

    # Create
    r = client.post("/courses/", json=course_payload, headers=headers)
    assert r.status_code == 200, f"Create course failed: {r.text}"
    course = r.json()
    course_id = course["id"]

    # Read all
    r = client.get("/courses/", headers=headers)
    assert r.status_code == 200
    courses = r.json()
    assert any(c["id"] == course_id for c in courses)

    # Read one
    r = client.get(f"/courses/{course_id}", headers=headers)
    assert r.status_code == 200

    # Update
    updated_payload = course_payload.copy()
    updated_payload.update({"name": "Intro to APIs - Updated", "duration": "5 weeks", "mode": "Offline", "fees": "Paid"})
    r = client.put(f"/courses/{course_id}", json=updated_payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Intro to APIs - Updated"

    # Delete
    r = client.delete(f"/courses/{course_id}", headers=headers)
    assert r.status_code == 200

    # Confirm delete
    r = client.get(f"/courses/{course_id}", headers=headers)
    assert r.status_code == 404

    # Job CRUD (similar steps)
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

    # Create job
    r = client.post("/jobs/", json=job_payload, headers=headers)
    assert r.status_code == 200
    job = r.json()
    job_id = job["id"]

    # Read all jobs
    r = client.get("/jobs/", headers=headers)
    assert r.status_code == 200
    jobs = r.json()
    assert any(j["id"] == job_id for j in jobs)

    # Read job by id
    r = client.get(f"/jobs/{job_id}", headers=headers)
    assert r.status_code == 200

    # Update job
    updated_job = job_payload.copy()
    updated_job.update({"title": "Backend Engineer - Updated", "job_type": "Part-time", "location": "Onsite", "salary_range": "$100k-$140k"})
    r = client.put(f"/jobs/{job_id}", json=updated_job, headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "Backend Engineer - Updated"

    # Delete job
    r = client.delete(f"/jobs/{job_id}", headers=headers)
    assert r.status_code == 200

    # Confirm job delete
    r = client.get(f"/jobs/{job_id}", headers=headers)
    assert r.status_code == 404
