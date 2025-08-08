from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.organization_schema import OrgProfile
from app.service import profile_service
from app.utils.deps import get_db

router = APIRouter(prefix="/profile", tags=["Organization Profile"])

@router.get("/{org_id}")
def get_org_profile(org_id: int, db: Session = Depends(get_db)):
    return profile_service.get_org(db, org_id)

@router.put("/{org_id}")
def update_org_profile(org_id: int, profile: OrgProfile, db: Session = Depends(get_db)):
    return profile_service.update_org(db, org_id, profile)
