#!/usr/bin/env python3
"""
Fix existing organization-admin role to be a Platform role with all permissions
Run this script to update the existing organization-admin role from Business unit to Platform role
and ensure all platform permissions are assigned.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.future import select
from app.models.rbac import Role
from app.core.casbin import get_enforcer, invalidate_policy_cache
from app.core.permission_registry import parse_permission_slug, get_platform_permissions
from app.config import settings

# Database URL - use the one from settings
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def fix_organization_admin_role():
    """Fix existing organization-admin role to be Platform role with all permissions"""
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        try:
            # Find the organization-admin role
            role_result = await db.execute(
                select(Role).where(Role.name == "organization-admin")
            )
            org_admin_role = role_result.scalar_one_or_none()
            
            if not org_admin_role:
                print("❌ organization-admin role not found. It will be created when you create a new organization.")
                return
            
            print(f"Found organization-admin role (ID: {org_admin_role.id})")
            print(f"Current is_platform_role: {org_admin_role.is_platform_role}")
            
            # Update role if it's not a Platform role
            role_updated = False
            if not org_admin_role.is_platform_role:
                org_admin_role.is_platform_role = True
                await db.commit()
                await db.refresh(org_admin_role)
                print("✅ Updated organization-admin role from Business unit to Platform role")
                role_updated = True
            else:
                print("✅ Role is already a Platform role")
            
            # Get all platform permissions
            platform_permissions = get_platform_permissions()
            print(f"\nAssigning {len(platform_permissions)} platform permissions to organization-admin role...")
            
            # Assign all platform permissions to the role
            enforcer = get_enforcer()
            enforcer.set_org_domain("*")
            
            permissions_added = 0
            permissions_existing = 0
            permissions_failed = 0
            
            for perm_slug in platform_permissions:
                try:
                    obj, act = parse_permission_slug(perm_slug)
                    # Check if policy already exists before adding
                    existing_policies = enforcer.get_filtered_policy(0, "organization-admin", "*", obj, act)
                    if not existing_policies:
                        enforcer.add_policy("organization-admin", "*", obj, act)
                        permissions_added += 1
                    else:
                        permissions_existing += 1
                except Exception as e:
                    print(f"⚠️  Failed to add permission {perm_slug}: {e}")
                    permissions_failed += 1
            
            enforcer.save_policy()
            invalidate_policy_cache()
            
            print(f"\n✅ Permission assignment complete:")
            print(f"   - Added: {permissions_added} new permissions")
            print(f"   - Already existed: {permissions_existing} permissions")
            if permissions_failed > 0:
                print(f"   - Failed: {permissions_failed} permissions")
            
            if role_updated or permissions_added > 0:
                print("\n✅ organization-admin role has been fixed successfully!")
                print("   The role is now a Platform role with all platform permissions assigned.")
            else:
                print("\n✅ organization-admin role is already correctly configured!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ ERROR: Failed to fix organization-admin role: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_organization_admin_role())
