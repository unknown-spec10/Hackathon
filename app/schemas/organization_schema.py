from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Optional
from enum import Enum


class OrgType(str, Enum):
    COMPANY = "Company"
    INSTITUTION = "Institution"


class OrgProfile(BaseModel):
    name: str = Field(..., min_length=2, description="Organization name", example="Tech Corp")
    org_type: OrgType = Field(..., description="Organization type", example=OrgType.COMPANY)
    address: str = Field(
        ..., pattern=r"^[A-Za-z0-9\s]+,\s*[A-Za-z\s]+,\s*[A-Za-z\s]+$", description="Organization address (e.g., '123 Main St, New York, USA')", example="123 Main St, New York, USA"
    )
    contact_email: EmailStr = Field(..., description="Contact email", example="contact@techcorp.com")
    contact_phone: Optional[str] = Field(None, pattern=r"^\+?\d[\d\s\-]{5,18}\d$", description="Contact phone number (e.g., '+1234567890')", example="+1234567890")
    logo_path: Optional[HttpUrl] = Field(None, description="URL to the organization's logo", example="https://techcorp.com/logo.png")

    @validator("name", "address")
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    class Config:
        from_attributes = True


class OrgProfileCreate(OrgProfile):
    pass


class OrgProfileUpdate(OrgProfile):
    id: int = Field(..., description="Organization profile ID", example=1)


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(
        ..., pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$", description="New password (must include letter, number, and special character)"
    )