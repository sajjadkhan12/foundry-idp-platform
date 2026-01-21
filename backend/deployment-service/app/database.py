"""Database configuration"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
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


async def get_db() -> AsyncSession:
    """Get database session - FastAPI dependency"""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
