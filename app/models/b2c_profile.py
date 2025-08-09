from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship, validates
from database.db_setup import Base
import re
from datetime import date


class B2CProfile(Base):
    __tablename__ = "b2c_profiles"

    id = Column(Integer, primary_key=True, index=True, comment="Unique profile identifier")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, comment="User ID")
    phone = Column(String(20), nullable=True, comment="Phone number")
    address = Column(String(200), nullable=True, comment="Address")
    bio = Column(Text, nullable=True, comment="User biography")
    date_of_birth = Column(Date, nullable=True, comment="Date of birth")
    profile_picture = Column(String(200), nullable=True, comment="URL or path to profile picture")
    
    # Relationships
    user = relationship("User", backref="b2c_profile")
    
    @validates("phone")
    def validate_phone(self, key, value):
        if value:
            if not re.match(r"^\+?\d[\d\s\-]{5,18}\d$", value):
                raise ValueError("Invalid phone number format")
        return value
    
    @validates("date_of_birth")
    def validate_date_of_birth(self, key, value):
        if value:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 13:
                raise ValueError("User must be at least 13 years old")
        return value
    
    @validates("profile_picture")
    def validate_profile_picture(self, key, value):
        if value:
            from urllib.parse import urlparse
            parsed = urlparse(value)
            if all([parsed.scheme, parsed.netloc]) and parsed.scheme in ("http", "https"):
                return value 
            if not value.endswith((".png", ".jpg", ".jpeg", ".svg")):
                raise ValueError("Profile picture must be a valid image file or URL")
        return value