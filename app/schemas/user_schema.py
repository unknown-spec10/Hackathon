from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    username: Optional[str] = None
    user_type: UserType = UserType.B2C
    
    # B2B Organization details (required if user_type is B2B)
    org_name: Optional[str] = None
    org_type: Optional[str] = None  # "Company" or "Institution"  
    org_address: Optional[str] = None
    org_contact_phone: Optional[str] = None
    org_logo_path: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    org_id: Optional[int] = None
    user_type: UserType

    model_config = {"from_attributes": True}
