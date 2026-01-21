"""Configuration models for organization and business unit settings"""
from sqlalchemy import String, ForeignKey, Boolean, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional
from app.database import Base


class OrganizationConfiguration(Base):
    """Organization or business unit level configuration storage"""
    __tablename__ = "organization_configurations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    business_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("business_units.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    config_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    config_value_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'business_unit_id', 'config_key', name='uq_org_config'),
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", backref="configurations")
    business_unit: Mapped[Optional["BusinessUnit"]] = relationship("BusinessUnit", backref="configurations")
