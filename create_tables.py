#!/usr/bin/env python3
"""
Database setup script to create all tables
"""

from database.db_setup import Base, engine
from app.models.user import User
from app.models.profile import Organization
from app.models.job import Job
from app.models.course import Course
from app.models.resume import Resume

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    create_tables()
