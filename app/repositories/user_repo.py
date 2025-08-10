from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import Organization
from app.models.resume import Resume
from app.utils.deps import get_db

class UserRepository:
    def __init__(self):
        self.db = next(get_db())
    
    def create_user(self, user_data: dict):
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int):
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_resume(self, resume_data: dict):
        """Create a new resume entry"""
        resume = Resume(**resume_data)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume
    
    def get_user_resumes(self, user_id: int):
        """Get all resumes for a user"""
        return self.db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).all()
    
    def get_resume_by_id(self, resume_id: int):
        """Get resume by ID"""
        return self.db.query(Resume).filter(Resume.id == resume_id).first()
    
    def delete_resume(self, resume_id: int):
        """Delete a resume"""
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            self.db.delete(resume)
            self.db.commit()
            return True
        return False

# Legacy functions for backward compatibility
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
