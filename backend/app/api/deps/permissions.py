"""Permission checking dependencies"""
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from casbin import Enforcer

from app.database import get_db
from app.models.rbac import User
from app.core.casbin import get_enforcer
from app.core.organization import get_user_organization, get_organization_domain
from app.core.authorization import check_permission
from app.core.permission_registry import parse_permission_slug, get_permission_scope
from app.logger import logger
from .auth import get_current_user
from .helpers import is_platform_admin, get_user_platform_roles, get_bu_membership
from .business_unit import get_active_business_unit


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
        request: Request,
        current_user: User = Depends(get_current_user),
        business_unit_id: Optional[UUID] = Depends(get_active_business_unit),
        enforcer: Enforcer = Depends(get_enforcer),
        db: AsyncSession = Depends(get_db)
    ):
        
        from app.core.permission_registry import (
            get_permission_scope,
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
            
            logger.info(f"Checking permission '{permission_slug}' for user {current_user.email} with role '{role.name}' in BU {business_unit_id}")
            
            # Check permission for this role in BU context
            # Format: (role, org_domain, bu:{bu_id}:resource, action)
            bu_obj = f"bu:{business_unit_id}:{obj}"
            has_permission = enforcer.enforce(role.name, org_domain, bu_obj, act)
            # Permission check completed
            
            # If permission doesn't exist, try to create it
            if not has_permission:
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
