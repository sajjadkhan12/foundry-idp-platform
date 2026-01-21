"""Plugin models"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class Plugin(Base):
    __tablename__ = "plugins"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(String)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deployment_type: Mapped[str] = mapped_column(String(50), nullable=False, default="infrastructure")
    # Organization isolation - each plugin belongs to an organization
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship removed - manually query versions instead to avoid FK requirement
    # versions: Mapped[List["PluginVersion"]] = relationship(...)


class PluginVersion(Base):
    __tablename__ = "plugin_versions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plugin_id: Mapped[str] = mapped_column(String, nullable=False, index=True)  # No FK to avoid cross-service dependencies
    version: Mapped[str] = mapped_column(String, nullable=False)
    manifest: Mapped[dict] = mapped_column(JSON, nullable=False)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    git_repo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    git_branch: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    template_repo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    template_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship removed - manually query plugin instead to avoid FK requirement
    # plugin: Mapped["Plugin"] = relationship(back_populates="versions")
