from sqlalchemy.orm import Session
from app.models.user import User

def create_user(db: Session, username: str, password_hash: str, org_id: int):
    user = User(username=username, password_hash=password_hash, org_id=org_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def change_password(db: Session, username: str, new_password_hash: str):
    user = get_user_by_username(db, username)
    if user:
        user.password_hash = new_password_hash
        db.commit()
        db.refresh(user)
        return user
    return None
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()    
