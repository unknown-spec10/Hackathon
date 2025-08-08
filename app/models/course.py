from sqlalchemy import Column, Integer, String, Date, Text, Enum, Numeric, event, CheckConstraint, JSON
from sqlalchemy.orm import validates
from database.db_setup import Base
from schemas.course_schema import CourseMode as CourseModeEnum 
from datetime import date


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, comment="Unique course identifier")
    name = Column(String(100), nullable=False, index=True, comment="Course name")
    duration = Column(String(50), nullable=False, comment="Course duration (e.g., '3 months')")
    mode = Column(Enum(CourseModeEnum), nullable=False, comment="Course mode: Online / Offline / Hybrid")
    fees = Column(Numeric(10, 2), nullable=True, comment="Course fees (optional)")
    description = Column(Text, nullable=False, comment="Course description")
    skills_required = Column(JSON, nullable=False, comment="List of required skills")
    application_deadline = Column(Date, nullable=False, index=True, comment="Application deadline")
    prerequisites = Column(JSON, nullable=False, comment="List of prerequisite courses")
    # Removed views (moved to CourseStats)

    __table_args__ = (
        CheckConstraint("json_array_length(skills_required) > 0", name="non_empty_skills"),
        CheckConstraint("json_array_length(prerequisites) > 0", name="non_empty_prerequisites"),
    )

    @validates("skills_required", "prerequisites")
    def validate_json(self, key, value):
        if not isinstance(value, list) or not value:
            raise ValueError(f"{key} must be a non-empty list")
        return value

    @validates("application_deadline")
    def validate_deadline(self, key, value):
        if value < date.today():
            raise ValueError("Application deadline must be in the future")
        return value