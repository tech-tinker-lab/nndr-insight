from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, JSON, Text, Date, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from datetime import datetime

class DataStandard(Base):
    __tablename__ = "data_standards"
    __table_args__ = {"schema": "design_enhanced"}

    standard_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    standard_code = Column(String(100), unique=True, nullable=False)
    standard_name = Column(String(255), nullable=False)
    standard_type = Column(String(100), nullable=False)
    governing_body = Column(String(255))
    description = Column(Text)
    compliance_level = Column(String(50))
    version = Column(String(50))
    effective_date = Column(Date)
    expiry_date = Column(Date)
    website_url = Column(Text)
    contact_info = Column(JSONB, default=dict)
    created_by = Column(String(100), nullable=False, default='system')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    standard_id = Column(String, ForeignKey("design_enhanced.data_standards.standard_id"))
    standard_version = Column(String)
    upload_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    standard = relationship("DataStandard") 