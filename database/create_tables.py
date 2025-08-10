#!/usr/bin/env python3
"""
Database setup script to create all tables
"""

import sys
import os

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
