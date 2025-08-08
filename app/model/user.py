from sqlalchemy import Column, Integer, String
from database.db_setup import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)  # Store hashed password
    org_id = Column(Integer)  # ForeignKey link optional
    email = Column(String, unique=True, nullable=False)