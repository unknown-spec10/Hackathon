from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.profile_schema import ProfileResponse, ProfileUpdate
from app.utils.auth_deps import get_current_user
from app.repositories.profile_repo import ProfileRepository

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/{org_id}", response_model=ProfileResponse)
async def get_profile(org_id: int):
    """Get organization profile"""
    profile_repo = ProfileRepository()
    profile = profile_repo.get_profile_by_id(org_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return ProfileResponse.from_orm(profile)

@router.put("/{org_id}", response_model=ProfileResponse)
async def update_profile(org_id: int, profile: ProfileUpdate, current_user = Depends(get_current_user)):
    """Update organization profile"""
    profile_repo = ProfileRepository()
    updated_profile = profile_repo.update_profile(org_id, profile.dict(exclude_unset=True))
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return ProfileResponse.from_orm(updated_profile)
