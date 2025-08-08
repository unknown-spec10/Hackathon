from datetime import date
from app.repositories import course_repo, job_repo, profile_repo, user_repo
from app.models.course import CourseModeEnum
from app.models.job import JobTypeEnum
from app.models.organization import Organization, OrgTypeEnum


def test_user_repo_crud(db_session):
    # Create
    user = user_repo.create_user(db_session, username="test", password_hash="x", org_id=1)
    assert user.id is not None

    # Read
    got = user_repo.get_user_by_username(db_session, "test")
    assert got is not None
    assert got.username == "test"

    got_by_id = user_repo.get_user_by_id(db_session, user.id)
    assert got_by_id is not None
    assert got_by_id.username == "test"

    # Update
    updated = user_repo.update_user(db_session, user.id, type("Obj", (), {
        "dict": lambda self: {"username": "updated", "password_hash": "y", "org_id": 1}
    })())
    assert updated.username == "updated"

    # List/Get all
    all_users = user_repo.get_all_users(db_session)
    assert any(u.id == user.id for u in all_users)

    # Delete
    user_repo.delete_user(db_session, user.id)
    assert user_repo.get_user_by_id(db_session, user.id) is None


def test_profile_repo_crud(db_session):
    # Create Organization
    org = Organization(name="Org", org_type=OrgTypeEnum.COMPANY, address="addr", contact_email="c@e.com")
    db_session.add(org)
    db_session.commit()

    # Read
    got = profile_repo.get_organization_by_id(db_session, org.id)
    assert got is not None

    # Update
    updated = profile_repo.update_organization(db_session, org.id, type("Obj", (), {
        "dict": lambda self: {"name": "New Org", "org_type": OrgTypeEnum.COMPANY, "address": "a", "contact_email": "c@e.com", "contact_phone": None, "logo_path": None}
    })())
    assert updated.name == "New Org"

    # List/Get all
    all_orgs = profile_repo.get_all_organizations(db_session)
    assert any(o.id == org.id for o in all_orgs)

    # Delete
    profile_repo.delete_organization(db_session, org.id)
    assert profile_repo.get_organization_by_id(db_session, org.id) is None


def test_course_repo_crud(db_session):
    # Create
    payload = type("Obj", (), {"dict": lambda self: {
        "name": "Course A", "duration": "4w", "mode": CourseModeEnum.ONLINE,
        "fees": "Free", "description": "desc", "skills_required": ["Python"],
        "application_deadline": date(2025,1,1), "prerequisites": ["Basics"]
    }})()
    created = course_repo.create_course(db_session, payload)
    assert created.id is not None

    # Read
    got = course_repo.get_course_by_id(db_session, created.id)
    assert got.name == "Course A"

    # Update
    updated = course_repo.update_course(db_session, created.id, type("Obj", (), {
        "dict": lambda self: {
            "name": "Course B", "duration": "5w", "mode": CourseModeEnum.OFFLINE,
            "fees": "Paid", "description": "desc2", "skills_required": ["Python", "SQL"],
            "application_deadline": date(2025,2,1), "prerequisites": ["Basics", "Advanced"]
        }
    })())
    assert updated.name == "Course B"

    # List/Get all
    all_courses = course_repo.get_all_courses(db_session)
    assert any(c.id == created.id for c in all_courses)

    # Delete
    course_repo.delete_course(db_session, created.id)
    assert course_repo.get_course_by_id(db_session, created.id) is None


def test_job_repo_crud(db_session):
    # Create
    payload = type("Obj", (), {"dict": lambda self: {
        "title": "Backend", "job_type": JobTypeEnum.FULL_TIME, "location": "Remote",
        "salary_range": "$1", "responsibilities": None, "skills_required": ["Py"],
        "application_deadline": date(2025,1,1), "industry": None, "remote_option": None,
        "experience_level": None, "contact_email": None, "application_url": None,
        "posted_date": None, "updated_date": None, "number_of_openings": 1
    }})()
    created = job_repo.create_job(db_session, payload)
    assert created.id is not None

    # Read
    got = job_repo.get_job_by_id(db_session, created.id)
    assert got.title == "Backend"

    # Update
    updated = job_repo.update_job(db_session, created.id, type("Obj", (), {
        "dict": lambda self: {
            "title": "Frontend", "job_type": JobTypeEnum.PART_TIME, "location": "Onsite",
            "salary_range": "$2", "responsibilities": "Dev", "skills_required": ["JS"],
            "application_deadline": date(2025,2,1), "industry": "IT", "remote_option": False,
            "experience_level": "Junior", "contact_email": "hr@e.com", "application_url": "url",
            "posted_date": date(2024,6,1), "updated_date": date(2024,6,2), "number_of_openings": 2
        }
    })())
    assert updated.title == "Frontend"

    # List/Get all
    all_jobs = job_repo.get_all_jobs(db_session)
    assert any(j.id == created.id for j in all_jobs)

    # Delete
    job_repo.delete_job(db_session, created.id)
    assert job_repo.get_job_by_id(db_session, created.id) is None
