"""Database session management for worker tasks"""
from app.database import get_sync_db_session as _get_sync_db_session

# Re-export for compatibility
def get_sync_db_session():
    """Get a synchronous database session using the shared engine"""
    return _get_sync_db_session()

