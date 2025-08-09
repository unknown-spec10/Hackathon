from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import validates, relationship
from database.db_setup import Base
from schemas.user_schema import UserType  # Reuse schema enum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="Unique user identifier")
    email = Column(String(100), unique=True, nullable=False, comment="User email address")
    password_hash = Column(String(128), nullable=False, comment="Hashed user password")
    full_name = Column(String(100), nullable=False, index=True, comment="Full name of the user")
    user_type = Column(Enum(UserType), nullable=False, comment="User type (B2B or B2C)")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, comment="Organization ID for B2B users")
    
    # Relationships
    organization = relationship("Organization", back_populates="users")

    @validates("email", "full_name")
    def validate_non_empty(self, key, value):
        if not value.strip():
            raise ValueError(f"{key} cannot be empty or whitespace")
        return value.strip()

    @validates("email")
    def validate_email(self, key, value):
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value

    @validates("password_hash")
    def validate_password_hash(self, key, value):
        if not value.strip():
            raise ValueError("Password hash cannot be empty or whitespace")
        return value