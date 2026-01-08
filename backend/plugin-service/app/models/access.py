"""Plugin access models"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import enum
import uuid as uuid_module

Base = declarative_base()


class AccessRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


class PluginAccess(Base):
    """Plugin access grants"""
    __tablename__ = "plugin_access"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plugin_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    user_id: Mapped[uuid_module.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    business_unit_id: Mapped[Optional[uuid_module.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    granted_by: Mapped[uuid_module.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PluginAccessRequest(Base):
    """Plugin access requests"""
    __tablename__ = "plugin_access_requests"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid_module.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid_module.uuid4)
    plugin_id: Mapped[str] = mapped_column(String, nullable=False, index=True)  # Plugin IDs are strings like 'gcp-bucket'
    user_id: Mapped[uuid_module.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    business_unit_id: Mapped[Optional[uuid_module.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # Store as string to avoid enum issues
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[Optional[uuid_module.UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
