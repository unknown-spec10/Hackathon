from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.token_schema import Token
from app.utils.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from typing import Optional
from app.utils.deps import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserTypeSelection, B2BUserCreate, B2CUserCreate, UserType, OrgType, UserTypeSelectionResponse
from app.schemas.token_schema import Token
from app.utils.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from typing import Optional
from app.utils.deps import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/select-user-type", response_model=UserTypeSelectionResponse)
def select_user_type(selection: UserTypeSelection):
    """First step: User selects B2B or B2C"""
    return UserTypeSelectionResponse(
        message=f"User type '{selection.user_type.value}' selected",
        next_step="b2b_signup" if selection.user_type == UserType.B2B else "b2c_signup",
        required_fields={
            "B2B": ["email", "password", "org_name", "org_type", "org_address", "org_contact_phone"],
            "B2C": ["email", "password", "username", "full_name"]
        }[selection.user_type.value]
    )


@router.post("/signup/b2b", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_b2b(user_data: B2BUserCreate, db: Session = Depends(get_db)):
    """B2B user registration with organization details"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate organization type permissions
    if user_data.org_type == OrgType.COMPANY:
        permissions = "Can post jobs"
    elif user_data.org_type == OrgType.INSTITUTION:
        permissions = "Can set courses"
    else:
        raise HTTPException(status_code=400, detail="Invalid organization type")

    hashed_pw = get_password_hash(user_data.password)
    
    # Create organization first
    from app.models.profile import Organization, OrgTypeEnum
    try:
        org_type_enum = OrgTypeEnum.COMPANY if user_data.org_type == OrgType.COMPANY else OrgTypeEnum.INSTITUTION
    except:
        raise HTTPException(status_code=400, detail="Invalid org_type")
        
    new_org = Organization(
        name=user_data.org_name,
        org_type=org_type_enum,
        address=user_data.org_address,
        contact_email=user_data.email,
        contact_phone=user_data.org_contact_phone,
        logo_path=user_data.org_logo_path
    )
    db.add(new_org)
    db.flush()  # Get the org ID without committing
    org_id = new_org.id

    new_user = User(
        email=user_data.email,
        password_hash=hashed_pw,
        username=user_data.username or f"org_{new_org.id}",
        org_id=org_id,
        user_type=user_data.user_type,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/signup/b2c", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_b2c(user_data: B2CUserCreate, db: Session = Depends(get_db)):
    """B2C user registration with personal details"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pw,
        username=user_data.username,
        org_id=None,
        user_type=user_data.user_type,
        full_name=user_data.full_name,
        phone=user_data.phone,
        location=user_data.location,
        bio=user_data.bio,
        skills=user_data.skills,
        experience_years=user_data.experience_years
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Legacy unified signup endpoint for backward compatibility"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user_data.password)
    
    # If B2B user, create organization first
    org_id = None
    if user_data.user_type.value == "B2B":
        # Validate required organization fields
        if not all([user_data.org_name, user_data.org_type, user_data.org_address, user_data.org_contact_phone]):
            raise HTTPException(
                status_code=400, 
                detail="B2B users must provide org_name, org_type, org_address, and org_contact_phone"
            )
        
        # Create organization
        from app.models.profile import Organization, OrgTypeEnum
        try:
            org_type_enum = OrgTypeEnum.COMPANY if user_data.org_type == "Company" else OrgTypeEnum.INSTITUTION
        except:
            raise HTTPException(status_code=400, detail="org_type must be 'Company' or 'Institution'")
            
        new_org = Organization(
            name=user_data.org_name,
            org_type=org_type_enum,
            address=user_data.org_address,
            contact_email=user_data.email,
            contact_phone=user_data.org_contact_phone,
            logo_path=user_data.org_logo_path
        )
        db.add(new_org)
        db.flush()  # Get the org ID without committing
        org_id = new_org.id

    new_user = User(
        email=user_data.email,
        password_hash=hashed_pw,
        username=user_data.username,
        org_id=org_id,
        user_type=user_data.user_type,
        full_name=user_data.full_name,
        phone=user_data.phone,
        location=user_data.location,
        bio=user_data.bio,
        skills=user_data.skills,
        experience_years=user_data.experience_years
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id), "user_type": user.user_type.value})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
