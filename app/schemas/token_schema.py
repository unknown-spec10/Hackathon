from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional
from datetime import datetime


class TokenType(str, Enum):
    BEARER = "Bearer"


class Token(BaseModel):
    access_token: str = Field(
        ..., min_length=1, description="JWT or other access token", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: TokenType = Field(..., description="Token type (e.g., 'Bearer')", example=TokenType.BEARER)
    refresh_token: Optional[str] = Field(None, min_length=1, description="Refresh token, if applicable", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time", example="2025-08-09T12:00:00Z")

    @validator("access_token", "refresh_token")
    def validate_jwt(cls, v):
        if v and v.count(".") != 2:
            raise ValueError("Invalid JWT format")
        return v