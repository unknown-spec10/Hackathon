#!/usr/bin/env python3
"""
Script to create sample users for testing authentication and permissions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import get_db, Base, engine
from app.models.user import User, UserTypeEnum
from app.models.profile import Organization, OrgTypeEnum
from app.utils.auth import get_password_hash
from sqlalchemy.orm import Session

def create_sample_users():
    """Create sample users for testing"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    try:
        # Check if sample users already exist
        existing_user = db.query(User).filter(User.email == "company@test.com").first()
        if existing_user:
            print("✅ Sample users already exist!")
            return
        
        # 1. Create sample organizations first
        
        # Company organization
        company_org = Organization(
            name="TechCorp Solutions",
            org_type=OrgTypeEnum.COMPANY,
            address="123 Business St, San Francisco, CA 94105",
            contact_email="company@test.com",
            contact_phone="+1-555-123-4567",
            logo_path="https://via.placeholder.com/150x150/0066cc/ffffff?text=TechCorp"
        )
        db.add(company_org)
        db.flush()  # Get ID without committing
        
        # Institution organization
        institution_org = Organization(
            name="Digital University",
            org_type=OrgTypeEnum.INSTITUTION,
            address="456 Education Ave, Boston, MA 02115",
            contact_email="institution@test.com",
            contact_phone="+1-555-987-6543",
            logo_path="https://via.placeholder.com/150x150/00aa00/ffffff?text=DigitalU"
        )
        db.add(institution_org)
        db.flush()  # Get ID without committing
        
        # 2. Create sample users
        
        # B2B Company user
        company_user = User(
            username="company_admin",
            email="company@test.com",
            password_hash=get_password_hash("password123"),
            user_type=UserTypeEnum.B2B,
            org_id=company_org.id
        )
        db.add(company_user)
        
        # B2B Institution user
        institution_user = User(
            username="institution_admin",
            email="institution@test.com",
            password_hash=get_password_hash("password123"),
            user_type=UserTypeEnum.B2B,
            org_id=institution_org.id
        )
        db.add(institution_user)
        
        # B2C Individual user
        individual_user = User(
            username="john_doe",
            email="user@test.com",
            password_hash=get_password_hash("password123"),
            user_type=UserTypeEnum.B2C,
            org_id=None  # No organization for B2C users
        )
        db.add(individual_user)
        
        # Admin user (B2B with special privileges)
        admin_user = User(
            username="admin",
            email="admin@test.com",
            password_hash=get_password_hash("password123"),
            user_type=UserTypeEnum.B2B,
            org_id=company_org.id  # Associate with company for now
        )
        db.add(admin_user)
        
        # Commit all changes
        db.commit()
        
        print("✅ Sample users created successfully!")
        print("\n📋 Created Users:")
        print("1. company@test.com (B2B Company - Can create jobs)")
        print("2. institution@test.com (B2B Institution - Can create courses)")
        print("3. user@test.com (B2C Individual - Browse only)")
        print("4. admin@test.com (Admin - Full access)")
        print("\n🔑 All passwords: password123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_users()
