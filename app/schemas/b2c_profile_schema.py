from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional
from datetime import date
import re


class B2CProfileBase(BaseModel):
    phone: Optional[str] = Field(
        None, 
        pattern=r"^\+?\d[\d\s\-]{5,18}\d$", 
        description="Phone number (e.g., '+1234567890')", 
        example="+1234567890"
    )
    address: Optional[str] = Field(
        None, 
        description="User address", 
        example="123 Main St, New York, USA"
    )
    bio: Optional[str] = Field(
        None, 
        max_length=500, 
        description="User biography", 
        example="I am a software developer with 5 years of experience."
    )
    date_of_birth: Optional[date] = Field(
        None, 
        description="Date of birth (must be at least 13 years old)", 
        example="1990-01-01"
    )
    profile_picture: Optional[HttpUrl] = Field(
        None, 
        description="URL to the user's profile picture", 
        example="https://example.com/profile.jpg"
    )
    
    @validator("date_of_birth")
    def validate_age(cls, v):
        if v:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 13:
                raise ValueError("User must be at least 13 years old")
        return v


class B2CProfileCreate(B2CProfileBase):
    user_id: int = Field(..., description="User ID", example=1)


class B2CProfileUpdate(B2CProfileBase):
    pass


class B2CProfileResponse(B2CProfileBase):
    id: int = Field(..., description="Profile ID", example=1)
    user_id: int = Field(..., description="User ID", example=1)
    
    class Config:
        from_attributes = True