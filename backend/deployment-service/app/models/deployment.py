from sqlalchemy import String, ForeignKey, DateTime, BigInteger, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime
import enum
from typing import Optional, List, TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
    from .user import User


class DeploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    PROVISIONING = "provisioning"
    UPDATING = "updating"
    FAILED = "failed"
    DELETING = "deleting"
    DELETED = "deleted"


class DeploymentType(str, enum.Enum):
    INFRASTRUCTURE = "infrastructure"
    MICROSERVICE = "microservice"


class CICDStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Environment(str, enum.Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentTag(Base):
    """Tags for deployments - flexible key-value pairs"""
    __tablename__ = "deployment_tags"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('deployment_id', 'key', name='uix_deployment_tag_key'),
    )
    
    # Relationship
    deployment: Mapped["Deployment"] = relationship("Deployment", back_populates="tags")


class Deployment(Base):
    __tablename__ = "deployments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=DeploymentStatus.PROVISIONING)
    deployment_type: Mapped[str] = mapped_column(String(50), nullable=False, default=DeploymentType.INFRASTRUCTURE)
    
    # Environment & Cost Tracking
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default=Environment.DEVELOPMENT, index=True)
    cost_center: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    project_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_monthly_cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    actual_monthly_cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Plugin reference
    plugin_id: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Infrastructure details
    stack_name: Mapped[str] = mapped_column(String(255), nullable=True)
    cloud_provider: Mapped[str] = mapped_column(String(50), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    git_branch: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Microservice details
    github_repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_repo_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # CI/CD status tracking
    ci_cd_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ci_cd_run_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    ci_cd_run_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ci_cd_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Update tracking
    update_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_update_job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_update_error: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_update_attempted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Infrastructure linking (for microservices with associated infra)
    pulumi_stack_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    infrastructure_deployment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Data
    inputs: Mapped[Optional[dict]] = mapped_column(JSONB)
    outputs: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Ownership
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key to users table (exists in DB but not in this service's models)
    
    # Business Unit
    business_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)  # Foreign key to business_units table (exists in DB but not in this service's models)
    
    # Organization (for direct filtering)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key to organizations table (exists in DB but not in this service's models)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tags: Mapped[List["DeploymentTag"]] = relationship("DeploymentTag", back_populates="deployment", cascade="all, delete-orphan")
    history: Mapped[List["DeploymentHistory"]] = relationship("DeploymentHistory", back_populates="deployment", cascade="all, delete-orphan", order_by="DeploymentHistory.version_number.desc()")
    costs: Mapped[List["DeploymentCost"]] = relationship("DeploymentCost", back_populates="deployment", cascade="all, delete-orphan", order_by="DeploymentCost.billing_month.desc()")
    # User relationship - using primaryjoin since User model is from different service
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id], primaryjoin="Deployment.user_id == User.id", viewonly=True)


class DeploymentHistory(Base):
    """Tracks all versions/changes to deployments for history and rollback capability"""
    __tablename__ = "deployment_history"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    inputs: Mapped[dict] = mapped_column(JSONB, nullable=False)
    outputs: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('deployment_id', 'version_number', name='uix_deployment_version'),
    )
    
    # Relationships
    deployment: Mapped["Deployment"] = relationship("Deployment", back_populates="history")


class DeploymentCost(Base):
    """Historical cost records for deployments"""
    __tablename__ = "deployment_costs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False, index=True)
    
    billing_month: Mapped[str] = mapped_column(String(7), nullable=False)  # Format: YYYY-MM
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    
    # Breakdown details (stored as JSON)
    # e.g., {"compute": 45.0, "storage": 12.5, "network": 2.1}
    breakdown: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('deployment_id', 'billing_month', name='uix_deployment_cost_month'),
    )
    
    # Relationships
    deployment: Mapped["Deployment"] = relationship("Deployment", back_populates="costs")
