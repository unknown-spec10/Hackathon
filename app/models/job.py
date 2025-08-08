from sqlalchemy import Column, Integer, String, Date, Text, Enum, JSON, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import validates
from database.db_setup import Base
from schemas.job_schema import JobType, RemoteOption, ExperienceLevel
from datetime import date


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, comment="Unique job identifier")
    title = Column(String(100), nullable=False, index=True, comment="Job title")
    job_type = Column(Enum(JobType), nullable=False, comment="Job type (Full-time / Internship / etc.)")
    location = Column(String(100), nullable=False, index=True, comment="Job location")
    salary_min = Column(Numeric(10, 2), nullable=False, comment="Minimum salary")
    salary_max = Column(Numeric(10, 2), nullable=False, comment="Maximum salary")
    responsibilities = Column(JSON, nullable=True, comment="List of job responsibilities")
    skills_required = Column(JSON, nullable=False, comment="List of required skills")
    application_deadline = Column(Date, nullable=False, index=True, comment="Application deadline")
    industry = Column(String(50), nullable=True, comment="Industry sector")
    remote_option = Column(Enum(RemoteOption), nullable=True, comment="Remote work option")
    experience_level = Column(Enum(ExperienceLevel), nullable=True, comment="Experience level required")
    contact_email = Column(String(100), nullable=True, comment="Contact email")
    application_url = Column(String(200), nullable=True, comment="Application URL")
    posted_date = Column(Date, nullable=False, default=date.today, comment="Date job was posted")
    updated_date = Column(Date, nullable=True, comment="Date job was last updated")
    number_of_openings = Column(Integer, nullable=False, default=1, comment="Number of openings")

    __table_args__ = (
        CheckConstraint("json_array_length(skills_required) > 0", name="non_empty_skills"),
    )

    @validates("skills_required")
    def validate_skills(self, key, value):
        if not isinstance(value, list) or not value:
            raise ValueError("skills_required must be a non-empty list")
        return value

    @validates("responsibilities")
    def validate_responsibilities(self, key, value):
        if value is not None and not isinstance(value, list):
            raise ValueError("responsibilities must be a list")
        return value

    @validates("application_deadline")
    def validate_deadline(self, key, value):
        if value < date.today():
            raise ValueError("Application deadline must be in the future")
        return value

    @validates("contact_email")
    def validate_email(self, key, value):
        if value:
            import re
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                raise ValueError("Invalid email format")
        return value

    @validates("application_url")
    def validate_url(self, key, value):
        if value:
            from urllib.parse import urlparse
            parsed = urlparse(value)
            if not all([parsed.scheme, parsed.netloc]) or parsed.scheme not in ("http", "https"):
                raise ValueError("Invalid URL format")
        return value