from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.b2c_profile_schema import B2CProfileCreate, B2CProfileUpdate
from app.repositories import b2c_profile_repo
from app.models.user import User
from app.schemas.user_schema import UserType


def create_profile(db: Session, profile_data: B2CProfileCreate):
    """Create a new B2C user profile"""
    # Verify user exists and is a B2C user
    user = db.query(User).filter(User.id == profile_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.user_type != UserType.B2C:
        raise HTTPException(status_code=400, detail="Profile can only be created for B2C users")
    
    # Check if profile already exists
    existing_profile = b2c_profile_repo.get_profile_by_user_id(db, profile_data.user_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")
    
    try:
        return b2c_profile_repo.create_b2c_profile(db, profile_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_profile(db: Session, user_id: int):
    """Get B2C profile by user ID"""
    profile = b2c_profile_repo.get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def update_profile(db: Session, user_id: int, profile_data: B2CProfileUpdate):
    """Update B2C profile for a user"""
    # Verify user exists and is a B2C user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.user_type != UserType.B2C:
        raise HTTPException(status_code=400, detail="Only B2C user profiles can be updated")
    
    updated_profile = b2c_profile_repo.update_b2c_profile(db, user_id, profile_data)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated_profile


def delete_profile(db: Session, user_id: int):
    """Delete B2C profile for a user"""
    result = b2c_profile_repo.delete_b2c_profile(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted successfully"}