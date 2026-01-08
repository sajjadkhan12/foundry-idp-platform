"""Job models"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, JSON, Integer, Enum as SQLEnum, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEAD_LETTER = "dead_letter"


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    plugin_version_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # No FK
    deployment_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)  # UUID stored as string
    status: Mapped[str] = mapped_column(String, default=JobStatus.PENDING.value)  # Store as string, will be cast to enum in DB
    triggered_by: Mapped[str] = mapped_column(String, nullable=False)
    inputs: Mapped[dict] = mapped_column(JSON, default={})
    outputs: Mapped[Optional[dict]] = mapped_column(JSON)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    logs: Mapped[List["JobLog"]] = relationship(
        "JobLog",
        primaryjoin="Job.id == foreign(JobLog.job_id)",
        back_populates="job",
        cascade="all, delete-orphan"
    )


class JobLog(Base):
    __tablename__ = "job_logs"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String, nullable=False, index=True)  # No FK to avoid cross-service dependencies
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    level: Mapped[str] = mapped_column(String, default="INFO")
    message: Mapped[str] = mapped_column(Text, nullable=False)

    job: Mapped["Job"] = relationship(
        "Job",
        primaryjoin="foreign(JobLog.job_id) == Job.id",
        back_populates="logs"
    )


# Event listener to convert enum to value before insert/update
@event.listens_for(Job, "before_insert", propagate=True)
@event.listens_for(Job, "before_update", propagate=True)
def receive_before_insert(mapper, connection, target):
    """Convert JobStatus enum to its value before database insert/update"""
    if isinstance(target.status, JobStatus):
        target.status = target.status.value
