import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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

client = TestClient(app)
print("[SETUP] Using DATABASE_URL=", os.environ.get("DATABASE_URL"))


def print_step(title):
    print(f"\n===== {title} =====")


def assert_ok(response, context=""):
    if not (200 <= response.status_code < 400):
        print(f"[ERROR] {context} -> {response.status_code}: {response.text}")
    response.raise_for_status()


def signup_user():
    print_step("Signup new user")
    email = f"demo+{datetime.utcnow().strftime('%Y%m%d%H%M%S')}@example.com"
    payload = {"email": email, "password": "secret123", "username": "demo"}
    r = client.post("/auth/signup", json=payload)
    assert_ok(r, "signup")
    user = r.json()
    print("[SIGNUP]", user)
    return user, payload


def login_user(email, password):
    print_step("Login")
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert_ok(r, "login")
    token = r.json()["access_token"]
    print("[LOGIN] Token:", token[:30] + "..." if token else None)
    return token


def get_me(headers):
    print_step("Get current user")
    r = client.get("/auth/me", headers=headers)
    assert_ok(r, "me")
    print("[ME]", r.json())


def course_crud(headers):
    print_step("Create course")
    payload = {
        "name": "Intro to APIs",
        "duration": "4 weeks",
        "mode": "Online",  # <-- fix here
        "fees": "Free",
        "description": "Learn to build APIs",
        "skills_required": ["Python"],
        "application_deadline": "2025-12-31",
        "prerequisites": ["Basics of Python"],
    }
    r = client.post("/courses/", json=payload)
    assert_ok(r, "create course")
    course = r.json()
    print("[COURSE] Created:", course)

    print_step("List courses")
    r = client.get("/courses/")
    assert_ok(r, "list courses")
    print("[COURSE] List:", r.json())

    print_step("Get course by id")
    r = client.get(f"/courses/{course['id']}")
    assert_ok(r, "get course")
    print("[COURSE] Details:", r.json())

    print_step("Update course")
    update_payload = payload.copy()
    update_payload.update(
        {
            "name": "Intro to APIs - Updated",
            "duration": "5 weeks",
            "mode": "Offline",  # <-- fix here
            "fees": "Paid",
        }
    )
    r = client.put(f"/courses/{course['id']}", json=update_payload)
    assert_ok(r, "update course")
    print("[COURSE] Updated:", r.json())

    print_step("Delete course")
    r = client.delete(f"/courses/{course['id']}")
    assert_ok(r, "delete course")
    print("[COURSE] Deleted:", r.json())

    print_step("List courses after deletion")
    r = client.get("/courses/")
    assert_ok(r, "list courses after deletion")
    print("[COURSE] List after deletion:", r.json())

    print_step("Get deleted course (should fail)")
    r = client.get(f"/courses/{course['id']}")
    if r.status_code == 404:
        print("[COURSE] Not found as expected.")
    else:
        assert_ok(r, "get deleted course")


def job_crud(headers):
    print_step("Create job")
    payload = {
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
        "number_of_openings": 2,
    }
    r = client.post("/jobs/", json=payload)
    assert_ok(r, "create job")
    job = r.json()
    print("[JOB] Created:", job)

    print_step("List jobs")
    r = client.get("/jobs/")
    assert_ok(r, "list jobs")
    print("[JOB] List:", r.json())

    print_step("Get job by id")
    r = client.get(f"/jobs/{job['id']}")
    assert_ok(r, "get job")
    print("[JOB] Details:", r.json())

    print_step("Update job")
    update_payload = payload.copy()
    update_payload.update(
        {
            "title": "Backend Engineer - Updated",
            "job_type": "Part-time",
            "location": "Onsite",
            "salary_range": "$100k-$140k",
        }
    )
    r = client.put(f"/jobs/{job['id']}", json=update_payload)
    assert_ok(r, "update job")
    print("[JOB] Updated:", r.json())

    print_step("Delete job")
    r = client.delete(f"/jobs/{job['id']}")
    assert_ok(r, "delete job")
    print("[JOB] Deleted:", r.json())

    print_step("List jobs after deletion")
    r = client.get("/jobs/")
    assert_ok(r, "list jobs after deletion")
    print("[JOB] List after deletion:", r.json())

    print_step("Get deleted job (should fail)")
    r = client.get(f"/jobs/{job['id']}")
    if r.status_code == 404:
        print("[JOB] Not found as expected.")
    else:
        assert_ok(r, "get deleted job")


def main():
    user, creds = signup_user()
    token = login_user(creds["email"], creds["password"])
    headers = {"Authorization": f"Bearer {token}"}
    get_me(headers)
    course_crud(headers)
    job_crud(headers)
    print("\n[COMPLETE] Demo workflow finished successfully.")


if __name__ == "__main__":
    main()
print_step("Get deleted course (should fail)")
r = client.get(f"/courses/{course['id']}")
if r.status_code == 404:
    print("[COURSE] Not found as expected.")
else:
    assert_ok(r, "get deleted course")

# 17) Try to get deleted job (should fail)
print_step("Get deleted job (should fail)")
r = client.get(f"/jobs/{job['id']}")
if r.status_code == 404:
    print("[JOB] Not found as expected.")
else:
    assert_ok(r, "get deleted job")

print("\n[COMPLETE] Demo workflow finished successfully.")
