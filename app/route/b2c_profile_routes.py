from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.b2c_profile_schema import B2CProfileCreate, B2CProfileUpdate, B2CProfileResponse
from app.service import b2c_profile_service
from app.utils.deps import get_db
from app.utils.auth import oauth2_scheme, decode_access_token
from app.models.user import User

router = APIRouter(prefix="/b2c-profiles", tags=["B2C Profiles"])


@router.post("/", response_model=B2CProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(profile_data: B2CProfileCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Create a new B2C user profile (only for B2C users)"""
    # Verify user from token
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload["sub"])
    # Only allow users to create their own profile
    if user_id != profile_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create a profile for yourself"
        )
    
    return b2c_profile_service.create_profile(db, profile_data)


@router.get("/me", response_model=B2CProfileResponse)
def get_my_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user's B2C profile"""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload["sub"])
    return b2c_profile_service.get_profile(db, user_id)


@router.get("/{user_id}", response_model=B2CProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get a B2C profile by user ID (public endpoint)"""
    return b2c_profile_service.get_profile(db, user_id)


@router.put("/me", response_model=B2CProfileResponse)
def update_my_profile(profile_data: B2CProfileUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Update the current user's B2C profile"""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload["sub"])
    return b2c_profile_service.update_profile(db, user_id, profile_data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Delete the current user's B2C profile"""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload["sub"])
    b2c_profile_service.delete_profile(db, user_id)
    return None