from sqlalchemy import Column, Integer, String, Date, Text
from database.db_setup import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration = Column(String)
    mode = Column(String)
    fees = Column(String)
    description = Column(Text)
    skills_required = Column(Text)  # comma-separated
    application_deadline = Column(Date)
    visibility = Column(String, default="public")
