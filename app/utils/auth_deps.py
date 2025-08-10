from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.utils.deps import get_db
from app.utils.auth import decode_access_token
from app.models.user import User, UserTypeEnum

# OAuth2 scheme for Bearer token
oauth2_scheme = HTTPBearer()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from token."""
    # Extract token from HTTPBearer
    access_token = token.credentials
    payload = decode_access_token(access_token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

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
