import casbin
from casbin_sqlalchemy_adapter import Adapter
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.enforcer_wrapper import MultiTenantEnforcerWrapper, create_enforcer_with_org_context
from app.models.rbac import User
from typing import Optional
import os
import time

# Create a synchronous engine for Casbin adapter
# The adapter currently requires a sync engine
sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
if "postgresql://" not in sync_db_url and "postgresql+psycopg2://" not in sync_db_url:
    sync_db_url = sync_db_url.replace("postgresql:", "postgresql+psycopg2:")

# Create engine with connection pooling for multi-worker/replica environments
engine = create_engine(
    sync_db_url,
    pool_size=10,  # Base pool size
    max_overflow=20,  # Allow overflow for multiple workers/replicas
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False
)

# Initialize adapter
adapter = Adapter(engine)

# Path to model.conf
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rbac_model.conf")

# Fix Casbin policy columns BEFORE initializing enforcer
# The adapter reads all non-NULL columns, so v4/v5 must be NULL (not empty strings)
# to avoid "invalid policy size" errors
def _fix_casbin_policy_columns_sync():
    """Fix Casbin policy columns using sync connection before enforcer init"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Set v4, v5 to NULL for all policies
            conn.execute(text("UPDATE casbin_rule SET v4 = NULL, v5 = NULL WHERE v4 IS NOT NULL OR v5 IS NOT NULL"))
            # Set v3 to NULL for grouping policies (they only use v0, v1, v2)
            conn.execute(text("UPDATE casbin_rule SET v3 = NULL WHERE ptype = 'g' AND v3 IS NOT NULL"))
            conn.commit()
    except Exception as e:
        # Table might not exist yet on first run, that's OK
        if "casbin_rule" not in str(e).lower() or "does not exist" not in str(e).lower():
            logger.debug(f"Could not fix Casbin columns (may be first run): {e}")

# Run the fix before initializing enforcer
_fix_casbin_policy_columns_sync()

# Initialize enforcer with error handling
try:
    _base_enforcer = casbin.Enforcer(model_path, adapter)
except Exception as e:
    # If initialization fails, try to clean up any problematic rows and retry
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize Casbin enforcer: {e}")
    logger.error("This might be due to NULL or empty string values in casbin_rule table v4/v5 columns.")
    logger.error("Please run: UPDATE casbin_rule SET v4 = NULL, v5 = NULL;")
    # Re-raise to fail fast
    raise

# For backward compatibility, keep the global enforcer reference
# but it will be wrapped
enforcer = _base_enforcer

# Policy cache: track last reload time and cache TTL
# In production with multiple replicas, reduce cache time for faster sync
import os
_cache_ttl = float(os.getenv("CASBIN_CACHE_TTL", "2.0"))  # Default 2 seconds, configurable
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
    """
    Dependency to get Casbin enforcer.
    
    Returns a wrapper that accepts both old (3-param) and new (4-param) formats.
    For proper multi-tenancy, the wrapper needs org_domain to be set via set_org_domain().
    """
    # Reload policy only if cache expired (performance optimization)
    if _should_reload_policy():
        _base_enforcer.load_policy()
    # Return wrapper that supports both old and new formats
    wrapper = MultiTenantEnforcerWrapper(_base_enforcer)
    return wrapper

async def get_enforcer_with_org(
    current_user: Optional[User] = None,
    db: Optional[AsyncSession] = None,
    org_domain: Optional[str] = None
) -> MultiTenantEnforcerWrapper:
    """
    Dependency to get organization-aware Casbin enforcer.
    
    This enforcer automatically injects organization domain into all enforcement checks.
    
    Args:
        current_user: Current authenticated user (to get organization from)
        db: Database session (to load organization if needed)
        org_domain: Explicit organization domain (if already known)
        
    Returns:
        MultiTenantEnforcerWrapper with organization context set
    """
    # Reload policy only if cache expired (performance optimization)
    if _should_reload_policy():
        _base_enforcer.load_policy()
    
    # Determine organization domain
    domain = org_domain
    if not domain and current_user:
        from app.core.organization import get_user_organization, get_organization_domain
        if db:
            org = await get_user_organization(current_user, db)
            domain = get_organization_domain(org)
        elif hasattr(current_user, 'organization') and current_user.organization:
            domain = get_organization_domain(current_user.organization)
    
    if not domain:
        # If we still don't have a domain, create a wrapper without context
        # It will log warnings on enforcement checks
        return MultiTenantEnforcerWrapper(_base_enforcer)
    
    return create_enforcer_with_org_context(_base_enforcer, domain)
