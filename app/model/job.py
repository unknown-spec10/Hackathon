from sqlalchemy import Column, Integer, String, Date, Text
from database.db_setup import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    job_type = Column(String)
    location = Column(String)
    salary_range = Column(String)
    responsibilities = Column(Text)
    skills_required = Column(Text)  # comma-separated
    application_deadline = Column(Date)
    visibility = Column(String, default="public")
