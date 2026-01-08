"""Cloud credential models"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class CloudProvider(str, enum.Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    KUBERNETES = "kubernetes"


class CloudCredential(Base):
    __tablename__ = "cloud_credentials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    provider: Mapped[CloudProvider] = mapped_column(SQLEnum(CloudProvider), nullable=False)
    encrypted_data: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted JSON blob
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
