"""Helper functions for auth microservice"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from casbin import Enforcer

from app.models.rbac import User, Role
from app.core.organization import get_user_organization, get_organization_domain
from app.core.authorization import get_user_platform_roles


async def is_platform_admin(user: User, db: AsyncSession, enforcer: Enforcer) -> bool:
    """Check if user has platform admin permissions"""
    org = await get_user_organization(user, db)
    org_domain = get_organization_domain(org)
    
    if hasattr(enforcer, 'set_org_domain') and (not hasattr(enforcer, '_org_domain') or not enforcer._org_domain):
        enforcer.set_org_domain(org_domain)
    
    key_admin_permissions = [
        "platform:business_units:create",
        "platform:business_units:delete",
        "platform:roles:create",
        "platform:users:create",
        "platform:organizations:update",
    ]
    
    user_id = str(user.id)
    all_user_roles = []
    
    try:
        if hasattr(enforcer, '_org_domain'):
            all_user_roles = enforcer.get_roles_for_user(user_id)
        else:
            all_user_roles = enforcer.get_roles_for_user(user_id, org_domain)
    except Exception:
        try:
            if hasattr(enforcer, '_enforcer'):
                base_enforcer = enforcer._enforcer
            else:
                base_enforcer = enforcer
            implicit_roles = base_enforcer.get_implicit_roles_for_user(user_id, org_domain)
            for role_info in implicit_roles:
                if isinstance(role_info, (list, tuple)) and len(role_info) > 0:
                    all_user_roles.append(role_info[0])
                else:
                    all_user_roles.append(role_info)
            all_user_roles = list(set(all_user_roles))
        except Exception:
            pass
    
    role_result = await db.execute(select(Role.name))
    valid_role_names = {role_name for role_name in role_result.scalars().all()}
    valid_roles = [role for role in all_user_roles if role in valid_role_names]
    
    has_admin_role = False
    if hasattr(enforcer, '_org_domain'):
        has_admin_role = enforcer.has_grouping_policy(user_id, "admin")
    else:
        has_admin_role = enforcer.has_grouping_policy(user_id, "admin", org_domain)
    
    if has_admin_role and "admin" not in valid_roles:
        valid_roles.append("admin")
    if not valid_roles:
        return False
    
    # Check if user has any of the key admin permissions
    for permission in key_admin_permissions:
        try:
            obj, act = permission.split(":")[1:]  # Skip "platform:" prefix
            if hasattr(enforcer, '_org_domain'):
                if enforcer.enforce(user_id, obj, act):
                    return True
            else:
                if enforcer.enforce(user_id, org_domain, obj, act):
                    return True
        except Exception:
            continue
    
    # Also check if user has "platform-admin" or "organization-admin" role
    if "platform-admin" in valid_roles or "admin" in valid_roles or "organization-admin" in valid_roles:
        return True
    
    return False


async def is_super_admin(user: User, db: AsyncSession, enforcer: Enforcer) -> bool:
    """Check if user is super admin (can manage all organizations)"""
    org = await get_user_organization(user, db)
    org_domain = get_organization_domain(org)
    
    if hasattr(enforcer, 'set_org_domain') and (not hasattr(enforcer, '_org_domain') or not enforcer._org_domain):
        enforcer.set_org_domain(org_domain)
    
    user_id = str(user.id)
    
    # Check directly in Casbin for super-admin role (most efficient)
    try:
        # Check all domains for super-admin role
        if enforcer.has_grouping_policy(user_id, "super-admin", org_domain):
            return True
        # Also check without domain (platform-level)
        if enforcer.has_grouping_policy(user_id, "super-admin", ""):
            return True
    except Exception:
        pass
    
    # Fallback: Check for super admin permissions
    super_permissions = [
        "super:organizations:create",
        "super:organizations:delete",
        "super:organizations:list",
    ]
    
    from app.core.authorization import check_permission
    
    for perm in super_permissions:
        try:
            if await check_permission(user, perm, None, db, enforcer):
                return True
        except Exception:
            continue
    
    return False
