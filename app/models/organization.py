from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import validates
from database.db_setup import Base
from schemas.organization_schema import OrgType as OrgTypeEnum 


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, comment="Unique organization identifier")
    name = Column(String(100), nullable=False, index=True, comment="Organization name")
    org_type = Column(Enum(OrgTypeEnum), nullable=False, comment="Organization type (Company / Institution)")
    address = Column(String(200), nullable=False, comment="Organization address")
    contact_email = Column(String(100), nullable=False, index=True, comment="Contact email")
    contact_phone = Column(String(20), nullable=True, comment="Contact phone number")
    logo_path = Column(String(200), nullable=True, comment="URL or path to organization logo")

    @validates("name", "address")
    def validate_non_empty(self, key, value):
        if not value.strip():
            raise ValueError(f"{key} cannot be empty or whitespace")
        return value.strip()

    @validates("contact_email")
    def validate_email(self, key, value):
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value

    @validates("contact_phone")
    def validate_phone(self, key, value):
        if value:
            import re
            if not re.match(r"^\+?\d[\d\s\-]{5,18}\d$", value):
                raise ValueError("Invalid phone number format")
        return value

    @validates("logo_path")
    def validate_logo_path(self, key, value):
        if value:
            from urllib.parse import urlparse
            parsed = urlparse(value)
            if all([parsed.scheme, parsed.netloc]) and parsed.scheme in ("http", "https"):
                return value 
            if not value.endswith((".png", ".jpg", ".jpeg", ".svg")):
                raise ValueError("Logo path must be a valid image file or URL")
        return value