import enum
from sqlalchemy import Column, Integer, String, Enum, Text
from sqlalchemy.orm import relationship
from database.db_setup import Base


class UserTypeEnum(enum.Enum):
    B2B = "B2B"  # Organization users (can post jobs/courses)
    B2C = "B2C"  # Talent users (search for jobs)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)  
    org_id = Column(Integer)  
    email = Column(String, unique=True, nullable=False)
    user_type = Column(Enum(UserTypeEnum), nullable=False, default=UserTypeEnum.B2C)
    
    # B2C Personal details
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # JSON string of skills array
    experience_years = Column(Integer, default=0)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="user", lazy="dynamic")