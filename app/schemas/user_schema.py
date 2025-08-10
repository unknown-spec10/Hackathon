from pydantic import BaseModel, EmailStr, Field, root_validator
from typing import Optional
from enum import Enum


class UserType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"


class OrgType(str, Enum):
    COMPANY = "Company"      # Can post jobs
    INSTITUTION = "Institution"  # Can set courses


class UserTypeSelection(BaseModel):
    """First step: User selects their type"""
    user_type: UserType


class B2BUserCreate(BaseModel):
    """B2B User registration with organization details"""
    # User details
    email: EmailStr
    password: str = Field(min_length=6)
    username: Optional[str] = None
    user_type: UserType = UserType.B2B
    
    # Organization details (all required for B2B)
    org_name: str = Field(min_length=1)
    org_type: OrgType
    org_address: str = Field(min_length=1)
    org_contact_phone: str = Field(min_length=10)
    org_logo_path: Optional[str] = None  # Optional logo upload


class B2CUserCreate(BaseModel):
    """B2C User registration with personal details"""
    # Personal details
    email: EmailStr
    password: str = Field(min_length=6)
    username: str = Field(min_length=1)
    user_type: UserType = UserType.B2C
    
    # Additional personal details
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None  # JSON string of skills array
    experience_years: Optional[int] = Field(ge=0, default=0)


class UserCreate(BaseModel):
    """Unified user creation schema for backward compatibility"""
    email: EmailStr
    password: str = Field(min_length=6)
    username: Optional[str] = None
    user_type: UserType = UserType.B2C
    
    # B2B Organization details (required if user_type is B2B)
    org_name: Optional[str] = None
    org_type: Optional[str] = None
    org_address: Optional[str] = None
    org_contact_phone: Optional[str] = None
    org_logo_path: Optional[str] = None
    
    # B2C Personal details
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = Field(ge=0, default=0)
    
    @root_validator(skip_on_failure=True)
    def validate_user_fields(cls, values):
        user_type = values.get('user_type')
        
        if user_type == UserType.B2B:
            required_fields = ['org_name', 'org_type', 'org_address', 'org_contact_phone']
            for field in required_fields:
                if not values.get(field):
                    raise ValueError(f'{field} is required for B2B users')
        
        elif user_type == UserType.B2C:
            if not values.get('username'):
                raise ValueError('Username is required for B2C users')
        
        return values


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    org_id: Optional[int] = None
    user_type: UserType
    
    # B2C fields
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """User login schema"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class UserTypeSelectionResponse(BaseModel):
    """Response for user type selection"""
    message: str
    next_step: str
    required_fields: list[str]


class OrganizationResponse(BaseModel):
    """Organization details in user response"""
    id: int
    name: str
    org_type: str
    address: str
    contact_phone: str
    logo_path: Optional[str] = None
    
    model_config = {"from_attributes": True}
