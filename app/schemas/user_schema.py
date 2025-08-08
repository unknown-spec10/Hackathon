from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from enum import Enum


class UserType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address", example="user@example.com")
    full_name: str = Field(..., min_length=2, description="Full name of the user", example="John Doe")
    user_type: UserType = Field(..., description="User type (B2B or B2C)", example=UserType.B2C)

    @validator("full_name")
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be empty or whitespace")
        return v.strip()


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        description="Password (must include letter, number, and special character)",
        example="Password123!"
    )


class UserUpdate(BaseModel):
    id: int = Field(..., description="User ID", example=1)
    full_name: Optional[str] = Field(None, min_length=2, description="Updated full name", example="Jane Doe")
    user_type: Optional[UserType] = Field(None, description="Updated user type (B2B or B2C)", example=UserType.B2B)

    @validator("full_name")
    def check_non_empty(cls, v):
        if v and not v.strip():
            raise ValueError("Full name cannot be empty or whitespace")
        return v.strip() if v else v


class UserResponse(UserBase):
    id: int = Field(..., description="User ID", example=1)

    class Config:
        from_attributes = True