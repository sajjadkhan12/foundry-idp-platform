#!/usr/bin/env python3
"""
Initialize admin user and default organization
Run this script once to set up the initial admin user.
"""
import asyncio
import os
import sys
from pathlib import Path
try:
    import bcrypt
except ImportError:
    # Fallback: install bcrypt if not available
    print("bcrypt not found, trying to use passlib...")
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        bcrypt = None
    except ImportError:
        print("ERROR: Neither bcrypt nor passlib is available. Please install bcrypt.")
        sys.exit(1)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from app.models.rbac import User, Organization, Role
from app.database import async_engine
from app.config import settings

# Get admin credentials from environment
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@foundry-idp.com")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123!@#")

def validate_password_strength(password: str):
    """Validate password strength"""
    import re
    
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        return False, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return True, ""

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    if bcrypt:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    else:
        # Use passlib if bcrypt module not available
        return pwd_context.hash(password)

async def init_admin():
    """Initialize admin user and default organization"""
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin user already exists
            result = await db.execute(
                select(User).where(User.email == ADMIN_EMAIL.lower())
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"Admin user already exists: {ADMIN_EMAIL}")
                return
            
            # Validate password
            is_valid, error = validate_password_strength(ADMIN_PASSWORD)
            if not is_valid:
                print(f"ERROR: Password does not meet requirements: {error}")
                print("\nPassword requirements:")
                print("  - At least 12 characters")
                print("  - At least one uppercase letter")
                print("  - At least one lowercase letter")
                print("  - At least one digit")
                print("  - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
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
                print(f"Created organization: {org.name} (slug: {org.slug})")
            else:
                print(f"Using existing organization: {org.name} (slug: {org.slug})")
            
            # Hash password
            hashed_password = hash_password(ADMIN_PASSWORD)
            
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
            print(f"Created admin user: {ADMIN_EMAIL} (username: {ADMIN_USERNAME})")
            
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
                print("Created platform-admin role")
            
            # Note: Casbin policies would need to be set up separately
            # For now, the user is created and can login
            
            print("\n✅ Admin user initialized successfully!")
            print(f"\nLogin credentials:")
            print(f"  Email/Username: {ADMIN_EMAIL} or {ADMIN_USERNAME}")
            print(f"  Password: {ADMIN_PASSWORD}")
            print("\nNote: You may need to assign the platform-admin role via Casbin policies")
            print("      or through the admin interface after logging in.")
            
        except Exception as e:
            await db.rollback()
            print(f"ERROR: Failed to initialize admin user: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_admin())
