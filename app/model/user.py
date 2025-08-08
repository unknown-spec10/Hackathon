from sqlalchemy import Column, Integer, String
from database.db_setup import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)  
    org_id = Column(Integer)  
    email = Column(String, unique=True, nullable=False)