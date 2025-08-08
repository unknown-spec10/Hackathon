import enum
from sqlalchemy import Column, Integer, String, Date, Text, Enum, JSON
from app.schemas.job_schema import JobType, RemoteOption, ExperienceLevel
from database.db_setup import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    job_type = Column(Enum(JobType), nullable=False)
    location = Column(String, nullable=False)
    salary_range = Column(String, nullable=False)
    responsibilities = Column(Text, nullable=True)
    skills_required = Column(JSON, nullable=False)  # store list of skills as JSON
    application_deadline = Column(Date, nullable=False)
    industry = Column(String, nullable=True)
    remote_option = Column(Enum(RemoteOption), nullable=True)
    experience_level = Column(Enum(ExperienceLevel), nullable=True)
    contact_email = Column(String, nullable=True)
    application_url = Column(String, nullable=True)  # store URL as string
    posted_date = Column(Date, nullable=True)
    updated_date = Column(Date, nullable=True)
    number_of_openings = Column(Integer, nullable=False, default=1)
    views = Column(Integer, nullable=False, default=0)
