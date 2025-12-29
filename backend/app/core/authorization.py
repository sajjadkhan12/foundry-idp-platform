"""
Core Authorization Module - Unified permission checking for all scopes.

This module provides centralized authorization logic that handles:
- Platform-level permissions (no BU required)
- Business Unit-scoped permissions (BU required)
- User-specific permissions (no BU required)
"""
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from casbin import Enforcer

from app.models.rbac import User, Role
from app.models.business_unit import BusinessUnitMember
from app.core.organization import get_user_organization, get_organization_domain
from app.core.permission_registry import get_permission_scope, parse_permission_slug


async def get_user_platform_roles(
    user: User,
    db: AsyncSession,
    enforcer: Enforcer,
    org_domain: str
) -> list[str]:
    """
    Get user's platform-level roles (not BU-scoped).
    Platform roles are roles where is_platform_role = True.
    """
    from sqlalchemy.future import select
    
    # Get all roles for user in this organization
    # Handle different enforcer types:
    # 1. OrgAwareEnforcer (from deps.py) - has _enforcer and _org_domain, get_roles_for_user(user_id)
    # 2. MultiTenantEnforcerWrapper (from casbin.py) - has _enforcer and _org_domain, get_roles_for_user(user, domain=None)
    # 3. Base Casbin Enforcer - get_implicit_roles_for_user(user, domain)
    
    # Check if it's a wrapper with _org_domain attribute
    if hasattr(enforcer, '_org_domain'):
        # It's OrgAwareEnforcer or MultiTenantEnforcerWrapper
        # Check if _org_domain is set, if not, set it
        if not enforcer._org_domain:
            enforcer.set_org_domain(org_domain)
        # MultiTenantEnforcerWrapper.get_roles_for_user accepts optional domain
        # But if _org_domain is set, we don't need to pass it
        try:
            user_roles = enforcer.get_roles_for_user(str(user.id))
        except TypeError:
            # If that fails, try with domain
            user_roles = enforcer.get_roles_for_user(str(user.id), org_domain)
    elif hasattr(enforcer, 'enforcer'):
        # It's a wrapper but not the expected type, access underlying enforcer
        base_enforcer = enforcer.enforcer
        try:
            implicit_roles = base_enforcer.get_implicit_roles_for_user(str(user.id), org_domain)
            user_roles = []
            for role_info in implicit_roles:
                if isinstance(role_info, (list, tuple)) and len(role_info) > 0:
                    user_roles.append(role_info[0])
                else:
                    user_roles.append(role_info)
            user_roles = list(set(user_roles))
        except Exception:
            user_roles = []
    else:
        # It's base Casbin Enforcer, use get_implicit_roles_for_user with domain
        try:
            implicit_roles = enforcer.get_implicit_roles_for_user(str(user.id), org_domain)
            # Extract role names from implicit roles
            user_roles = []
            for role_info in implicit_roles:
                if isinstance(role_info, (list, tuple)) and len(role_info) > 0:
                    user_roles.append(role_info[0])
                else:
                    user_roles.append(role_info)
            user_roles = list(set(user_roles))
        except Exception:
            # Fallback: try get_roles_for_user without domain
            try:
                user_roles = enforcer.get_roles_for_user(str(user.id))
            except Exception:
                user_roles = []
    
    # Filter to only platform roles
    from app.logger import logger
    logger.debug(f"User {user.id} has roles from enforcer: {user_roles}")
    
    if not user_roles:
        logger.debug(f"User {user.id} has no roles from enforcer")
        return []
    
    result = await db.execute(
        select(Role).where(Role.name.in_(user_roles), Role.is_platform_role == True)
    )
    platform_roles = result.scalars().all()
    platform_role_names = [r.name for r in platform_roles]
    logger.debug(f"User {user.id} platform roles after filtering: {platform_role_names}")
    return platform_role_names


async def get_bu_membership(
    user_id: uuid.UUID,
    business_unit_id: uuid.UUID,
    db: AsyncSession
) -> Optional[BusinessUnitMember]:
    """
    Get user's membership in a specific business unit with role.
    Returns first BusinessUnitMember with a role if user is a member, None otherwise.
    Note: A user can have multiple roles in a BU, so we return the first one with a role.
    Prioritizes memberships with roles over memberships without roles.
    """
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    from sqlalchemy import or_
    
    # First try to get a membership with a role (prioritize non-NULL role_id)
    result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(
            BusinessUnitMember.user_id == user_id,
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.role_id.isnot(None)  # Only get memberships with roles
        )
        .limit(1)
    )
    membership = result.scalar_one_or_none()
    
    # If no membership with role found, return None (user needs a role to have permissions)
    return membership


async def check_permission(
    user: User,
    permission_slug: str,
    business_unit_id: Optional[uuid.UUID],
    db: AsyncSession,
    enforcer: Enforcer
) -> bool:
    """
    Unified permission check that handles all three scopes.
    
    New format support:
    - platform:resource:action (e.g., "platform:users:list")
    - business_unit:resource:action:environment (e.g., "business_unit:deployments:create:development")
    - user:resource:action (e.g., "user:profile:read")
    
    Args:
        user: Current user
        permission_slug: Permission to check (e.g., "platform:users:list", "business_unit:deployments:create:development")
        business_unit_id: Active business unit ID (None for platform/user permissions)
        db: Database session
        enforcer: Casbin enforcer
        
    Returns:
        True if user has permission, False otherwise
    """
    # Parse permission - extract resource and action (scope prefix is handled separately)
    try:
        obj, act = parse_permission_slug(permission_slug)
    except ValueError:
        return False
    
    # Get org domain
    org = await get_user_organization(user, db)
    org_domain = get_organization_domain(org)
    user_id = str(user.id)
    
    # Ensure enforcer has org_domain set if it's a wrapper
    if hasattr(enforcer, 'set_org_domain') and (not hasattr(enforcer, '_org_domain') or not enforcer._org_domain):
        enforcer.set_org_domain(org_domain)
    
    # Check if enforcer is OrgAwareEnforcer (only takes 3 args) or base enforcer (takes 4 args)
    is_org_aware = hasattr(enforcer, '_org_domain') and hasattr(enforcer, '_enforcer')
    
    # Check permission scope from slug prefix
    scope = get_permission_scope(permission_slug)
    
    # Check if enforcer is OrgAwareEnforcer (only takes 3 args) or base enforcer (takes 4 args)
    is_org_aware = hasattr(enforcer, '_org_domain') and hasattr(enforcer, '_enforcer')
    
    if scope == "platform":
        # Platform permission: Check platform roles only
        platform_roles = await get_user_platform_roles(user, db, enforcer, org_domain)
        for role in platform_roles:
            if is_org_aware:
                # OrgAwareEnforcer: (role, obj, act) - org_domain is injected automatically
                if enforcer.enforce(role, obj, act):
                    return True
            else:
                # Base enforcer: (role, org_domain, obj, act)
                if enforcer.enforce(role, org_domain, obj, act):
                    return True
        return False
    
    elif scope == "business_unit":
        # BU permission: Require active BU
        if not business_unit_id:
            return False
        
        # Check BU membership
        membership = await get_bu_membership(user.id, business_unit_id, db)
        if not membership:
            return False
        
        # If membership exists but has no role (role_id is NULL), user has no permissions
        if not membership.role_id:
            return False
        
        # Ensure role relationship is loaded (refresh to avoid lazy loading issues)
        # The selectinload should have loaded it, but refresh ensures it's accessible
        await db.refresh(membership, ["role"])
        
        # Get role and check permission
        role = membership.role
        if not role:
            return False
        # Check with BU context: bu:{bu_id}:resource
        bu_obj = f"bu:{business_unit_id}:{obj}"
        
        # Check if enforcer is OrgAwareEnforcer (from deps.py) or MultiTenantEnforcerWrapper
        # OrgAwareEnforcer has _enforcer and _org_domain attributes
        # MultiTenantEnforcerWrapper also has _org_domain
        is_org_aware_enforcer = hasattr(enforcer, '_enforcer') and hasattr(enforcer, '_org_domain')
        
        # Force reload policies to pick up new BU-scoped permissions
        # Navigate through wrappers to get to the base enforcer
        base_enforcer = enforcer
        if is_org_aware_enforcer:
            base_enforcer = enforcer._enforcer
            # If it's still a wrapper, get the actual base enforcer
            if hasattr(base_enforcer, 'enforcer'):
                base_enforcer = base_enforcer.enforcer
        
        # Reload policies on the base enforcer
        if hasattr(base_enforcer, 'load_policy'):
            base_enforcer.load_policy()
        
        if is_org_aware_enforcer:
            # OrgAwareEnforcer: (role.name, bu_obj, act) - org_domain is injected automatically
            # The OrgAwareEnforcer.enforce() will call _enforcer.enforce() which is a MultiTenantEnforcerWrapper
            # MultiTenantEnforcerWrapper.enforce(sub, obj, act) with 2 args injects org_domain
            # So it becomes: base_enforcer.enforce(role.name, org_domain, bu_obj, act)
            has_permission = enforcer.enforce(role.name, bu_obj, act)
            # Fallback: Check without BU prefix
            if not has_permission:
                has_permission = enforcer.enforce(role.name, obj, act)
        else:
            # Base enforcer: (role.name, org_domain, bu_obj, act)
            has_permission = enforcer.enforce(role.name, org_domain, bu_obj, act)
            # Fallback: Check without BU prefix
            if not has_permission:
                has_permission = enforcer.enforce(role.name, org_domain, obj, act)
        
        return has_permission
    
    else:  # user scope
        # User-specific permissions (profile, etc.)
        # Check if user has any role with this permission
        # Handle different enforcer types for getting user roles
        if hasattr(enforcer, '_org_domain'):
            # It's OrgAwareEnforcer or MultiTenantEnforcerWrapper, don't pass org_domain
            user_roles = enforcer.get_roles_for_user(user_id)
        elif hasattr(enforcer, 'get_roles_for_user') and hasattr(enforcer, 'get_implicit_roles_for_user'):
            # It's MultiTenantEnforcerWrapper, can pass domain
            user_roles = enforcer.get_roles_for_user(user_id, org_domain)
        else:
            # It's base Casbin Enforcer, use get_implicit_roles_for_user with domain
            try:
                implicit_roles = enforcer.get_implicit_roles_for_user(user_id, org_domain)
                user_roles = []
                for role_info in implicit_roles:
                    if isinstance(role_info, (list, tuple)) and len(role_info) > 0:
                        user_roles.append(role_info[0])
                    else:
                        user_roles.append(role_info)
                user_roles = list(set(user_roles))
            except Exception:
                # Fallback: try get_roles_for_user without domain
                user_roles = enforcer.get_roles_for_user(user_id)
        for role in user_roles:
            if is_org_aware:
                # OrgAwareEnforcer: (role, obj, act) - org_domain is injected automatically
                if enforcer.enforce(role, obj, act):
                    return True
            else:
                # Base enforcer: (role, org_domain, obj, act)
                if enforcer.enforce(role, org_domain, obj, act):
                    return True
        return False


async def check_bu_permission(
    user: User,
    permission_slug: str,
    business_unit_id: uuid.UUID,
    db: AsyncSession,
    enforcer: Enforcer
) -> bool:
    """
    Specialized check for BU-scoped permissions.
    Requires business_unit_id to be provided.
    """
    if not business_unit_id:
        return False
    return await check_permission(user, permission_slug, business_unit_id, db, enforcer)


async def check_platform_permission(
    user: User,
    permission_slug: str,
    db: AsyncSession,
    enforcer: Enforcer
) -> bool:
    """
    Specialized check for platform permissions.
    Does not require business unit context.
    """
    # Directly check the permission without circular dependency
    # Note: We don't check is_platform_admin here to avoid circular dependency
    # If user has platform permissions, they effectively have admin access
    return await check_permission(user, permission_slug, None, db, enforcer)

