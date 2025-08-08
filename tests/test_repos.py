from datetime import date
from app.repositories import course_repo, job_repo, profile_repo, user_repo
from app.models.course import CourseModeEnum
from app.models.job import JobTypeEnum
from app.models.profile import Organization, OrgTypeEnum


def test_user_repo_crud(db_session):
    user = user_repo.create_user(db_session, username="test", password_hash="x", org_id=1)
    got = user_repo.get_user_by_username(db_session, "test")
    assert got is not None
    assert got.username == "test"


def test_profile_repo_crud(db_session):
    org = Organization(name="Org", org_type=OrgTypeEnum.COMPANY, address="addr", contact_email="c@e.com")
    db_session.add(org)
    db_session.commit()

    got = profile_repo.get_organization_by_id(db_session, org.id)
    assert got is not None

    updated = profile_repo.update_organization(db_session, org.id, type("Obj", (), {
        "dict": lambda self: {"name": "New Org", "org_type": OrgTypeEnum.COMPANY, "address": "a", "contact_email": "c@e.com", "contact_phone": None, "logo_path": None}
    })())
    assert updated.name == "New Org"


def test_course_repo_crud(db_session):
    payload = type("Obj", (), {"dict": lambda self: {
        "name": "Course A", "duration": "4w", "mode": CourseModeEnum.ONLINE,
        "fees": "Free", "description": "desc", "skills_required": ["Python"],
        "application_deadline": date(2025,1,1), "prerequisites": ["Basics"]
    }})()
    created = course_repo.create_course(db_session, payload)
    assert created.id is not None
    got = course_repo.get_course_by_id(db_session, created.id)
    assert got.name == "Course A"


def test_job_repo_crud(db_session):
    payload = type("Obj", (), {"dict": lambda self: {
        "title": "Backend", "job_type": JobTypeEnum.FULL_TIME, "location": "Remote",
        "salary_range": "$1", "responsibilities": None, "skills_required": ["Py"],
        "application_deadline": date(2025,1,1), "industry": None, "remote_option": None,
        "experience_level": None, "contact_email": None, "application_url": None,
        "posted_date": None, "updated_date": None, "number_of_openings": 1
    }})()
    created = job_repo.create_job(db_session, payload)
    assert created.id is not None
    got = job_repo.get_job_by_id(db_session, created.id)
    assert got.title == "Backend"
