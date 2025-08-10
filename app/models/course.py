from sqlalchemy import Column, Integer, String, Date, Text, Enum, JSON
from database.db_setup import Base
from app.schemas.course_schema import CourseMode


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=True)  # Added provider field
    duration = Column(String, nullable=False)
    mode = Column(Enum(CourseMode), nullable=False)
    fees = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    skills_required = Column(JSON, nullable=False)  
    application_deadline = Column(Date, nullable=False)
    prerequisites = Column(JSON, nullable=False)
    views = Column(Integer, nullable=False, default=0)