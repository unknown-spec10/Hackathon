import enum
from sqlalchemy import Column, Integer, String, Enum
from database.db_setup import Base


class OrgTypeEnum(enum.Enum):
    COMPANY = "Company"        # Can post jobs
    INSTITUTION = "Institution"  # Can set courses


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    org_type = Column(Enum(OrgTypeEnum), nullable=False)
    address = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=False)  # Required for B2B
    logo_path = Column(String, nullable=True)  # Optional logo upload
