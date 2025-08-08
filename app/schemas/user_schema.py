from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    username: Optional[str] = None
    org_id: Optional[int] = None
    user_type: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    org_id: Optional[int] = None
    user_type: Optional[str] = None

    class Config:
        orm_mode = True
