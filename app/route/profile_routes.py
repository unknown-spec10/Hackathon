from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.profile_schema import OrgProfile
from app.repositories import organization_repo
from app.utils.deps import get_db

router = APIRouter(prefix="/profile", tags=["Organization Profile"])

@router.get("/{org_id}")
def get_org_profile(org_id: int, db: Session = Depends(get_db)):
    org = organization_repo.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/{org_id}")
def update_org_profile(org_id: int, profile: OrgProfile, db: Session = Depends(get_db)):
    updated = organization_repo.update_organization(db, org_id, profile)
    if not updated:
        raise HTTPException(status_code=404, detail="Organization not found")
    return updated
