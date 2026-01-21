"""Database configuration"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from app.config import settings

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Async engine for async operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Disable SQL query logging
    future=True
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync engine for worker tasks (Pulumi needs sync)
sync_database_url = settings.DATABASE_URL.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql+psycopg2")
sync_engine = create_engine(
    sync_database_url,
    echo=False,  # Disable SQL query logging
    pool_pre_ping=True
)

# Sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


def get_sync_db_session():
    """Get synchronous database session for worker tasks"""
    return SessionLocal()


async def get_db() -> AsyncSession:
    """Get database session - FastAPI dependency"""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
