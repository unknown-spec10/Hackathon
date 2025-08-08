from pydantic import BaseModel, EmailStr
from typing import Optional

class OrgProfile(BaseModel):
    name: str
    org_type: str
    address: str
    contact_email: EmailStr
    contact_phone: str
    logo_path: Optional[str]

class OrgProfileUpdate(OrgProfile):
    id: int

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
