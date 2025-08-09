from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.b2c_profile import B2CProfile
from app.schemas.b2c_profile_schema import B2CProfileCreate, B2CProfileUpdate


def create_b2c_profile(db: Session, profile_data: B2CProfileCreate):
    """Create a new B2C user profile"""
    try:
        profile = B2CProfile(**profile_data.dict())
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except IntegrityError:
        db.rollback()
        raise ValueError("Profile already exists for this user or user does not exist")


def get_profile_by_user_id(db: Session, user_id: int):
    """Get B2C profile by user ID"""
    return db.query(B2CProfile).filter(B2CProfile.user_id == user_id).first()


def get_profile_by_id(db: Session, profile_id: int):
    """Get B2C profile by profile ID"""
    return db.query(B2CProfile).filter(B2CProfile.id == profile_id).first()


def update_b2c_profile(db: Session, user_id: int, profile_data: B2CProfileUpdate):
    """Update B2C profile for a user"""
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        return None
    
    update_data = profile_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile


def delete_b2c_profile(db: Session, user_id: int):
    """Delete B2C profile for a user"""
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        return False
    
    db.delete(profile)
    db.commit()
    return True