from sqlalchemy.orm import Session
from app.models.profile import Organization
from app.schemas.profile_schema import OrgProfile
from app.utils.deps import get_db

class ProfileRepository:
    def __init__(self):
        self.db = next(get_db())
    
    def get_profile_by_id(self, org_id: int):
        """Get organization profile by ID"""
        return self.db.query(Organization).filter(Organization.id == org_id).first()
    
    def update_profile(self, org_id: int, profile_data: dict):
        """Update organization profile"""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if org:
            for key, value in profile_data.items():
                setattr(org, key, value)
            self.db.commit()
            self.db.refresh(org)
            return org
        return None

# Legacy functions for backward compatibility
def create_organization(db: Session, org_data: OrgProfile):
    org = Organization(**org_data.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def get_organization_by_id(db: Session, org_id: int):
    return db.query(Organization).filter(Organization.id == org_id).first()

def update_organization(db: Session, org_id: int, org_data: OrgProfile):
    org = get_organization_by_id(db, org_id)
    if not org:
        return None
    for key, value in org_data.dict().items():
        setattr(org, key, value)
    db.commit()
    db.refresh(org)
    return org
def delete_organization(db: Session, org_id: int):
    org = get_organization_by_id(db, org_id)
    if org:
        db.delete(org)
        db.commit()
        return True
    return False
