from fastapi import Depends, HTTPException, status, Request, Header, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
import uuid
from app.database import get_db
from app.models.rbac import User, Organization
from app.config import settings
from app.core.organization import get_user_organization, get_organization_domain
from app.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Async query - eagerly load organization
    result = await db.execute(
        select(User)
        .options(selectinload(User.organization))
        .where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

from app.core.casbin import get_enforcer
from casbin import Enforcer

async def is_platform_admin(user: User, db: AsyncSession, enforcer: Enforcer) -> bool:
    """
    Check if user has platform admin permissions (any platform:* permission).
    This checks permissions directly through all user roles (including group-inherited),
    not just platform roles, to handle cases where admin roles might not be marked as platform roles.
    """
    from app.core.authorization import check_permission, get_user_platform_roles, parse_permission_slug
    from app.core.organization import get_user_organization, get_organization_domain
    
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
    from app.models.rbac import Role
    from sqlalchemy import select
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
    
    #logger.warning(f"User {user.id} is NOT platform admin (no key permissions found in roles: {valid_roles})")
    return False


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
    enforcer: Enforcer = Depends(get_enforcer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Check if user is a platform admin using permission-based checks instead of hardcoded role names.
    """
    # Use permission-based check instead of hardcoded role name
    is_admin = await is_platform_admin(current_user, db, enforcer)
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def is_allowed(permission_slug: str):
    """
    Dependency for checking permissions using Casbin with organization context.
    
    Supports new permission format with scope prefixes:
    - Platform: "platform:users:list" -> obj="users", act="list"
    - Business Unit: "business_unit:deployments:create:development" -> obj="deployments", act="create:development"
    - User: "user:profile:read" -> obj="profile", act="read"
    
    Casbin storage format: (role/user_id, org_domain, obj, act)
    """
    async def dependency(
        current_user: User = Depends(get_current_user),
        enforcer: Enforcer = Depends(get_enforcer),
        db: AsyncSession = Depends(get_db)
    ):
        from app.core.permission_registry import (
            parse_permission_slug,
            get_permission_scope
        )
        from app.core.authorization import check_permission
        
        # Parse permission slug using the registry function
        try:
            obj, act = parse_permission_slug(permission_slug)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid permission slug: {permission_slug} - {e}"
            )
        
        # Get permission scope
        scope = get_permission_scope(permission_slug)
        
        # Ensure enforcer has org_domain set if it's a wrapper
        # This is needed because get_enforcer() returns a MultiTenantEnforcerWrapper without org_domain
        from app.core.organization import get_user_organization, get_organization_domain
        org = await get_user_organization(current_user, db)
        org_domain = get_organization_domain(org)
        if hasattr(enforcer, 'set_org_domain') and (not hasattr(enforcer, '_org_domain') or not enforcer._org_domain):
            enforcer.set_org_domain(org_domain)
        
        # Check if user is platform admin first (admins bypass permission checks)
        logger.debug(f"Checking permission '{permission_slug}' for user {current_user.id} ({current_user.email})")
        is_admin = await is_platform_admin(current_user, db, enforcer)
        logger.debug(f"User {current_user.id} is_platform_admin: {is_admin}")
        
        if is_admin:
            # Platform admins have access to all platform endpoints
            logger.debug(f"User {current_user.id} is platform admin, allowing access")
            return current_user
        
        # Use the unified check_permission function which handles all scopes
        has_permission = await check_permission(
            current_user,
            permission_slug,
            None,  # business_unit_id - not needed for platform/user scopes
            db,
            enforcer
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_slug} required"
            )
        return current_user
    return dependency


async def get_user_platform_roles(
    user: User,
    db: AsyncSession,
    enforcer: Enforcer,
    org_domain: str
) -> List[str]:
    """
    Get user's platform-level roles (not BU-scoped).
    Platform roles are roles where is_platform_role = True.
    """
    from app.models.rbac import Role
    
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


async def get_bu_membership(
    user_id: uuid.UUID,
    business_unit_id: uuid.UUID,
    db: AsyncSession
):
    """
    Get user's membership in a specific business unit with role.
    Returns first BusinessUnitMember if user is a member, None otherwise.
    Note: A user can have multiple roles in a BU, so we return the first one.
    """
    from app.models.business_unit import BusinessUnitMember
    
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
    business_unit_id: uuid.UUID,
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
    business_unit_id: uuid.UUID,
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
    from app.logger import logger
    
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
    # OrgAwareEnforcer.enforce() expects 3 args: (sub, obj, act) and injects org_domain automatically
    # MultiTenantEnforcerWrapper.enforce() accepts either:
    # - 2 args: (sub, obj, act) - injects org_domain automatically
    # - 3 args: (sub, dom, obj, act) - uses provided domain
    # Base Casbin enforcer expects 4 args: (sub, dom, obj, act)
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
    # Permission check completed
    
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
        # Global permission check completed
        
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


def is_allowed_bu(permission_slug: str, require_bu: bool = True):
    """
    Dependency for checking BU-scoped permissions.
    
    Handles three permission scopes:
    - Platform-level: Checks platform roles only (no BU required)
    - Business Unit-level: Requires active BU, checks BU membership and role
    - User-level: Checks user's roles (no BU required)
    
    Args:
        permission_slug: Permission to check (e.g., "deployments:create")
        require_bu: If True, requires active business unit for BU-scoped permissions.
                    If False, allows platform-level permissions without BU.
    """
    async def dependency(
        current_user: User = Depends(get_current_user),
        business_unit_id: Optional[uuid.UUID] = Depends(get_active_business_unit),
        enforcer: Enforcer = Depends(get_enforcer),
        db: AsyncSession = Depends(get_db)
    ):
        from app.core.permission_registry import (
            get_permission_scope,
            is_platform_permission,
            is_bu_permission,
            parse_permission_slug
        )
        
        # Parse permission
        try:
            obj, act = parse_permission_slug(permission_slug)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid permission slug: {permission_slug}"
            )
        
        # Get organization domain
        organization = await get_user_organization(current_user, db)
        org_domain = get_organization_domain(organization)
        user_id = str(current_user.id)
        
        # Check permission scope
        scope = get_permission_scope(permission_slug)
        
        if scope == "platform":
            # Platform permission: Check platform roles only
            platform_roles = await get_user_platform_roles(current_user, db, enforcer, org_domain)
            has_permission = False
            for role in platform_roles:
                if enforcer.enforce(role, org_domain, obj, act):
                    has_permission = True
                    break
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_slug} required (platform-level)"
                )
            return current_user
        
        elif scope == "business_unit":
            # BU permission: Require active BU
            if require_bu and not business_unit_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Business unit context required for this action"
                )
            
            if not business_unit_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_slug} requires a business unit context"
                )
            
            # Check BU membership
            membership = await get_bu_membership(current_user.id, business_unit_id, db)
            if not membership:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not a member of this business unit"
                )
            
            # Ensure role relationship is loaded (refresh to avoid lazy loading issues)
            if membership.role_id:
                await db.refresh(membership, ["role"])
                # If role is still None after refresh, try to load it directly
                if not membership.role:
                    from sqlalchemy.future import select
                    from app.models.rbac import Role
                    role_result = await db.execute(
                        select(Role).where(Role.id == membership.role_id)
                    )
                    role_obj = role_result.scalar_one_or_none()
                    if role_obj:
                        # Manually set the role on the membership object
                        membership.role = role_obj
            
            # Get user's role in this BU
            role = membership.role
            if not role:
                # Role might have been deleted or is orphaned
                # Check if role_id exists but role object is None
                if membership.role_id:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Role not found for business unit membership. Role ID {membership.role_id} does not exist in the roles table."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have a role assigned in this business unit. Please contact a business unit administrator."
                    )
            
            from app.logger import logger
            logger.info(f"Checking permission '{permission_slug}' for user {current_user.email} with role '{role.name}' in BU {business_unit_id}")
            
            # Check permission for this role in BU context
            # Format: (role, org_domain, bu:{bu_id}:resource, action)
            bu_obj = f"bu:{business_unit_id}:{obj}"
            has_permission = enforcer.enforce(role.name, org_domain, bu_obj, act)
            # Permission check completed
            
            # If permission doesn't exist, try to create it
            if not has_permission:
                from app.logger import logger
                # First check if the role has this permission globally (without BU context)
                global_has_permission = enforcer.enforce(role.name, org_domain, obj, act)
                
                if global_has_permission:
                    # Role has permission globally, create BU-scoped version
                    logger.info(f"Role '{role.name}' has global permission '{permission_slug}', creating BU-scoped version")
                    enforcer.add_policy(role.name, org_domain, bu_obj, act)
                    enforcer.save_policy()
                    has_permission = enforcer.enforce(role.name, org_domain, bu_obj, act)
                    if has_permission:
                        logger.info(f"Successfully created BU-scoped permission for role '{role.name}': {bu_obj}:{act}")
                    else:
                        logger.warning(f"Failed to create BU-scoped permission for role '{role.name}': {bu_obj}:{act}")
                else:
                    # Try to create from default role permissions
                    from app.core.migrate_casbin_policies import create_default_bu_role_permissions
                    try:
                        logger.info(f"Creating BU-scoped permissions for role '{role.name}' in BU {business_unit_id} for permission {permission_slug}")
                        await create_default_bu_role_permissions(role.name, business_unit_id, org_domain, enforcer)
                        enforcer.save_policy()
                        # Check again after creating permissions
                        has_permission = enforcer.enforce(role.name, org_domain, bu_obj, act)
                        if has_permission:
                            logger.info(f"Successfully created and verified BU permission for role '{role.name}': {bu_obj}:{act}")
                    except Exception as e:
                        logger.error(f"Failed to create default BU permissions for role {role.name} in BU {business_unit_id}: {e}", exc_info=True)
            
            # Fallback: Check without BU prefix (for backward compatibility during migration)
            if not has_permission:
                has_permission = enforcer.enforce(role.name, org_domain, obj, act)
            
            if not has_permission:
                # Check if role has the permission globally to provide better error message
                global_has = enforcer.enforce(role.name, org_domain, obj, act)
                if global_has:
                    # Role has permission globally but not in BU context - this shouldn't happen
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied: {permission_slug} required in business unit context. Role '{role.name}' has this permission globally but not in business unit context. Please contact an administrator."
                    )
                else:
                    # Role doesn't have permission at all
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied: {permission_slug} required in business unit context. Your role '{role.name}' does not have this permission. Please contact a business unit administrator to assign you a role with this permission."
                    )
            return current_user
        
        else:  # user scope
            # User-specific permissions (profile, etc.)
            # Check if user has any role with this permission
            user_roles = enforcer.get_roles_for_user(user_id, org_domain)
            has_permission = False
            for role in user_roles:
                if enforcer.enforce(role, org_domain, obj, act):
                    has_permission = True
                    break
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_slug} required"
                )
            return current_user
    
    return dependency


def is_allowed_platform(permission_slug: str):
    """
    Dependency for checking platform-level permissions.
    These permissions do NOT require a business unit context.
    Only checks platform roles (is_platform_role = True).
    """
    async def dependency(
        current_user: User = Depends(get_current_user),
        enforcer: Enforcer = Depends(get_enforcer),
        db: AsyncSession = Depends(get_db)
    ):
        from app.core.permission_registry import (
            get_permission_scope,
            parse_permission_slug
        )
        
        # Ensure this is a platform permission
        scope = get_permission_scope(permission_slug)
        if scope != "platform":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Permission {permission_slug} is not a platform-level permission"
            )
        
        # Parse permission
        try:
            obj, act = parse_permission_slug(permission_slug)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid permission slug: {permission_slug}"
            )
        
        # Get organization domain
        organization = await get_user_organization(current_user, db)
        org_domain = get_organization_domain(organization)
        
        # Check platform roles only
        platform_roles = await get_user_platform_roles(current_user, db, enforcer, org_domain)
        has_permission = False
        for role in platform_roles:
            if enforcer.enforce(role, org_domain, obj, act):
                has_permission = True
                break
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_slug} required (platform-level)"
            )
        return current_user
    
    return dependency


async def get_org_domain(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    Dependency to get organization domain for current user.
    Use this in endpoints that need organization context for Casbin enforcement.
    """
    organization = await get_user_organization(current_user, db)
    return get_organization_domain(organization)


class OrgAwareEnforcer:
    """
    Wrapper that automatically injects organization domain into enforcement checks.
    Use this as a dependency in endpoints to get automatic multi-tenant enforcement.
    """
    def __init__(self, enforcer, org_domain: str):
        self._enforcer = enforcer
        self._org_domain = org_domain
        # If the underlying enforcer is a MultiTenantEnforcerWrapper, set its org_domain
        if hasattr(enforcer, 'set_org_domain'):
            enforcer.set_org_domain(org_domain)
    
    def enforce(self, user_id: str, resource: str, action: str) -> bool:
        """3-param enforce that automatically adds org_domain"""
        # MultiTenantEnforcerWrapper expects (sub, obj, act) and injects org_domain itself
        # So we pass (user_id, resource, action) and it will add org_domain
        if hasattr(self._enforcer, '_org_domain'):
            # It's a MultiTenantEnforcerWrapper - use 3-param format (sub, obj, act)
            # The wrapper will inject org_domain automatically
            return self._enforcer.enforce(user_id, resource, action)
        elif hasattr(self._enforcer, 'enforce'):
            # It's a base Casbin enforcer - use 4-param format (sub, dom, obj, act)
            return self._enforcer.enforce(user_id, self._org_domain, resource, action)
        else:
            # Fallback - try direct call
            return self._enforcer.enforce(user_id, self._org_domain, resource, action)
    
    def has_grouping_policy(self, user_id: str, role: str) -> bool:
        """2-param has_grouping_policy that automatically adds org_domain"""
        return self._enforcer.has_grouping_policy(user_id, role, self._org_domain)
    
    def add_grouping_policy(self, user_id: str, role: str) -> bool:
        """2-param add_grouping_policy that automatically adds org_domain"""
        return self._enforcer.add_grouping_policy(user_id, role, self._org_domain)
    
    def add_policy(self, subject: str, resource: str, action: str) -> bool:
        """3-param add_policy that automatically adds org_domain"""
        return self._enforcer.add_policy(subject, self._org_domain, resource, action)
    
    def remove_policy(self, subject: str, resource: str, action: str) -> bool:
        """3-param remove_policy that automatically adds org_domain"""
        return self._enforcer.remove_policy(subject, self._org_domain, resource, action)
    
    def remove_grouping_policy(self, user_id: str, role: str) -> bool:
        """2-param remove_grouping_policy that automatically adds org_domain"""
        return self._enforcer.remove_grouping_policy(user_id, role, self._org_domain)
    
    def get_roles_for_user(self, user_id: str) -> list:
        """
        Get roles for user within the organization domain.
        Includes both direct role assignments and roles through groups.
        """
        # Ensure the underlying enforcer has org_domain set if it's a wrapper
        if hasattr(self._enforcer, 'set_org_domain'):
            self._enforcer.set_org_domain(self._org_domain)
        
        # Use the wrapper's get_roles_for_user which handles group inheritance
        if hasattr(self._enforcer, 'get_roles_for_user'):
            # Pass domain explicitly to ensure correct domain is used
            return self._enforcer.get_roles_for_user(user_id, self._org_domain)
        # Fallback to direct call
        try:
            # Try implicit roles first (handles groups)
            implicit_roles = self._enforcer.get_implicit_roles_for_user(user_id, self._org_domain)
            # Extract role names from implicit roles
            roles = []
            for role_info in implicit_roles:
                if isinstance(role_info, (list, tuple)) and len(role_info) > 0:
                    roles.append(role_info[0])
                else:
                    roles.append(role_info)
            return list(set(roles))
        except Exception:
            # Fallback to direct roles only
            try:
                return self._enforcer.get_roles_for_user(user_id, self._org_domain)
            except Exception:
                return []
    
    def get_users_for_role(self, role: str) -> list:
        """Get users for role within the organization domain"""
        return self._enforcer.get_users_for_role(role, self._org_domain)
    
    def get_all_roles(self) -> list:
        """Get all roles within the organization domain"""
        # Access the base enforcer (unwrap if necessary)
        base_enforcer = self._enforcer
        if hasattr(self._enforcer, 'enforcer'):
            base_enforcer = self._enforcer.enforcer
        
        # Get all grouping policies and extract unique roles for this org
        all_grouping = base_enforcer.get_grouping_policy()
        roles = set()
        for policy in all_grouping:
            # Format: [user/group, role, domain]
            if len(policy) >= 3 and policy[2] == self._org_domain:
                roles.add(policy[1])  # role is at index 1
        return list(roles)
    
    def get_permissions_for_user(self, user_id: str) -> list:
        """Get permissions for user within the organization domain"""
        return self._enforcer.get_permissions_for_user(user_id, self._org_domain)
    
    def get_implicit_permissions_for_user(self, user_id: str) -> list:
        """Get all permissions (direct and inherited) for user within the organization domain"""
        return self._enforcer.get_implicit_permissions_for_user(user_id, self._org_domain)
    
    def delete_roles_for_user(self, user_id: str) -> bool:
        """Delete all roles for user within the organization domain"""
        try:
            # Access the base enforcer (unwrap if necessary)
            base_enforcer = self._enforcer
            if hasattr(self._enforcer, 'enforcer'):
                base_enforcer = self._enforcer.enforcer
            
            # Get all grouping policies for this user
            grouping_policies = base_enforcer.get_filtered_grouping_policy(0, user_id)
            removed = False
            
            # Remove all grouping policies for this user in this organization domain
            for policy in grouping_policies:
                # Format: [user_id, role, domain] or [user_id, role]
                if len(policy) >= 3:
                    # Multi-tenant format: check if domain matches
                    if policy[2] == self._org_domain:
                        base_enforcer.remove_grouping_policy(*policy)
                        removed = True
                elif len(policy) == 2:
                    # Old format: remove it (will be re-added with domain if needed)
                    base_enforcer.remove_grouping_policy(*policy)
                    removed = True
            
            # Save the policy changes
            if removed:
                base_enforcer.save_policy()
            
            return removed
        except Exception as e:
            import logging
            logging.warning(f"Failed to delete roles for user {user_id}: {e}")
            return False
    
    def delete_role(self, role: str) -> bool:
        """Delete a role within the organization domain"""
        return self._enforcer.delete_role(role, self._org_domain)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete all policies and grouping policies for a user within the organization domain"""
        result = False
        
        try:
            # Access the base enforcer (unwrap if necessary)
            base_enforcer = self._enforcer
            if hasattr(self._enforcer, 'enforcer'):
                base_enforcer = self._enforcer.enforcer
            
            # Delete all role assignments (grouping policies) for the user in this organization
            # Get all grouping policies for this user
            grouping_policies = base_enforcer.get_filtered_grouping_policy(0, user_id)
            for policy in grouping_policies:
                # Only delete if it's in this organization domain
                if len(policy) >= 3 and policy[2] == self._org_domain:
                    base_enforcer.remove_grouping_policy(*policy)
                    result = True
            
            # Delete all direct permissions (policies) for the user in this organization
            policies = base_enforcer.get_filtered_policy(0, user_id, self._org_domain)
            for policy in policies:
                base_enforcer.remove_policy(*policy)
                result = True
            
            # Save the policy changes
            if result:
                base_enforcer.save_policy()
        except Exception as e:
            # Log the error but don't fail the deletion
            import logging
            logging.warning(f"Failed to clean up Casbin policies for user {user_id}: {e}")
            # Continue with user deletion even if Casbin cleanup fails
        
        return True  # Always return True to allow user deletion to proceed
    
    def delete_permission(self, *params) -> bool:
        """Delete a permission within the organization domain"""
        # Auto-inject org_domain if needed
        if len(params) == 2:  # resource, action
            return self._enforcer.delete_permission(self._org_domain, params[0], params[1])
        else:
            return self._enforcer.delete_permission(*params)
    
    def get_policy(self) -> list:
        """Get all policies"""
        # Access the base enforcer (unwrap if necessary)
        base_enforcer = self._enforcer
        if hasattr(self._enforcer, 'enforcer'):
            base_enforcer = self._enforcer.enforcer
        return base_enforcer.get_policy()
    
    def get_filtered_policy(self, field_index: int, *field_values) -> list:
        """Get filtered policies"""
        # Access the base enforcer (unwrap if necessary)
        base_enforcer = self._enforcer
        if hasattr(self._enforcer, 'enforcer'):
            base_enforcer = self._enforcer.enforcer
        return base_enforcer.get_filtered_policy(field_index, *field_values)
    
    def get_grouping_policy(self) -> list:
        """Get all grouping policies"""
        # Access the base enforcer (unwrap if necessary)
        base_enforcer = self._enforcer
        if hasattr(self._enforcer, 'enforcer'):
            base_enforcer = self._enforcer.enforcer
        return base_enforcer.get_grouping_policy()
    
    def get_filtered_grouping_policy(self, field_index: int, *field_values) -> list:
        """Get filtered grouping policies"""
        # Access the base enforcer (unwrap if necessary)
        base_enforcer = self._enforcer
        if hasattr(self._enforcer, 'enforcer'):
            base_enforcer = self._enforcer.enforcer
        return base_enforcer.get_filtered_grouping_policy(field_index, *field_values)
    
    def remove_filtered_policy(self, field_index: int, *field_values) -> bool:
        """Remove filtered policies"""
        # Access the base enforcer (unwrap if necessary)
        base_enforcer = self._enforcer
        if hasattr(self._enforcer, 'enforcer'):
            base_enforcer = self._enforcer.enforcer
        return base_enforcer.remove_filtered_policy(field_index, *field_values)
    
    def remove_filtered_grouping_policy(self, field_index: int, *field_values) -> bool:
        """Remove filtered grouping policies"""
        # Access the base enforcer (unwrap if necessary)
        base_enforcer = self._enforcer
        if hasattr(self._enforcer, 'enforcer'):
            base_enforcer = self._enforcer.enforcer
        return base_enforcer.remove_filtered_grouping_policy(field_index, *field_values)
    
    def load_policy(self):
        """Delegate to underlying enforcer"""
        return self._enforcer.load_policy()
    
    def save_policy(self):
        """Delegate to underlying enforcer"""
        return self._enforcer.save_policy()


async def get_org_aware_enforcer(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OrgAwareEnforcer:
    """
    Get an organization-aware enforcer that automatically injects org_domain.
    
    This allows existing code to work without changes:
    - enforcer.enforce(user_id, "resource", "action") -> automatically adds org_domain
    - enforcer.has_grouping_policy(user_id, "role") -> automatically adds org_domain
    - etc.
    
    Use this dependency in new endpoints or replace Depends(get_enforcer) with this.
    """
    from app.core.casbin import get_enforcer
    base_enforcer = get_enforcer()
    org_domain = await get_org_domain(current_user, db)
    return OrgAwareEnforcer(base_enforcer, org_domain)


async def get_active_business_unit(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Optional[uuid.UUID]:
    """
    Dependency to get active business unit ID from request headers or query params.
    Validates that user has access to the business unit.
    Returns None if no business unit is specified or user doesn't have access.
    
    Usage in endpoints:
    - Header: X-Business-Unit-Id
    - Query param: business_unit_id
    """
    from app.models.business_unit import BusinessUnitMember
    
    # Try header first, then query param
    business_unit_id_str = request.headers.get("X-Business-Unit-Id") or request.query_params.get("business_unit_id")
    
    if not business_unit_id_str:
        return None
    
    try:
        business_unit_uuid = uuid.UUID(business_unit_id_str)
    except (ValueError, TypeError):
        return None
    
    # Validate user has access to this business unit
    # A user can have multiple roles in a BU, so we get all memberships
    result = await db.execute(
        select(BusinessUnitMember).where(
            BusinessUnitMember.business_unit_id == business_unit_uuid,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = result.scalars().all()
    membership = memberships[0] if memberships else None
    
    if not membership:
        # Check if user is super admin (they can access all business units)
        from app.core.casbin import get_enforcer
        enforcer = get_enforcer()
        org_domain = await get_org_domain(current_user, db)
        is_admin = await is_platform_admin(current_user, db, enforcer)
        if is_admin:
            return business_unit_uuid
        return None
    
    return business_unit_uuid


async def require_business_unit(
    business_unit_id: Optional[uuid.UUID] = Depends(get_active_business_unit),
    current_user: User = Depends(get_current_user)
) -> uuid.UUID:
    """
    Dependency that requires a business unit to be selected.
    Raises 400 error if no business unit is selected.
    """
    if business_unit_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business unit must be selected. Please select a business unit from the header dropdown."
        )
    return business_unit_id
