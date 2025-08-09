from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.organization_schema import OrgProfile, OrgProfileCreate, OrgProfileUpdate
from app.repositories import profile_repo
from app.utils.deps import get_db
from app.utils.auth import oauth2_scheme, decode_access_token
from app.models.user import User

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("/", response_model=OrgProfile, status_code=status.HTTP_201_CREATED)
def create_organization(org_data: OrgProfileCreate, db: Session = Depends(get_db)):
    """Create a new organization (for B2B users)"""
    return profile_repo.create_organization(db, org_data)


@router.get("/{org_id}", response_model=OrgProfile)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    """Get organization details by ID"""
    org = profile_repo.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.put("/{org_id}", response_model=OrgProfile)
def update_organization(
    org_id: int, org_data: OrgProfileUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Update organization details (restricted to users of that organization)"""
    # Verify user belongs to this organization
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to update this organization"
        )
    
    updated_org = profile_repo.update_organization(db, org_id, org_data)
    if not updated_org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return updated_org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Delete an organization (admin only)"""
    # This would typically be restricted to admin users
    # For now, we'll just check if the user belongs to this organization
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You don't have permission to delete this organization"
        )
    
    result = profile_repo.delete_organization(db, org_id)
    if not result:
        raise HTTPException(status_code=404, detail="Organization not found")
    return None