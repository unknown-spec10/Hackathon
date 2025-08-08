from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.profile_schema import OrgProfile
from app.repositories import profile_repo


def get_org(db: Session, org_id: int):
    org = profile_repo.get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


def update_org(db: Session, org_id: int, payload: OrgProfile):
    updated = profile_repo.update_organization(db, org_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Organization not found")
    return updated
