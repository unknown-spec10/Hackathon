from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.utils.auth_deps import get_current_user
from app.repositories.user_repo import UserRepository
from app.utils.auth import verify_password, create_access_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    user_repo = UserRepository()
    
    try:
        # Check if user already exists
        existing_user = user_repo.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        user_data = user.dict()
        user_data['password_hash'] = hashed_password
        user_data.pop('password', None)  # Remove plaintext password from data
        
        new_user = user_repo.create_user(user_data)
        return UserResponse.from_orm(new_user)
    finally:
        user_repo.close()

@router.post("/login")
async def login(user_credentials: UserLogin):
    """Login user and return access token"""
    user_repo = UserRepository()
    
    try:
        user = user_repo.get_user_by_email(user_credentials.email)
        if not user or not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        user_repo.close()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)
