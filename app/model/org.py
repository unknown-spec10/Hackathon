from sqlalchemy import Column, Integer, String
from database.db_setup import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    org_type = Column(String)
    address = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    logo_path = Column(String)
