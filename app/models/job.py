import enum
from sqlalchemy import Column, Integer, String, Date, Text, Enum, JSON
from database.db_setup import Base


class JobTypeEnum(enum.Enum):
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"
    PART_TIME = "Part-time"


class RemoteOptionEnum(enum.Enum):
    REMOTE = "Remote"
    ONSITE = "On-site"
    HYBRID = "Hybrid"


class ExperienceLevelEnum(enum.Enum):
    ENTRY = "Entry"
    MID = "Mid"
    SENIOR = "Senior"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    job_type = Column(Enum(JobTypeEnum), nullable=False)
    location = Column(String, nullable=False)
    salary_range = Column(String, nullable=False)
    responsibilities = Column(Text, nullable=True)
    skills_required = Column(JSON, nullable=False)  # store list of skills as JSON
    application_deadline = Column(Date, nullable=False)
    industry = Column(String, nullable=True)
    remote_option = Column(Enum(RemoteOptionEnum), nullable=True)
    experience_level = Column(Enum(ExperienceLevelEnum), nullable=True)
    contact_email = Column(String, nullable=True)
    application_url = Column(String, nullable=True)  # store URL as string
    posted_date = Column(Date, nullable=True)
    updated_date = Column(Date, nullable=True)
    number_of_openings = Column(Integer, nullable=False, default=1)
    views = Column(Integer, nullable=False, default=0)
