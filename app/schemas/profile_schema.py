from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class OrgType(str, Enum):
    COMPANY = "Company"
    INSTITUTION = "Institution"


class OrgProfile(BaseModel):
    name: str = Field(..., min_length=2, description="Organization name")
    org_type: OrgType = Field(..., description="Organization type")
    address: str = Field(..., min_length=5, description="Organization address")
    contact_email: EmailStr = Field(..., description="Contact email")
    contact_phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Contact phone number")
    logo_path: Optional[str] = Field(None, description="Path or URL to the organization's logo")

    class Config:
        orm_mode = True


class OrgProfileUpdate(OrgProfile):
    id: int = Field(..., description="Organization profile ID")


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")

