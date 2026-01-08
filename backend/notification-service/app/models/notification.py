"""Notification model"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class NotificationType(str, enum.Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}  # Don't recreate table, use existing

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Note: Foreign key constraint exists in database schema
    # We don't define it here to avoid SQLAlchemy validation issues
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default=NotificationType.INFO)
    is_read = Column(Boolean, default=False, index=True)
    link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
