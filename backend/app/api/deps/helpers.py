"""Helper functions for dependencies"""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from casbin import Enforcer

from app.models.rbac import User, Role
from app.models.business_unit import BusinessUnitMember
from app.core.organization import get_user_organization, get_organization_domain
from app.core.authorization import get_user_platform_roles, parse_permission_slug
from app.logger import logger


async def is_platform_admin(user: User, db: AsyncSession, enforcer: Enforcer) -> bool:
    """
    Check if user has platform admin permissions (any platform:* permission).
    This checks permissions directly through all user roles (including group-inherited),
    not just platform roles, to handle cases where admin roles might not be marked as platform roles.
    """
    # Get org domain
    org = await get_user_organization(user, db)
    org_domain = get_organization_domain(org)
    
    # Ensure enforcer has org_domain set if it's a wrapper
    if hasattr(enforcer, 'set_org_domain') and (not hasattr(enforcer, '_org_domain') or not enforcer._org_domain):
        enforcer.set_org_domain(org_domain)
    
    # Check if enforcer is OrgAwareEnforcer (only takes 3 args) or base enforcer (takes 4 args)
    is_org_aware = hasattr(enforcer, '_org_domain') and hasattr(enforcer, '_enforcer')
    
    # Check if user has ADMIN-ONLY platform permissions (not just any platform permission)
    # Note: platform:users:list and platform:roles:list are also given to BU owners,
    # so we need to check for permissions that are ONLY given to platform admins
    key_admin_permissions = [
        "platform:business_units:create",   # Only admins can create BUs
        "platform:business_units:delete",   # Only admins can delete BUs
        "platform:roles:create",            # Only admins can create roles
        "platform:users:create",            # Only admins can create users
        "platform:organizations:update",    # Only admins can update org settings
    ]
    
    # Get ALL user roles (including through group membership) - not just platform roles
    # This is important because admin roles might not be marked as platform roles
    user_id = str(user.id)
    all_user_roles = []
    
    try:
        if is_org_aware:
            # OrgAwareEnforcer: get all roles including group-inherited
            all_user_roles = enforcer.get_roles_for_user(user_id)
        else:
            # Base enforcer: get all roles including group-inherited
            all_user_roles = enforcer.get_roles_for_user(user_id, org_domain)
    except Exception as e:
        logger.warning(f"Failed to get roles for user {user_id}: {e}")
        # Fallback: try get_implicit_roles_for_user which includes group inheritance
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
        except Exception as e2:
            logger.warning(f"Failed to get implicit roles for user {user_id}: {e2}")
    
    logger.debug(f"User {user.id} all roles (including group-inherited): {all_user_roles}")
    
    # Filter to only actual role names (not group names)
    # Only check permissions for roles that exist in the database
    role_result = await db.execute(select(Role.name))
    valid_role_names = {role_name for role_name in role_result.scalars().all()}
    
    # Filter all_user_roles to only include valid role names
    valid_roles = [role for role in all_user_roles if role in valid_role_names]
    logger.debug(f"User {user.id} valid roles (filtered from groups): {valid_roles}")
    
    # Also get platform roles for logging
    platform_roles = await get_user_platform_roles(user, db, enforcer, org_domain)
    logger.debug(f"User {user.id} platform roles: {platform_roles}")
    
    # Fallback: Directly check if user has "admin" role assigned
    has_admin_role = False
    if is_org_aware:
        has_admin_role = enforcer.has_grouping_policy(user_id, "admin")
    else:
        has_admin_role = enforcer.has_grouping_policy(user_id, "admin", org_domain)
    
    if has_admin_role and "admin" not in valid_roles:
        logger.debug(f"User {user.id} has admin role assigned directly, adding to roles")
        valid_roles.append("admin")
    
    if not valid_roles:
        logger.debug(f"User {user.id} has no valid roles, cannot be platform admin")
        return False
    
    # Check each key permission directly using the enforcer through VALID user roles only
    # This way it works even if the role isn't marked as is_platform_role
    for perm in key_admin_permissions:
        try:
            obj, act = parse_permission_slug(perm)
            logger.debug(f"Checking permission '{perm}' -> obj='{obj}', act='{act}' for roles {valid_roles}")
            for role in valid_roles:
                if is_org_aware:
                    # OrgAwareEnforcer: (role, obj, act) - org_domain is injected automatically
                    result = enforcer.enforce(role, obj, act)
                    logger.debug(f"  Role '{role}' with OrgAwareEnforcer: {result}")
                    if result:
                        logger.debug(f"User {user.id} is platform admin (has permission '{perm}' via role '{role}')")
                        return True
                else:
                    # Base enforcer: (role, org_domain, obj, act)
                    result = enforcer.enforce(role, org_domain, obj, act)
                    logger.debug(f"  Role '{role}' with base enforcer: {result}")
                    if result:
                        logger.debug(f"User {user.id} is platform admin (has permission '{perm}' via role '{role}')")
                        return True
        except ValueError as e:
            logger.warning(f"Error parsing permission '{perm}': {e}")
            continue
    
    return False


async def get_user_platform_roles(
    user: User,
    db: AsyncSession,
    enforcer: Enforcer,
    org_domain: str
) -> list:
    """
    Get user's platform-level roles (not BU-scoped).
    Platform roles are roles where is_platform_role = True.
    """
    # Get all roles for user in this organization
    # Handle both OrgAwareEnforcer and base Enforcer
    if hasattr(enforcer, '_enforcer') or hasattr(enforcer, '_org_domain'):
        # It's OrgAwareEnforcer, don't pass org_domain
        user_roles = enforcer.get_roles_for_user(str(user.id))
    else:
        # It's base Enforcer, need org_domain
        user_roles = enforcer.get_roles_for_user(str(user.id), org_domain)
    
    # Filter to only platform roles
    if not user_roles:
        return []
    
    result = await db.execute(
        select(Role).where(Role.name.in_(user_roles), Role.is_platform_role == True)
    )
    platform_roles = result.scalars().all()
    return [r.name for r in platform_roles]


async def get_org_domain(
    current_user: User,
    db: AsyncSession
) -> str:
    """
    Get organization domain for current user.
    Use this in endpoints that need organization context for Casbin enforcement.
    """
    organization = await get_user_organization(current_user, db)
    return get_organization_domain(organization)


async def get_bu_membership(
    user_id: UUID,
    business_unit_id: UUID,
    db: AsyncSession
):
    """
    Get user's membership in a specific business unit with role.
    Returns first BusinessUnitMember if user is a member, None otherwise.
    Note: A user can have multiple roles in a BU, so we return the first one.
    """
    result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(
            BusinessUnitMember.user_id == user_id,
            BusinessUnitMember.business_unit_id == business_unit_id
        )
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_user_bu_role(
    user: User,
    business_unit_id: UUID,
    db: AsyncSession
):
    """
    Get user's role in a specific business unit.
    Returns Role if user is a member, None otherwise.
    """
    membership = await get_bu_membership(user.id, business_unit_id, db)
    if membership:
        return membership.role
    return None


async def check_bu_permission(
    user: User,
    business_unit_id: UUID,
    permission_slug: str,
    db: AsyncSession,
    enforcer: Enforcer,
    org_domain: str
) -> bool:
    """
    Check if a user has a specific permission in a business unit context.
    This is permission-based, not role-name-based.
    
    Args:
        user: The user to check
        business_unit_id: The business unit ID
        permission_slug: Permission to check (e.g., "business_units:manage_members")
        db: Database session
        enforcer: Casbin enforcer (should be OrgAwareEnforcer with org_domain set)
        org_domain: Organization domain
        
    Returns:
        True if user has the permission, False otherwise
    """
    from app.core.permission_registry import parse_permission_slug
    
    # Ensure enforcer has org_domain set (if it's a wrapper)
    if hasattr(enforcer, 'set_org_domain'):
        enforcer.set_org_domain(org_domain)
    
    # Check if user is platform admin using permission-based check
    is_admin = await is_platform_admin(user, db, enforcer)
    if is_admin:
        return True
    
    # Check if user is a member of the business unit
    membership = await get_bu_membership(user.id, business_unit_id, db)
    if not membership or not membership.role:
        # User is not a member of business unit
        logger.debug(f"[DEBUG check_bu_permission] User {user.email} is not a member of BU {business_unit_id} or has no role")
        return False
    
    logger.info(f"[DEBUG check_bu_permission] User {user.email} has membership in BU {business_unit_id} with role: {membership.role.name}")
    
    # Parse permission slug
    try:
        obj, act = parse_permission_slug(permission_slug)
    except ValueError as e:
        logger.error(f"Failed to parse permission slug '{permission_slug}': {e}")
        return False
    
    # Reload policies to ensure we have the latest BU-scoped permissions
    base_enforcer = enforcer
    if hasattr(enforcer, 'enforcer'):
        base_enforcer = enforcer.enforcer
    if hasattr(base_enforcer, 'load_policy'):
        base_enforcer.load_policy()
    
    # Check permission for this role in BU context
    # Format: (role, org_domain, bu:{bu_id}:resource, action)
    bu_obj = f"bu:{business_unit_id}:{obj}"
    
    logger.info(f"[DEBUG check_bu_permission] Checking permission: role={membership.role.name}, bu_obj={bu_obj}, act={act}, org_domain={org_domain}")
    
    # Handle different enforcer types
    if hasattr(enforcer, '_enforcer') and hasattr(enforcer, '_org_domain'):
        # It's an OrgAwareEnforcer: use 3-arg format (sub, obj, act), org_domain is injected automatically
        has_permission = enforcer.enforce(membership.role.name, bu_obj, act)
        logger.info(f"[DEBUG check_bu_permission] OrgAwareEnforcer result: {has_permission}")
    elif hasattr(enforcer, '_org_domain') and hasattr(enforcer, 'enforcer'):
        # MultiTenantEnforcerWrapper: use 3-arg format (sub, dom, obj, act)
        has_permission = enforcer.enforce(membership.role.name, org_domain, bu_obj, act)
        logger.info(f"[DEBUG check_bu_permission] MultiTenantEnforcerWrapper result: {has_permission}")
    else:
        # Base Casbin enforcer: expects (sub, dom, obj, act)
        has_permission = enforcer.enforce(membership.role.name, org_domain, bu_obj, act)
        logger.info(f"[DEBUG check_bu_permission] Base enforcer result: {has_permission}")
    
    # If not found, check global permission and create BU-scoped version if it exists
    if not has_permission:
        logger.info(f"[DEBUG check_bu_permission] BU-scoped permission not found, checking global permission: role={membership.role.name}, obj={obj}, act={act}")
        if hasattr(enforcer, '_enforcer') and hasattr(enforcer, '_org_domain'):
            # OrgAwareEnforcer: use 3-arg format
            global_has_permission = enforcer.enforce(membership.role.name, obj, act)
        elif hasattr(enforcer, '_org_domain') and hasattr(enforcer, 'enforcer'):
            # MultiTenantEnforcerWrapper: use 3-arg format
            global_has_permission = enforcer.enforce(membership.role.name, org_domain, obj, act)
        else:
            # Base Casbin enforcer: use 4-arg format
            global_has_permission = enforcer.enforce(membership.role.name, org_domain, obj, act)
        logger.info(f"[DEBUG check_bu_permission] Global permission check result: {global_has_permission}")
        
        if global_has_permission:
            # Role has permission globally, create BU-scoped version
            logger.info(f"Role '{membership.role.name}' has global permission '{permission_slug}', creating BU-scoped version for BU {business_unit_id}")
            # Use enforcer.add_policy - it will automatically add org_domain if it's a wrapper
            enforcer.add_policy(membership.role.name, org_domain, bu_obj, act)
            enforcer.save_policy()
            has_permission = enforcer.enforce(membership.role.name, org_domain, bu_obj, act)
            if has_permission:
                logger.info(f"Successfully created BU-scoped permission for role '{membership.role.name}': {bu_obj}:{act}")
            else:
                logger.warning(f"Failed to create BU-scoped permission for role '{membership.role.name}': {bu_obj}:{act}")
        else:
            # Try to create from default role permissions
            from app.core.migrate_casbin_policies import create_default_bu_role_permissions
            try:
                logger.info(f"Creating BU-scoped permissions for role '{membership.role.name}' in BU {business_unit_id} for permission {permission_slug}")
                await create_default_bu_role_permissions(membership.role.name, business_unit_id, org_domain, enforcer)
                enforcer.save_policy()
                # Check again after creating permissions
                has_permission = enforcer.enforce(membership.role.name, org_domain, bu_obj, act)
                if has_permission:
                    logger.info(f"Successfully created and verified BU permission for role '{membership.role.name}': {bu_obj}:{act}")
            except Exception as e:
                logger.error(f"Failed to create default BU permissions for role {membership.role.name} in BU {business_unit_id}: {e}", exc_info=True)
    
    return has_permission
