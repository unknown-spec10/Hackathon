import enum
from sqlalchemy import Column, Integer, String, Enum
from database.db_setup import Base


class UserTypeEnum(enum.Enum):
    B2B = "B2B"  # Organization users (can post jobs/courses)
    B2C = "B2C"  # Talent users (search for jobs)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)  
    org_id = Column(Integer)  
    email = Column(String, unique=True, nullable=False)
    user_type = Column(Enum(UserTypeEnum), nullable=False, default=UserTypeEnum.B2C)