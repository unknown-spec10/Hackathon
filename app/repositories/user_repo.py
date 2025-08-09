from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from schemas.user_schema import UserCreate, UserUpdate, UserResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user: UserCreate) -> UserResponse:
    try:
        hashed_password = pwd_context.hash(user.password)
        user_data = {
            "email": user.email,
            "password_hash": hashed_password,
            "full_name": user.full_name,
            "user_type": user.user_type
        }
        
        # Add organization_id for B2B users
        if user.user_type == "B2B" and user.organization_id:
            user_data["organization_id"] = user.organization_id
            
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserResponse.from_orm(db_user)
    except IntegrityError:
        db.rollback()
        raise ValueError("Email already exists")


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def verify_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None


def change_password(db: Session, email: str, new_password: str) -> UserResponse | None:
    user = get_user_by_email(db, email)
    if user:
        user.password_hash = pwd_context.hash(new_password)
        db.commit()
        db.refresh(user)
        return UserResponse.from_orm(user)
    return None


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> UserResponse | None:
    user = get_user_by_id(db, user_id)
    if user:
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key != "id":
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return UserResponse.from_orm(user)
    return None