from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_active_superuser, is_allowed, get_db, OrgAwareEnforcer, get_org_aware_enforcer
from app.schemas.rbac import RoleCreate, RoleUpdate, RoleResponse, PermissionResponse
from app.models.rbac import Role, PermissionMetadata
from app.core.permission_registry import parse_permission_slug, get_permission, find_permission_by_resource_action
from uuid import uuid4, UUID
from datetime import datetime

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/")
async def list_roles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    enforcer: OrgAwareEnforcer = Depends(get_org_aware_enforcer),
    current_user = Depends(is_allowed("platform:roles:list"))
):
    """
    List all roles from DB and their permissions from Casbin with pagination.
    """
    from sqlalchemy import func
    
    # Get total count
    count_result = await db.execute(select(func.count(Role.id)))
    total = count_result.scalar() or 0
    
    # Fetch roles with pagination
    result = await db.execute(select(Role).offset(skip).limit(limit))
    roles_db = result.scalars().all()
    
    # Get metadata from database (gracefully handle if table doesn't exist yet)
    db_metadata = {}
    try:
        result_meta = await db.execute(select(PermissionMetadata))
        db_metadata = {perm.slug: perm for perm in result_meta.scalars().all()}
    except Exception:
        # Table doesn't exist yet - will use registry metadata only
        pass
    
    response = []
    for role in roles_db:
        # Get permissions for this role from Casbin
        # Multi-tenant format: [role, domain, obj, act] (4 elements)
        # New format: obj="deployments", act="create:development" -> slug="deployments:create:development"
        role_policies = enforcer.get_filtered_policy(0, role.name)
        permissions = []
        for policy in role_policies:
            if len(policy) >= 4:
                # Multi-tenant format: role is at index 0, domain at 1, obj at 2, act at 3
                # NEW: obj now includes scope (e.g., "platform:groups" instead of just "groups")
                obj = policy[2]
                act = policy[3]
                
                # Try to find the full permission slug from registry
                # obj may be in new format (scope:resource) or old format (resource)
                perm_def = find_permission_by_resource_action(obj, act)
                if perm_def:
                    perm_slug = perm_def["slug"]  # Use full slug from registry
                else:
                    # Fallback: construct slug from obj and act
                    # If obj doesn't have scope, try to construct it
                    if ":" in obj:
                        perm_slug = f"{obj}:{act}"
                    else:
                        # Old format - try to find scope from context or use as-is
                        perm_slug = f"{obj}:{act}"
                    perm_def = get_permission(perm_slug)
                
                db_perm = db_metadata.get(perm_slug)
                
                permissions.append(PermissionResponse(
                    id=db_perm.id if db_perm else None,
                    slug=perm_slug,
                    name=perm_def.get("name") if perm_def else None,
                    description=perm_def.get("description") if perm_def else None,
                    category=perm_def.get("category") if perm_def else None,
                    resource=perm_def.get("resource") if perm_def else None,
                    action=perm_def.get("action") if perm_def else None,
                    environment=perm_def.get("environment") if perm_def else None,
                    icon=perm_def.get("icon") if perm_def else None,
                    created_at=db_perm.created_at if db_perm else None
                ))
            elif len(policy) >= 3:
                # Old format: role is at index 0, obj at 1, act at 2
                # NEW: obj now includes scope (e.g., "platform:groups" instead of just "groups")
                obj = policy[1]
                act = policy[2]
                
                # Try to find the full permission slug from registry
                perm_def = find_permission_by_resource_action(obj, act)
                if perm_def:
                    perm_slug = perm_def["slug"]  # Use full slug from registry
                else:
                    # Fallback: construct slug from obj and act
                    if ":" in obj:
                        perm_slug = f"{obj}:{act}"
                    else:
                        perm_slug = f"{obj}:{act}"
                    perm_def = get_permission(perm_slug)
                
                db_perm = db_metadata.get(perm_slug)
                
                permissions.append(PermissionResponse(
                    id=db_perm.id if db_perm else None,
                    slug=perm_slug,
                    name=perm_def.get("name") if perm_def else None,
                    description=perm_def.get("description") if perm_def else None,
                    category=perm_def.get("category") if perm_def else None,
                    resource=perm_def.get("resource") if perm_def else None,
                    action=perm_def.get("action") if perm_def else None,
                    environment=perm_def.get("environment") if perm_def else None,
                    icon=perm_def.get("icon") if perm_def else None,
                    created_at=db_perm.created_at if db_perm else None
                ))
        
        response.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_platform_role=role.is_platform_role,
            created_at=role.created_at,
            permissions=permissions
        ))
    
    return {
        "items": response,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/", response_model=RoleResponse)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    enforcer: OrgAwareEnforcer = Depends(get_org_aware_enforcer),
    current_user = Depends(is_allowed("platform:roles:create"))
):
    """
    Create a new role in DB and Casbin.
    """
    # Check if role exists in DB
    result = await db.execute(select(Role).where(Role.name == role_in.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Role already exists")
    
    # Create in DB
    role = Role(
        name=role_in.name, 
        description=role_in.description,
        is_platform_role=role_in.is_platform_role
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    # Add permissions in Casbin using new format parser
    if role_in.permissions:
        for perm_slug in role_in.permissions:
            obj, act = parse_permission_slug(perm_slug)
            enforcer.add_policy(role.name, obj, act)
        # Save policies to persist changes
        enforcer.save_policy()
    
    # Get metadata for response (gracefully handle if table doesn't exist yet)
    db_metadata = {}
    try:
        result_meta = await db.execute(select(PermissionMetadata))
        db_metadata = {perm.slug: perm for perm in result_meta.scalars().all()}
    except Exception:
        # Table doesn't exist yet - will use registry metadata only
        pass
    
    # Construct response with enriched metadata
    permissions = []
    for perm_slug in role_in.permissions:
        perm_def = get_permission(perm_slug)
        db_perm = db_metadata.get(perm_slug)
        
        permissions.append(PermissionResponse(
            id=db_perm.id if db_perm else None,
            slug=perm_slug,
            name=perm_def.get("name") if perm_def else None,
            description=perm_def.get("description") if perm_def else None,
            category=perm_def.get("category") if perm_def else None,
            resource=perm_def.get("resource") if perm_def else None,
            action=perm_def.get("action") if perm_def else None,
            environment=perm_def.get("environment") if perm_def else None,
            icon=perm_def.get("icon") if perm_def else None,
            created_at=db_perm.created_at if db_perm else None
        ))

    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_platform_role=role.is_platform_role,
        created_at=role.created_at,
        permissions=permissions
    )

@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    enforcer: OrgAwareEnforcer = Depends(get_org_aware_enforcer),
    current_user = Depends(is_allowed("platform:roles:update"))
):
    """
    Update a role in DB and Casbin.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    old_name = role.name
    
    # Update DB
    if role_in.name:
        role.name = role_in.name
    if role_in.description is not None:
        role.description = role_in.description
    if role_in.is_platform_role is not None:
        role.is_platform_role = role_in.is_platform_role
        
    await db.commit()
    await db.refresh(role)
    
    # Update Casbin
    # If name changed, we have a problem with existing policies.
    # For now, assume name doesn't change or we need to migrate policies.
    # But permissions might change.
    
    if role_in.permissions is not None:
        # Get organization domain for proper policy removal
        from app.core.organization import get_user_organization, get_organization_domain
        from app.logger import logger
        org = await get_user_organization(current_user, db)
        org_domain = get_organization_domain(org)
        
        logger.info(f"Updating role '{role.name}' (old name: '{old_name}') with {len(role_in.permissions)} permissions in org domain '{org_domain}'")
        logger.info(f"Permission slugs received: {role_in.permissions}")
        
        # Get count of old policies before removal
        old_policies = enforcer.get_filtered_policy(0, old_name, org_domain)
        old_count = len(old_policies) if old_policies else 0
        logger.info(f"Found {old_count} existing policies for role '{old_name}' in domain '{org_domain}'")
        
        # Remove old permissions for this role in this organization domain
        # Policies are stored as [role_name, org_domain, obj, act]
        # Use remove_filtered_policy to remove all policies matching role_name and org_domain
        removed_result = enforcer.remove_filtered_policy(0, old_name, org_domain)
        logger.info(f"remove_filtered_policy returned: {removed_result}")
        
        # Reload policies after removal to ensure they're cleared from memory
        enforcer.load_policy()
        
        # Verify removal worked
        remaining_old = enforcer.get_filtered_policy(0, old_name, org_domain)
        if remaining_old:
            logger.warning(f"Warning: {len(remaining_old)} old policies still exist after removal. Attempting manual removal...")
            # Access base enforcer to manually remove remaining policies
            base_enforcer = enforcer._enforcer
            if hasattr(enforcer._enforcer, 'enforcer'):
                base_enforcer = enforcer._enforcer.enforcer
            for policy in remaining_old:
                base_enforcer.remove_policy(*policy)
            enforcer.load_policy()
        
        # All permissions are now unique (scope included in object name)
        # No deduplication needed - just add all permissions
        logger.info(f"Adding {len(role_in.permissions)} permissions to role '{role.name}'")
        
        # Add new permissions using new format parser (scope included in obj)
        added_count = 0
        failed_count = 0
        skipped_count = 0
        for perm_slug in role_in.permissions:
            try:
                obj, act = parse_permission_slug(perm_slug)
                # Check if policy already exists (shouldn't after removal, but check anyway)
                existing = enforcer.get_filtered_policy(0, role.name, org_domain, obj, act)
                if existing:
                    logger.debug(f"Policy already exists for slug '{perm_slug}' -> obj='{obj}', act='{act}', skipping")
                    skipped_count += 1
                    continue
                
                result = enforcer.add_policy(role.name, obj, act)
                if result:
                    added_count += 1
                    logger.info(f"Added policy: role='{role.name}', obj='{obj}', act='{act}' (from slug '{perm_slug}')")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to add policy for slug '{perm_slug}' -> obj='{obj}', act='{act}' (add_policy returned False)")
            except Exception as e:
                failed_count += 1
                logger.error(f"Error parsing/adding permission slug '{perm_slug}': {e}", exc_info=True)
        
        logger.info(f"Added {added_count} policies, {failed_count} failed for role '{role.name}'")
        
        # Save policies to persist changes
        save_result = enforcer.save_policy()
        logger.info(f"Policy save result: {save_result}")
        
        # Verify policies were saved by reloading and checking
        enforcer.load_policy()
        saved_policies = enforcer.get_filtered_policy(0, role.name, org_domain)
        logger.info(f"Verified: {len(saved_policies)} policies now exist for role '{role.name}' in domain '{org_domain}'")
                
    return await get_role(role.id, db, enforcer, current_user)

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    enforcer: OrgAwareEnforcer = Depends(get_org_aware_enforcer),
    current_user = Depends(is_allowed("platform:roles:read"))
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    # Get metadata from database (gracefully handle if table doesn't exist yet)
    db_metadata = {}
    try:
        result_meta = await db.execute(select(PermissionMetadata))
        db_metadata = {perm.slug: perm for perm in result_meta.scalars().all()}
    except Exception:
        # Table doesn't exist yet - will use registry metadata only
        pass
    
    role_policies = enforcer.get_filtered_policy(0, role.name)
    permissions = []
    for policy in role_policies:
        # Multi-tenant format: [role, domain, obj, act] (4 elements)
        # New format: obj="deployments", act="create:development" -> slug="deployments:create:development"
        if len(policy) >= 4:
            # Multi-tenant format: role is at index 0, domain at 1, obj at 2, act at 3
            # NEW: obj now includes scope (e.g., "platform:groups" instead of just "groups")
            obj = policy[2]
            act = policy[3]
            
            # Try to find the full permission slug from registry
            perm_def = find_permission_by_resource_action(obj, act)
            if perm_def:
                perm_slug = perm_def["slug"]  # Use full slug from registry (e.g., "platform:users:list")
            else:
                # Fallback: construct slug from obj and act
                if ":" in obj:
                    perm_slug = f"{obj}:{act}"
                else:
                    perm_slug = f"{obj}:{act}"
                perm_def = get_permission(perm_slug)
            
            db_perm = db_metadata.get(perm_slug)
            
            permissions.append(PermissionResponse(
                id=db_perm.id if db_perm else None,
                slug=perm_slug,
                name=perm_def.get("name") if perm_def else None,
                description=perm_def.get("description") if perm_def else None,
                category=perm_def.get("category") if perm_def else None,
                resource=perm_def.get("resource") if perm_def else None,
                action=perm_def.get("action") if perm_def else None,
                environment=perm_def.get("environment") if perm_def else None,
                icon=perm_def.get("icon") if perm_def else None,
                created_at=db_perm.created_at if db_perm else None
            ))
        elif len(policy) >= 3:
            # Old format: role is at index 0, obj at 1, act at 2
            obj = policy[1]
            act = policy[2]
            
            # Try to find the full permission slug from registry (with scope prefix)
            perm_def = find_permission_by_resource_action(obj, act)
            if perm_def:
                perm_slug = perm_def["slug"]  # Use full slug from registry
            else:
                # Fallback to constructed slug if not found in registry
                perm_slug = f"{obj}:{act}"
                perm_def = get_permission(perm_slug)
            
            db_perm = db_metadata.get(perm_slug)
            
            permissions.append(PermissionResponse(
                id=db_perm.id if db_perm else None,
                slug=perm_slug,
                name=perm_def.get("name") if perm_def else None,
                description=perm_def.get("description") if perm_def else None,
                category=perm_def.get("category") if perm_def else None,
                resource=perm_def.get("resource") if perm_def else None,
                action=perm_def.get("action") if perm_def else None,
                environment=perm_def.get("environment") if perm_def else None,
                icon=perm_def.get("icon") if perm_def else None,
                created_at=db_perm.created_at if db_perm else None
            ))
            
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_platform_role=role.is_platform_role,
        created_at=role.created_at,
        permissions=permissions
    )

@router.delete("/{role_id}")
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    enforcer: OrgAwareEnforcer = Depends(get_org_aware_enforcer),
    current_user = Depends(is_allowed("platform:roles:delete"))
):
    """
    Delete a role from DB and Casbin.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Remove from Casbin
    enforcer.remove_filtered_policy(0, role.name)
    # Remove grouping policies (where role is used)
    enforcer.remove_filtered_grouping_policy(1, role.name)
    
    await db.delete(role)
    await db.commit()
    
    return {"message": "Role deleted successfully"}
