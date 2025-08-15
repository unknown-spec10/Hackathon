from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.utils.deps import get_db
from app.utils.auth import decode_access_token
from app.models.user import User, UserTypeEnum

# OAuth2 scheme for Bearer token
oauth2_scheme = HTTPBearer()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    from app.core.settings import settings
    print(f"DEBUG: SECRET_KEY={settings.SECRET_KEY}")
    print(f"DEBUG: ALGORITHM={settings.ALGORITHM}")
    """Get the current authenticated user from token."""
    # Extract token from HTTPBearer
    access_token = token.credentials
    print(f"DEBUG: Incoming token: {access_token}")
    payload = decode_access_token(access_token)
    print(f"DEBUG: Decoded payload: {payload}")
    if not payload or "sub" not in payload:
        print("DEBUG: Invalid or expired token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    print(f"DEBUG: User ID from token: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print("DEBUG: User not found in database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    print(f"DEBUG: Authenticated user: {user}")
    return user


def require_b2b_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires the user to be B2B type."""
    if current_user.user_type != UserTypeEnum.B2B:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. B2B account required."
        )
    return current_user


def require_b2c_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires the user to be B2C type."""
    if current_user.user_type != UserTypeEnum.B2C:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. B2C account required."
        )
    return current_user
