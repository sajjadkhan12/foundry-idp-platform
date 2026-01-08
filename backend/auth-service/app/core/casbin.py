"""Casbin enforcer setup for auth microservice"""
import casbin
from casbin_sqlalchemy_adapter import Adapter
from sqlalchemy import create_engine, text
from app.config import settings
from app.core.enforcer_wrapper import MultiTenantEnforcerWrapper
import os
import time

# Create a synchronous engine for Casbin adapter
sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
if "postgresql://" not in sync_db_url and "postgresql+psycopg2://" not in sync_db_url:
    sync_db_url = sync_db_url.replace("postgresql:", "postgresql+psycopg2:")

engine = create_engine(
    sync_db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

adapter = Adapter(engine)

# Path to model.conf
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rbac_model.conf")

# Fix Casbin policy columns BEFORE initializing enforcer
def _fix_casbin_policy_columns_sync():
    """Fix Casbin policy columns using sync connection before enforcer init"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        with engine.connect() as conn:
            conn.execute(text("UPDATE casbin_rule SET v4 = NULL, v5 = NULL WHERE v4 IS NOT NULL OR v5 IS NOT NULL"))
            conn.execute(text("UPDATE casbin_rule SET v3 = NULL WHERE ptype = 'g' AND v3 IS NOT NULL"))
            conn.commit()
    except Exception as e:
        if "casbin_rule" not in str(e).lower() or "does not exist" not in str(e).lower():
            logger.debug(f"Could not fix Casbin columns (may be first run): {e}")

_fix_casbin_policy_columns_sync()

# Initialize enforcer
try:
    _base_enforcer = casbin.Enforcer(model_path, adapter)
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize Casbin enforcer: {e}")
    raise

enforcer = _base_enforcer

# Policy cache
_cache_ttl = float(os.getenv("CASBIN_CACHE_TTL", "2.0"))
_policy_cache = {
    "last_reload": 0,
    "cache_ttl": _cache_ttl
}

def _should_reload_policy() -> bool:
    """Check if policy should be reloaded based on cache TTL"""
    now = time.time()
    if now - _policy_cache["last_reload"] > _policy_cache["cache_ttl"]:
        _policy_cache["last_reload"] = now
        return True
    return False

def invalidate_policy_cache():
    """Invalidate policy cache - call this when permissions change"""
    _policy_cache["last_reload"] = 0

def get_enforcer():
    """Get Casbin enforcer wrapper."""
    if _should_reload_policy():
        _base_enforcer.load_policy()
    return MultiTenantEnforcerWrapper(_base_enforcer)
