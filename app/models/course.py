from sqlalchemy import Column, Integer, String, Date, Text, Enum
from sqlalchemy.dialects.postgresql import JSON
from database.db_setup import Base
import enum


class CourseModeEnum(enum.Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    HYBRID = "Hybrid"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    mode = Column(Enum(CourseModeEnum), nullable=False)
    fees = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    skills_required = Column(JSON, nullable=False)  
    application_deadline = Column(Date, nullable=False)
    prerequisites = Column(JSON, nullable=False)  