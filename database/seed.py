from sqlalchemy.orm import Session
from database.db_setup import SessionLocal, Base, engine
from app.models.user import User
from app.models.job import Job, JobTypeEnum, RemoteOptionEnum, ExperienceLevelEnum
from app.models.course import Course, CourseModeEnum
from app.models.organization import Organization, OrgTypeEnum
from datetime import date


def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Organizations
        org1 = Organization(name="Acme Corp", org_type=OrgTypeEnum.COMPANY, address="123 Main St", contact_email="hr@acme.com")
        org2 = Organization(name="Tech Institute", org_type=OrgTypeEnum.INSTITUTION, address="456 Campus Rd", contact_email="info@tech.edu")
        db.add_all([org1, org2])
        db.flush()

        # Users
        u1 = User(username="alice", email="alice@acme.com", org_id=org1.id, password_hash="dev")
        u2 = User(username="bob", email="bob@tech.edu", org_id=org2.id, password_hash="dev")
        db.add_all([u1, u2])

        # Jobs
        j1 = Job(
            title="Backend Engineer",
            job_type=JobTypeEnum.FULL_TIME,
            location="Remote",
            salary_range="$80k-$120k",
            responsibilities="Build APIs",
            skills_required=["Python", "FastAPI", "SQL"],
            application_deadline=date(2025, 12, 31),
            industry="Software",
            remote_option=RemoteOptionEnum.REMOTE,
            experience_level=ExperienceLevelEnum.MID,
            number_of_openings=2,
        )
        j2 = Job(
            title="Data Intern",
            job_type=JobTypeEnum.INTERNSHIP,
            location="NYC",
            salary_range="$20/hr",
            responsibilities="Support analytics",
            skills_required=["Python", "Pandas"],
            application_deadline=date(2025, 9, 30),
            industry="Analytics",
            remote_option=RemoteOptionEnum.HYBRID,
            experience_level=ExperienceLevelEnum.ENTRY,
            number_of_openings=1,
        )
        db.add_all([j1, j2])

        # Courses
        c1 = Course(
            name="Intro to APIs",
            duration="4 weeks",
            mode=CourseModeEnum.ONLINE,
            fees="Free",
            description="Learn to build APIs",
            skills_required=["Python"],
            application_deadline=date(2025, 8, 31),
            prerequisites=["Basics of Python"],
        )
        c2 = Course(
            name="Data Science Bootcamp",
            duration="12 weeks",
            mode=CourseModeEnum.HYBRID,
            fees="$999",
            description="End-to-end DS",
            skills_required=["Python", "Statistics"],
            application_deadline=date(2025, 10, 15),
            prerequisites=["Algebra"],
        )
        db.add_all([c1, c2])

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
