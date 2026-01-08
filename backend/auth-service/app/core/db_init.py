"""
Database initialization module
Creates default organization, admin user, and roles on first startup
"""
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.rbac import User, Organization, Role
from app.services.security_service import security_service
from app.core.casbin import get_enforcer
from app.core.organization import get_organization_domain
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Get admin credentials from environment
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "<your-email>")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "<your-username>")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "<your-password>")


async def init_database():
    """
    Initialize database with default organization, admin user, and roles.
    This function is idempotent - it only creates if they don't exist.
    """
    import asyncio
    
    # Retry logic in case database isn't ready yet
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as db:
                # Check if admin user already exists
                result = await db.execute(
                    select(User).where(User.email == ADMIN_EMAIL.lower())
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    logger.info(f"Admin user already exists: {ADMIN_EMAIL}")
                    return
                
                # Validate password
                is_valid, error = security_service.validate_password_strength(ADMIN_PASSWORD)
                if not is_valid:
                    logger.error(f"Admin password does not meet requirements: {error}")
                    logger.error("Password requirements:")
                    logger.error("  - At least 12 characters")
                    logger.error("  - At least one uppercase letter")
                    logger.error("  - At least one lowercase letter")
                    logger.error("  - At least one digit")
                    logger.error("  - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
                    logger.error(f"Current ADMIN_PASSWORD length: {len(ADMIN_PASSWORD)}")
                    return
                
                # Create or get default organization
                org_result = await db.execute(
                    select(Organization).where(Organization.slug == "default")
                )
                org = org_result.scalar_one_or_none()
                
                if not org:
                    org = Organization(
                        name="Default Organization",
                        slug="default",
                        description="Default organization for the platform",
                        is_active=True
                    )
                    db.add(org)
                    await db.commit()
                    await db.refresh(org)
                    logger.info(f"Created organization: {org.name} (slug: {org.slug})")
                else:
                    logger.info(f"Using existing organization: {org.name} (slug: {org.slug})")
                
                # Hash password
                hashed_password = security_service.hash_password(ADMIN_PASSWORD)
                
                # Create admin user
                admin_user = User(
                    email=ADMIN_EMAIL.lower(),
                    username=ADMIN_USERNAME,
                    hashed_password=hashed_password,
                    full_name="System Administrator",
                    organization_id=org.id,
                    is_active=True
                )
                db.add(admin_user)
                await db.commit()
                await db.refresh(admin_user)
                logger.info(f"Created admin user: {ADMIN_EMAIL} (username: {ADMIN_USERNAME})")
                
                # Get or create platform-admin role
                role_result = await db.execute(
                    select(Role).where(Role.name == "platform-admin")
                )
                role = role_result.scalar_one_or_none()
                
                if not role:
                    role = Role(
                        name="platform-admin",
                        description="Platform administrator with full access",
                        is_platform_role=True
                    )
                    db.add(role)
                    await db.commit()
                    await db.refresh(role)
                    logger.info("Created platform-admin role")
                
                # Assign platform-admin role to admin user via Casbin
                org_domain = get_organization_domain(org)
                enforcer = get_enforcer()
                enforcer.set_org_domain(org_domain)
                
                if not enforcer.has_grouping_policy(str(admin_user.id), "platform-admin", org_domain):
                    enforcer.add_grouping_policy(str(admin_user.id), "platform-admin", org_domain)
                    enforcer.save_policy()
                    logger.info(f"Assigned platform-admin role to {ADMIN_USERNAME}")
                
                logger.info("✅ Database initialization complete!")
                logger.info(f"Admin login: {ADMIN_EMAIL} or {ADMIN_USERNAME}")
            
        except Exception as e:
            try:
                await db.rollback()
            except:
                pass
            if attempt < max_retries - 1:
                logger.warning(f"Database initialization attempt {attempt + 1} failed, retrying in {retry_delay}s: {e}")
                await asyncio.sleep(retry_delay)
                continue
            else:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {e}", exc_info=True)
                # Don't raise - allow service to start even if init fails
                # (might be a transient DB issue)
                return
        else:
            # Success - break out of retry loop
            break
