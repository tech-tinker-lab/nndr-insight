from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

from app.models.base import Base

class DataStandardImportPlan(Base):
    __tablename__ = "data_standard_import_plans"
    __table_args__ = {"schema": "design_enhanced"}

    plan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(50), nullable=False)  # file, url, api
    source_path = Column(Text, nullable=False)        # file path or URL
    schedule = Column(String(100), nullable=True)     # cron or interval string
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    last_status = Column(String(50), nullable=True)   # success, failed, pending
    last_message = Column(Text, nullable=True)
    config = Column(JSONB, default=dict)              # extra config (headers, auth, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 