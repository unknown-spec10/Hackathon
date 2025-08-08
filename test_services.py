from datetime import date
from app.service import course_service, job_service, profile_service
from app.models.organization import Organization, OrgTypeEnum
from app.schemas.course_schema import CourseCreate, CourseMode
from app.schemas.job_schema import JobCreate, JobType


def test_course_service_flow(db_session):
    payload = CourseCreate(
        name="Course A", duration="4w", mode=CourseMode.ONLINE, fees="Free",
        description="desc", skills_required=["Python"], application_deadline=date(2025,1,1),
        prerequisites=["Basics"],
    )
    created = course_service.create_course(db_session, payload)
    listed = course_service.list_courses(db_session)
    assert any(c.id == created.id for c in listed)
    got = course_service.get_course(db_session, created.id)
    assert got.views >= 1


def test_job_service_flow(db_session):
    payload = JobCreate(
        title="Backend", job_type=JobType.FULL_TIME, location="Remote",
        salary_range="$1", responsibilities=None, skills_required=["Py"],
        application_deadline=date(2025,1,1), industry=None, remote_option=None,
        experience_level=None, contact_email=None, application_url=None,
        posted_date=None, updated_date=None, number_of_openings=1,
    )
    created = job_service.create_job(db_session, payload)
    listed = job_service.list_jobs(db_session)
    assert any(j.id == created.id for j in listed)
    got = job_service.get_job(db_session, created.id)
    assert got.views >= 1


def test_profile_service_flow(db_session):
    org = Organization(name="Org", org_type=OrgTypeEnum.COMPANY, address="addr", contact_email="c@e.com")
    db_session.add(org)
    db_session.commit()

    fetched = profile_service.get_org(db_session, org.id)
    assert fetched.id == org.id
