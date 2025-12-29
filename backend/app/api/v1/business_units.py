"""Business Units API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import List, Optional
import uuid

from app.database import get_db
from app.api.deps import get_current_user, get_org_aware_enforcer, OrgAwareEnforcer, is_allowed_bu, get_active_business_unit, is_platform_admin, is_allowed
from app.models.rbac import User
from app.models.business_unit import BusinessUnit, BusinessUnitMember
from app.models.rbac import Role
from app.schemas.business_unit import (
    BusinessUnitCreate, BusinessUnitUpdate, BusinessUnitResponse,
    BusinessUnitMemberResponse, BusinessUnitMemberAdd
)
from app.logger import logger

router = APIRouter(prefix="/business-units", tags=["Business Units"])

@router.get("", response_model=List[BusinessUnitResponse])
@router.get("/", response_model=List[BusinessUnitResponse])
async def list_business_units(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all business units the current user has access to.
    Also ensures existing owners have the necessary permissions.
    """
    # Grant permissions to existing owners who might not have them yet
    from app.core.casbin import get_enforcer
    from app.core.organization import get_user_organization, get_organization_domain
    organization = await get_user_organization(current_user, db)
    org_domain = get_organization_domain(organization)
    enforcer = get_enforcer()
    enforcer.set_org_domain(org_domain)  # Set org domain for the wrapper
    
    # Check if current user has business_units:manage_members permission in any business unit
    # This is permission-based, not role-name-based
    from app.api.deps import check_bu_permission
    
    # Get all business units where user is a member
    all_memberships_result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(BusinessUnitMember.user_id == current_user.id)
    )
    all_memberships = all_memberships_result.scalars().all()
    
    # Filter memberships where user has manage_members permission
    owner_memberships = []
    for membership in all_memberships:
        has_permission = await check_bu_permission(
            current_user,
            membership.business_unit_id,
            "business_unit:business_units:manage_members",
            db,
            enforcer,
            org_domain
        )
        if has_permission:
            owner_memberships.append(membership)
    
    # Grant permissions to existing members with manage_members permission
    if owner_memberships:
        # Get user's existing roles once (outside the loop)
        user_roles = enforcer.get_roles_for_user(str(current_user.id))
        roles_updated = False
        
        # Grant platform permissions to roles that have business_units:manage_members
        # This is permission-based, not role-name-based
        from app.core.permission_registry import parse_permission_slug
        platform_permissions = [
            "platform:roles:list",
            "platform:roles:read",
            "platform:users:list",
            "platform:users:read",
        ]
        
        # For each membership with manage_members permission, grant platform permissions to that role
        for membership in owner_memberships:
            if membership.role:
                role_name = membership.role.name
                for perm_slug in platform_permissions:
                    try:
                        obj, act = parse_permission_slug(perm_slug)
                        # Check if role already has this permission
                        existing = enforcer.get_filtered_policy(0, role_name, org_domain, obj, act)
                        if not existing:
                            enforcer.add_policy(role_name, org_domain, obj, act)
                            roles_updated = True
                            # Granted platform permission to role
                    except Exception as e:
                        logger.warning(f"Failed to add permission {perm_slug} to role {role_name}: {e}")
        
        for membership in owner_memberships:
            owner_role = f"business-unit-owner-{membership.business_unit_id}"
            # Check if user already has this role
            if not enforcer.has_grouping_policy(str(current_user.id), owner_role, org_domain):
                enforcer.add_grouping_policy(str(current_user.id), owner_role, org_domain)
                # Add permissions to the owner role
                from app.core.permission_registry import parse_permission_slug
                owner_permissions = [
                    "business_unit:business_units:update",
                    "business_unit:business_units:read",
                    "business_unit:business_units:manage_members",
                    "platform:users:list",  # Allow owners to list users when adding members
                    "platform:roles:list",  # Allow owners to list roles when adding members
                    "platform:roles:read",  # Allow owners to read role details
                ]
                for perm_slug in owner_permissions:
                    try:
                        obj, act = parse_permission_slug(perm_slug)
                        # Check if policy exists using get_filtered_policy
                        existing_policies = enforcer.get_filtered_policy(0, owner_role)
                        policy_exists = any(
                            len(p) >= 4 and p[0] == owner_role and p[1] == org_domain and p[2] == obj and p[3] == act
                            for p in existing_policies
                        )
                        if not policy_exists:
                            enforcer.add_policy(owner_role, org_domain, obj, act)
                    except Exception as e:
                        logger.warning(f"Failed to add permission {perm_slug} to owner role {owner_role}: {e}")
                roles_updated = True
                logger.info(f"Granted business unit owner permissions to {current_user.email} for business unit {membership.business_unit_id}")
        
        # Also grant platform:users:list permission directly to user's existing roles for immediate effect
        # This ensures owners can list users even if they don't have the business-unit-owner role yet
        from app.core.permission_registry import parse_permission_slug
        perm_slug = "platform:users:list"
        try:
            obj, act = parse_permission_slug(perm_slug)
            for role in user_roles:
                # Check if policy exists using get_filtered_policy
                existing_policies = enforcer.get_filtered_policy(0, role)
                policy_exists = any(
                    len(p) >= 4 and p[0] == role and p[1] == org_domain and p[2] == obj and p[3] == act
                    for p in existing_policies
                )
                if not policy_exists:
                    enforcer.add_policy(role, org_domain, obj, act)
                    roles_updated = True
            
            # Also grant permission directly to the user for immediate effect
            # This ensures the permission check works even if role-based checking has issues
            user_policies = enforcer.get_filtered_policy(0, str(current_user.id))
            user_policy_exists = any(
                len(p) >= 4 and p[0] == str(current_user.id) and p[1] == org_domain and p[2] == obj and p[3] == act
                for p in user_policies
            )
            if not user_policy_exists:
                enforcer.add_policy(str(current_user.id), org_domain, obj, act)
                roles_updated = True
        except Exception as e:
            logger.warning(f"Failed to add {perm_slug} permission: {e}")
        
        if roles_updated:
            enforcer.save_policy()
            # Reload policy to ensure changes take effect immediately
            enforcer.load_policy()
            logger.info(f"Granted platform:users:list permission to {current_user.email} (roles: {user_roles})")
    
    # Get all business units where user is a member
    result = await db.execute(
        select(BusinessUnit)
        .join(BusinessUnitMember)
        .where(
            BusinessUnitMember.user_id == current_user.id,
            BusinessUnit.is_active == True
        )
        .distinct()
    )
    business_units = result.scalars().all()
    
    # Also check if user is platform admin - admins can see all business units
    is_admin = await is_platform_admin(current_user, db, enforcer)
    
    if is_admin:
        # Admins can see all business units in their organization
        admin_result = await db.execute(
            select(BusinessUnit)
            .where(
                BusinessUnit.organization_id == current_user.organization_id,
                BusinessUnit.is_active == True
            )
        )
        admin_business_units = admin_result.scalars().all()
        # Combine and deduplicate
        all_business_units = {bu.id: bu for bu in business_units}
        for bu in admin_business_units:
            all_business_units[bu.id] = bu
        business_units = list(all_business_units.values())
    
    # Get user's role and member count for each business unit
    from sqlalchemy import func
    response_list = []
    for bu in business_units:
        member_result = await db.execute(
            select(BusinessUnitMember)
            .options(selectinload(BusinessUnitMember.role))
            .where(
                BusinessUnitMember.business_unit_id == bu.id,
                BusinessUnitMember.user_id == current_user.id
            )
        )
        memberships = member_result.scalars().all()
        membership = memberships[0] if memberships else None
        role = None
        if membership:
            # Get role name from relationship (now eagerly loaded)
            if membership.role:
                role = membership.role.name
            else:
                # Fallback: query role directly if relationship not loaded
                role_result = await db.execute(
                    select(Role).where(Role.id == membership.role_id)
                )
                role_obj = role_result.scalar_one_or_none()
                role = role_obj.name if role_obj else None
        if is_admin and not membership:
            role = "admin"  # Admins have admin role even if not explicitly members
        
        # Count total distinct members (users) in this business unit (not role assignments)
        count_result = await db.execute(
            select(func.count(func.distinct(BusinessUnitMember.user_id))).where(
                BusinessUnitMember.business_unit_id == bu.id
            )
        )
        member_count = count_result.scalar() or 0
        
        # Check if user has manage_members permission for this business unit
        can_manage = False
        if membership:
            logger.info(f"[DEBUG] Checking manage_members permission for user {current_user.email} in BU {bu.name} (id: {bu.id})")
            logger.info(f"[DEBUG] Membership role: {membership.role.name if membership.role else 'None'}, role_id: {membership.role_id}")
            can_manage = await check_bu_permission(
                current_user,
                bu.id,
                "business_unit:business_units:manage_members",
                db,
                enforcer,
                org_domain
            )
            logger.info(f"[DEBUG] Permission check result for {current_user.email} in BU {bu.name}: {can_manage}")
        elif is_admin:
            can_manage = True  # Admins can manage all business units
            logger.info(f"[DEBUG] User {current_user.email} is admin, can manage BU {bu.name}")
        
        response_list.append(BusinessUnitResponse(
            id=bu.id,
            name=bu.name,
            slug=bu.slug,
            description=bu.description,
            organization_id=bu.organization_id,
            is_active=bu.is_active,
            created_at=bu.created_at,
            updated_at=bu.updated_at,
            role=role,
            member_count=member_count,
            can_manage_members=can_manage
        ))
    
    return response_list

@router.post("", response_model=BusinessUnitResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=BusinessUnitResponse, status_code=status.HTTP_201_CREATED)
async def create_business_unit(
    business_unit: BusinessUnitCreate,
    current_user: User = Depends(is_allowed("platform:business_units:create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new business unit (super admin only)"""
    # Check if slug already exists in the same organization
    result = await db.execute(
        select(BusinessUnit).where(
            BusinessUnit.slug == business_unit.slug,
            BusinessUnit.organization_id == current_user.organization_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Business unit with slug '{business_unit.slug}' already exists in your organization"
        )
    
    # Create business unit
    new_bu = BusinessUnit(
        name=business_unit.name,
        slug=business_unit.slug,
        description=business_unit.description,
        organization_id=current_user.organization_id,
        is_active=True
    )
    db.add(new_bu)
    await db.commit()
    await db.refresh(new_bu)
    
    logger.info(f"Business unit '{new_bu.name}' created by {current_user.email}")
    
    return BusinessUnitResponse(
        id=new_bu.id,
        name=new_bu.name,
        slug=new_bu.slug,
        description=new_bu.description,
        organization_id=new_bu.organization_id,
        is_active=new_bu.is_active,
        created_at=new_bu.created_at,
        updated_at=new_bu.updated_at,
        role="admin",  # Admin who created it has admin role
        can_manage_members=True  # Admins can manage all business units
    )

@router.get("/{business_unit_id}", response_model=BusinessUnitResponse)
async def get_business_unit(
    business_unit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get business unit details"""
    # Check if user has access
    # Eagerly load role to avoid lazy loading issues
    result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = result.scalars().all()
    membership = memberships[0] if memberships else None
    
    # Check if user is super admin
    from app.core.casbin import get_enforcer
    from app.core.organization import get_user_organization, get_organization_domain
    enforcer = get_enforcer()
    organization = await get_user_organization(current_user, db)
    org_domain = get_organization_domain(organization)
    is_admin = await is_platform_admin(current_user, db, enforcer)
    
    if not membership and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this business unit"
        )
    
    # Get business unit
    bu_result = await db.execute(
        select(BusinessUnit).where(BusinessUnit.id == business_unit_id)
    )
    bu = bu_result.scalar_one_or_none()
    if not bu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business unit not found"
        )
    
    role = None
    if membership:
        if hasattr(membership.role, 'value'):
            role = membership.role.value
        elif membership.role:
            role = membership.role.name
        else:
            role = str(membership.role).lower()
    elif is_admin:
        role = "admin"
    
    # Check if user has manage_members permission
    from app.api.deps import check_bu_permission
    can_manage = False
    if membership:
        can_manage = await check_bu_permission(
            current_user,
            business_unit_id,
            "business_unit:business_units:manage_members",
            db,
            enforcer,
            org_domain
        )
    elif is_admin:
        can_manage = True  # Admins can manage all business units
    
    return BusinessUnitResponse(
        id=bu.id,
        name=bu.name,
        slug=bu.slug,
        description=bu.description,
        organization_id=bu.organization_id,
        is_active=bu.is_active,
        created_at=bu.created_at,
        updated_at=bu.updated_at,
        role=role,
        can_manage_members=can_manage
    )

@router.put("/{business_unit_id}", response_model=BusinessUnitResponse)
async def update_business_unit(
    business_unit_id: uuid.UUID,
    business_unit: BusinessUnitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a business unit (owner or admin only)"""
    # Get business unit
    result = await db.execute(
        select(BusinessUnit).where(BusinessUnit.id == business_unit_id)
    )
    bu = result.scalar_one_or_none()
    if not bu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business unit not found"
        )
    
    # Check organization
    if bu.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update business units in your organization"
        )
    
    # Check if user is owner or admin
    # Eagerly load role to avoid lazy loading issues
    member_result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = member_result.scalars().all()
    membership = memberships[0] if memberships else None
    
    from app.core.casbin import get_enforcer
    from app.core.organization import get_user_organization, get_organization_domain
    enforcer = get_enforcer()
    organization = await get_user_organization(current_user, db)
    org_domain = get_organization_domain(organization)
    is_admin = await is_platform_admin(current_user, db, enforcer)
    # Check if user has manage_members permission (permission-based, not role-name-based)
    from app.api.deps import check_bu_permission
    has_manage_permission = False
    if membership:
        has_manage_permission = await check_bu_permission(
            current_user,
            business_unit_id,
            "business_unit:business_units:manage_members",
            db,
            enforcer,
            org_domain
        )
    
    if not has_manage_permission and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business unit owners or admins can update business units"
        )
    
    # Update fields
    if business_unit.name is not None:
        bu.name = business_unit.name
    if business_unit.description is not None:
        bu.description = business_unit.description
    if business_unit.is_active is not None:
        bu.is_active = business_unit.is_active
    
    await db.commit()
    await db.refresh(bu)
    
    logger.info(f"Business unit '{bu.name}' updated by {current_user.email}")
    
    # Get user's role in the business unit
    from app.core.casbin import get_enforcer
    from app.core.organization import get_user_organization, get_organization_domain
    enforcer = get_enforcer()
    organization = await get_user_organization(current_user, db)
    org_domain = get_organization_domain(organization)
    is_admin = await is_platform_admin(current_user, db, enforcer)
    
    # Get membership to determine role
    member_result = await db.execute(
        select(BusinessUnitMember).where(
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = member_result.scalars().all()
    membership = memberships[0] if memberships else None
    role = None
    if membership:
        if hasattr(membership.role, 'value'):
            role = membership.role.value
        elif membership.role:
            role = membership.role.name
        else:
            role = str(membership.role).lower()
    elif is_admin:
        role = "admin"
    
    # Count members
    from sqlalchemy import func
    # Count total distinct members (users) in this business unit (not role assignments)
    count_result = await db.execute(
        select(func.count(func.distinct(BusinessUnitMember.user_id))).where(
            BusinessUnitMember.business_unit_id == bu.id
        )
    )
    member_count = count_result.scalar() or 0
    
    # Check if user has manage_members permission
    from app.api.deps import check_bu_permission
    can_manage = False
    if membership:
        can_manage = await check_bu_permission(
            current_user,
            business_unit_id,
            "business_unit:business_units:manage_members",
            db,
            enforcer,
            org_domain
        )
    elif is_admin:
        can_manage = True  # Admins can manage all business units
    
    return BusinessUnitResponse(
        id=bu.id,
        name=bu.name,
        slug=bu.slug,
        description=bu.description,
        organization_id=bu.organization_id,
        is_active=bu.is_active,
        created_at=bu.created_at,
        updated_at=bu.updated_at,
        role=role,
        member_count=member_count,
        can_manage_members=can_manage
    )

@router.delete("/{business_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_unit(
    business_unit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    enforcer: OrgAwareEnforcer = Depends(get_org_aware_enforcer)
):
    """Delete a business unit (platform admin or BU owner with delete permission)"""
    from app.core.authorization import check_permission
    
    # Check if user is platform admin
    is_admin = await is_platform_admin(current_user, db, enforcer.enforcer if hasattr(enforcer, 'enforcer') else enforcer)
    
    # If not platform admin, check if user has BU delete permission
    if not is_admin:
        has_delete_permission = await check_permission(
            current_user,
            "business_unit:business_units:delete",
            business_unit_id,
            db,
            enforcer.enforcer if hasattr(enforcer, 'enforcer') else enforcer
        )
        if not has_delete_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied: You do not have permission to delete this business unit"
            )
    # Get business unit
    result = await db.execute(
        select(BusinessUnit).where(BusinessUnit.id == business_unit_id)
    )
    bu = result.scalar_one_or_none()
    if not bu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business unit not found"
        )
    
    # Check organization
    if bu.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete business units in your organization"
        )
    
    # Check if there are any deployments associated with this business unit
    from app.models.deployment import Deployment
    deployments_result = await db.execute(
        select(Deployment).where(Deployment.business_unit_id == business_unit_id)
    )
    deployments = deployments_result.scalars().all()
    
    if deployments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete business unit with {len(deployments)} deployment(s). Delete or reassign deployments first."
        )
    
    # Delete the business unit (members will be cascade deleted)
    await db.delete(bu)
    await db.commit()
    
    logger.info(f"Business unit '{bu.name}' deleted by {current_user.email}")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{business_unit_id}/members", response_model=List[BusinessUnitMemberResponse])
async def list_business_unit_members(
    business_unit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List members of a business unit"""
    # Check if user has access (owner or admin)
    # Eagerly load role to avoid lazy loading issues
    # Note: A user can have multiple roles in a BU, so we get all memberships
    member_result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = member_result.scalars().all()
    membership = memberships[0] if memberships else None  # Use first membership for permission check
    
    from app.core.casbin import get_enforcer
    from app.core.organization import get_user_organization, get_organization_domain
    enforcer = get_enforcer()
    organization = await get_user_organization(current_user, db)
    org_domain = get_organization_domain(organization)
    is_admin = await is_platform_admin(current_user, db, enforcer)
    # Check if user has manage_members permission (permission-based, not role-name-based)
    from app.api.deps import check_bu_permission
    has_manage_permission = False
    if membership:
        has_manage_permission = await check_bu_permission(
            current_user,
            business_unit_id,
            "business_unit:business_units:manage_members",
            db,
            enforcer,
            org_domain
        )
    
    if not membership and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this business unit"
        )
    
    # Get all members with role relationship loaded
    result = await db.execute(
        select(BusinessUnitMember, User)
        .join(User, BusinessUnitMember.user_id == User.id)
        .where(BusinessUnitMember.business_unit_id == business_unit_id)
        .options(selectinload(BusinessUnitMember.user), selectinload(BusinessUnitMember.role))
    )
    members = result.all()
    
    return [
        BusinessUnitMemberResponse(
            id=member.id,
            business_unit_id=member.business_unit_id,
            user_id=member.user_id,
            user_email=user.email,
            user_name=user.full_name or user.username,
            role=member.role.name if member.role else "No role",
            role_id=member.role.id if member.role else None,
            created_at=member.created_at
        )
        for member, user in members
    ]

@router.post("/{business_unit_id}/members", response_model=BusinessUnitMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_business_unit_member(
    business_unit_id: uuid.UUID,
    member_data: BusinessUnitMemberAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a member to a business unit (owner or admin only)"""
    # Check if user is owner or admin
    # Eagerly load role to avoid lazy loading issues
    member_result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = member_result.scalars().all()
    membership = memberships[0] if memberships else None
    
    from app.core.casbin import get_enforcer
    from app.core.organization import get_user_organization, get_organization_domain
    enforcer = get_enforcer()
    organization = await get_user_organization(current_user, db)
    org_domain = get_organization_domain(organization)
    is_admin = await is_platform_admin(current_user, db, enforcer)
    # Check if user has manage_members permission (permission-based, not role-name-based)
    from app.api.deps import check_bu_permission
    has_manage_permission = False
    if membership:
        has_manage_permission = await check_bu_permission(
            current_user,
            business_unit_id,
            "business_unit:business_units:manage_members",
            db,
            enforcer,
            org_domain
        )
    
    if not has_manage_permission and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with 'business_unit:business_units:manage_members' permission or admins can add members"
        )
    
    # Find user by email
    user_result = await db.execute(
        select(User).where(User.email == member_data.user_email)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {member_data.user_email} not found"
        )
    
    # Get list of role IDs to assign (optional - members can be added without roles)
    role_ids_to_assign = []
    
    # Handle role_ids (new way - multiple roles)
    if member_data.role_ids and len(member_data.role_ids) > 0:
        role_ids_to_assign = member_data.role_ids
    # Handle role_id (backward compatibility - single role)
    elif member_data.role_id:
        role_ids_to_assign = [member_data.role_id]
    elif hasattr(member_data, 'role') and member_data.role:
        # role name provided (for backward compatibility)
        role_name = member_data.role.lower()
        # Map old enum values to new role names
        role_name_mapping = {
            "owner": "bu-owner",
            "member": "viewer"
        }
        role_name = role_name_mapping.get(role_name, role_name)
        
        role_result = await db.execute(
            select(Role).where(Role.name == role_name, Role.is_platform_role == False)
        )
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found or is a platform role"
            )
        role_ids_to_assign = [role.id]
    # If no roles provided, member will be added without roles (empty role_ids_to_assign is OK)
    
    # Validate all roles exist and are not platform roles
    roles_result = await db.execute(
        select(Role).where(Role.id.in_(role_ids_to_assign))
    )
    roles = roles_result.scalars().all()
    
    if len(roles) != len(role_ids_to_assign):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more roles not found"
        )
    
    for role in roles:
        if role.is_platform_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot assign platform role '{role.name}' to business unit members. Please select Business Unit roles only."
            )
    
    # Check if user is already a member
    existing_memberships_result = await db.execute(
        select(BusinessUnitMember).where(
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.user_id == user.id
        )
    )
    existing_memberships = existing_memberships_result.scalars().all()
    
    # If no roles provided and user is not a member, allow adding them without roles
    # They can assign roles later in the "Manage Roles" modal
    
    # Check which roles the user already has (to avoid duplicates)
    # Filter out None role_ids (members without roles)
    if role_ids_to_assign:
        existing_role_ids = {str(m.role_id) for m in existing_memberships if m.role_id is not None}
        new_role_ids = [role_id for role_id in role_ids_to_assign if str(role_id) not in existing_role_ids]
        
        if not new_role_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has all the specified roles in this business unit"
            )
        role_ids_to_assign = new_role_ids
    else:
        # If no roles provided, check if user is already a member (with or without role)
        if existing_memberships:
            # User is already a member, return existing
            first_member = existing_memberships[0]
            await db.refresh(first_member, ["role"])
            role_obj = first_member.role if hasattr(first_member, 'role') and first_member.role else None
            return BusinessUnitMemberResponse(
                id=first_member.id,
                business_unit_id=first_member.business_unit_id,
                user_id=first_member.user_id,
                user_email=user.email,
                user_name=user.full_name or user.username,
                role=role_obj.name if role_obj else "No role",
                role_id=role_obj.id if role_obj else None,
                created_at=first_member.created_at
            )
    
    # Create BU-scoped permissions helper
    from app.core.migrate_casbin_policies import create_default_bu_role_permissions
    from app.core.organization import get_user_organization, get_organization_domain
    from app.core.casbin import get_enforcer
    
    enforcer = get_enforcer()
    organization = await get_user_organization(user, db)
    org_domain = get_organization_domain(organization)
    
    # Add all new roles, or add member without role if no roles provided
    created_members = []
    
    if role_ids_to_assign and len(role_ids_to_assign) > 0:
        # If user is getting roles, remove any existing NULL-role membership
        # to avoid duplicate memberships that confuse permission checks
        null_role_memberships = [m for m in existing_memberships if m.role_id is None]
        for null_membership in null_role_memberships:
            await db.delete(null_membership)
            logger.info(f"Removed NULL-role membership for user {user.email} in BU {business_unit_id}")
        
        # Add roles
        for role_id in role_ids_to_assign:
            role_obj = next((r for r in roles if r.id == role_id), None)
            if not role_obj:
                continue
                
            new_member = BusinessUnitMember(
                business_unit_id=business_unit_id,
                user_id=user.id,
                role_id=role_id
            )
            db.add(new_member)
            created_members.append((new_member, role_obj))
    else:
        # Add member without role (role_id will be NULL)
        # But only if user doesn't already have any membership
        if not existing_memberships:
            new_member = BusinessUnitMember(
                business_unit_id=business_unit_id,
                user_id=user.id,
                role_id=None
            )
            db.add(new_member)
            created_members.append((new_member, None))
        else:
            # User already exists, don't create duplicate NULL membership
            first_member = existing_memberships[0]
            await db.refresh(first_member, ["role"])
            role_obj = first_member.role if hasattr(first_member, 'role') and first_member.role else None
            return BusinessUnitMemberResponse(
                id=first_member.id,
                business_unit_id=first_member.business_unit_id,
                user_id=first_member.user_id,
                user_email=user.email,
                user_name=user.full_name or user.username,
                role=role_obj.name if role_obj else "No role",
                role_id=role_obj.id if role_obj else None,
                created_at=first_member.created_at
            )
    
    await db.commit()
    
    # Refresh all created members and create permissions (only for members with roles)
    for new_member, role_obj in created_members:
        await db.refresh(new_member, ["role"])
        if role_obj:
            # Create BU-scoped role assignment: user -> composite_role (role@bu:bu_id)
            # This is needed for permission checks to work correctly
            user_id_str = str(user.id)
            bu_id_str = str(business_unit_id)
            composite_role = f"{role_obj.name}@bu:{bu_id_str}"
            
            # Check if grouping policy already exists
            existing_grouping = enforcer.get_filtered_grouping_policy(0, user_id_str)
            has_bu_role = any(
                len(p) >= 3 and p[1] == composite_role and p[2] == org_domain
                for p in existing_grouping
            )
            
            if not has_bu_role:
                enforcer.add_grouping_policy(user_id_str, composite_role, org_domain)
                logger.info(f"Added BU role assignment: {user_id_str} -> {composite_role} in {org_domain}")
            
            # IMPORTANT: Add role hierarchy so composite role inherits from base role
            # This allows Casbin to match permissions stored for the base role when user has composite role
            # Format: g, "Business Unit Owner@bu:{bu_id}", "Business Unit Owner", org_domain
            existing_hierarchy = enforcer.get_filtered_grouping_policy(0, composite_role)
            has_role_hierarchy = any(
                len(p) >= 3 and p[1] == role_obj.name and p[2] == org_domain
                for p in existing_hierarchy
            )
            
            if not has_role_hierarchy:
                enforcer.add_grouping_policy(composite_role, role_obj.name, org_domain)
                logger.info(f"Added role hierarchy: {composite_role} -> {role_obj.name} in {org_domain}")
            
            # Create default permissions for this role in this business unit
            await create_default_bu_role_permissions(role_obj.name, business_unit_id, org_domain, enforcer)
    
    enforcer.save_policy()
    
    if role_ids_to_assign and len(role_ids_to_assign) > 0:
        logger.info(f"Added {len(created_members)} role(s) to user {user.email} in business unit {business_unit_id}")
    else:
        logger.info(f"Added user {user.email} to business unit {business_unit_id} without roles")
    
    # Return the first created member (for backward compatibility with single-member response)
    if created_members:
        first_member, first_role = created_members[0]
        return BusinessUnitMemberResponse(
            id=first_member.id,
            business_unit_id=first_member.business_unit_id,
            user_id=first_member.user_id,
            user_email=user.email,
            user_name=user.full_name or user.username,
            role=first_role.name if first_role else "No role",
            role_id=first_role.id if first_role else None,
            created_at=first_member.created_at
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create member"
        )

@router.delete("/{business_unit_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_business_unit_member(
    business_unit_id: uuid.UUID,
    user_id: uuid.UUID,
    role_id: Optional[uuid.UUID] = Query(None, description="Optional: Remove specific role. If not provided, removes all roles for the user in this BU"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member (or specific role) from a business unit (owner or admin only)"""
    # Check if user is owner or admin
    # Eagerly load role to avoid lazy loading issues
    member_result = await db.execute(
        select(BusinessUnitMember)
        .options(selectinload(BusinessUnitMember.role))
        .where(
            BusinessUnitMember.business_unit_id == business_unit_id,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = member_result.scalars().all()
    membership = memberships[0] if memberships else None
    
    from app.core.casbin import get_enforcer
    from app.core.organization import get_user_organization, get_organization_domain
    enforcer = get_enforcer()
    organization = await get_user_organization(current_user, db)
    org_domain = get_organization_domain(organization)
    is_admin = await is_platform_admin(current_user, db, enforcer)
    # Check if user has manage_members permission (permission-based, not role-name-based)
    from app.api.deps import check_bu_permission
    has_manage_permission = False
    if membership:
        has_manage_permission = await check_bu_permission(
            current_user,
            business_unit_id,
            "business_unit:business_units:manage_members",
            db,
            enforcer,
            org_domain
        )
    
    if not has_manage_permission and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with 'business_unit:business_units:manage_members' permission or admins can remove members"
        )
    
    # Find and remove member(s)
    query = select(BusinessUnitMember).where(
        BusinessUnitMember.business_unit_id == business_unit_id,
        BusinessUnitMember.user_id == user_id
    )
    
    # If role_id is provided, remove only that specific role
    if role_id:
        query = query.where(BusinessUnitMember.role_id == role_id)
    
    result = await db.execute(query)
    members = result.scalars().all()
    
    if not members:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member or role not found"
        )
    
    # Get enforcer for removing Casbin policies
    enforcer.set_org_domain(org_domain)
    bu_id_str = str(business_unit_id)
    user_id_str = str(user_id)
    
    # Delete all matching memberships and remove Casbin policies
    for member in members:
        # Get the role name before deleting
        role_name = None
        if member.role_id:
            role_result = await db.execute(select(Role).where(Role.id == member.role_id))
            role_obj = role_result.scalar_one_or_none()
            if role_obj:
                role_name = role_obj.name
        
        # Delete the database record
        await db.delete(member)
        
        # Remove Casbin grouping policies for this user-role-BU combination
        if role_name:
            composite_role = f"{role_name}@bu:{bu_id_str}"
            
            # Remove user -> composite_role grouping policy (new format)
            try:
                enforcer.remove_grouping_policy(user_id_str, composite_role, org_domain)
                logger.info(f"Removed BU role assignment: {user_id_str} -> {composite_role} in {org_domain}")
            except Exception as e:
                logger.warning(f"Failed to remove grouping policy for {user_id_str} -> {composite_role}: {e}")
            
            # Also remove old format grouping policy (legacy: role-name-bu_id)
            # Convert role name to slug format: "Business Unit Owner" -> "business-unit-owner"
            role_slug = role_name.lower().replace(" ", "-")
            old_format_role = f"{role_slug}-{bu_id_str}"
            try:
                enforcer.remove_grouping_policy(user_id_str, old_format_role, org_domain)
                logger.info(f"Removed legacy BU role assignment: {user_id_str} -> {old_format_role} in {org_domain}")
            except Exception as e:
                # This is expected to fail if old format doesn't exist
                pass
            
            # Check if any other users have this composite role
            # If not, remove the role hierarchy policy too
            remaining_users = enforcer.get_users_for_role(composite_role)
            # Filter by org_domain
            remaining_in_domain = []
            for u in remaining_users:
                policies = enforcer.get_filtered_grouping_policy(0, u, composite_role)
                if any(len(p) >= 3 and p[2] == org_domain for p in policies):
                    remaining_in_domain.append(u)
            
            if not remaining_in_domain:
                # No more users with this composite role, remove the role hierarchy
                try:
                    enforcer.remove_grouping_policy(composite_role, role_name, org_domain)
                    logger.info(f"Removed role hierarchy: {composite_role} -> {role_name} in {org_domain}")
                except Exception as e:
                    logger.warning(f"Failed to remove role hierarchy for {composite_role} -> {role_name}: {e}")
            
            # Also check and remove old format role hierarchy if no users remain
            old_remaining = enforcer.get_users_for_role(old_format_role)
            old_remaining_in_domain = [u for u in old_remaining if any(
                len(p) >= 3 and p[2] == org_domain 
                for p in enforcer.get_filtered_grouping_policy(0, u, old_format_role)
            )]
            if not old_remaining_in_domain:
                try:
                    enforcer.remove_grouping_policy(old_format_role, role_name, org_domain)
                    logger.info(f"Removed legacy role hierarchy: {old_format_role} -> {role_name} in {org_domain}")
                except Exception:
                    pass
    
    # Save Casbin policy changes
    enforcer.save_policy()
    
    await db.commit()
    
    logger.info(f"Removed {len(members)} membership(s) for user {user_id} from business unit {business_unit_id}")
    
    return None

@router.post("/users/me/active-business-unit")
async def set_active_business_unit(
    business_unit_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set the active business unit for the current user"""
    if business_unit_id:
        # Validate user has access
        result = await db.execute(
            select(BusinessUnitMember).where(
                BusinessUnitMember.business_unit_id == business_unit_id,
                BusinessUnitMember.user_id == current_user.id
            )
        )
        memberships = result.scalars().all()
        membership = memberships[0] if memberships else None
        
        from app.core.casbin import get_enforcer
        from app.core.organization import get_user_organization, get_organization_domain
        enforcer = get_enforcer()
        organization = await get_user_organization(current_user, db)
        org_domain = get_organization_domain(organization)
        is_admin = await is_platform_admin(current_user, db, enforcer)
        
        if not membership and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this business unit"
            )
        
        # Store in user's active_business_unit_id field
        current_user.active_business_unit_id = business_unit_id
    else:
        # Clear active business unit
        current_user.active_business_unit_id = None
    
    await db.commit()
    await db.refresh(current_user)
    
    return {"business_unit_id": str(business_unit_id) if business_unit_id else None}

@router.get("/users/me/active-business-unit")
async def get_active_business_unit(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the active business unit for the current user"""
    # Refresh user to get latest active_business_unit_id
    await db.refresh(current_user)
    
    if current_user.active_business_unit_id:
        # Validate user still has access to this business unit
        result = await db.execute(
            select(BusinessUnitMember).where(
                BusinessUnitMember.business_unit_id == current_user.active_business_unit_id,
                BusinessUnitMember.user_id == current_user.id
            )
        )
        memberships = result.scalars().all()
        membership = memberships[0] if memberships else None
        
        # Also check if admin
        from app.core.casbin import get_enforcer
        from app.core.organization import get_user_organization, get_organization_domain
        enforcer = get_enforcer()
        organization = await get_user_organization(current_user, db)
        org_domain = get_organization_domain(organization)
        is_admin = await is_platform_admin(current_user, db, enforcer)
        
        if membership or is_admin:
            return {"business_unit_id": str(current_user.active_business_unit_id)}
        else:
            # User no longer has access, clear it
            current_user.active_business_unit_id = None
            await db.commit()
    
    return {"business_unit_id": None}

@router.get("/roles/available")
async def get_available_bu_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available business unit roles (non-platform roles only).
    This endpoint doesn't require platform permissions - any authenticated user can see BU roles.
    """
    from app.models.rbac import Role
    from app.schemas.rbac import RoleResponse
    from datetime import datetime
    
    # Get only business unit roles (not platform roles)
    result = await db.execute(
        select(Role).where(Role.is_platform_role == False).order_by(Role.name)
    )
    bu_roles = result.scalars().all()
    
    # Convert to response format
    roles_response = []
    for role in bu_roles:
        roles_response.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_platform_role=role.is_platform_role,
            created_at=role.created_at,
            permissions=[]  # Don't include permissions for this endpoint
        ))
    
    return roles_response

@router.get("/users/available")
async def get_available_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by email or name")
):
    """
    Get available users in the same organization.
    This endpoint doesn't require platform permissions - any authenticated user can see users in their organization.
    """
    from sqlalchemy import or_
    
    # Get users in the same organization
    query = select(User).where(User.organization_id == current_user.organization_id)
    
    # Apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.email.ilike(search_pattern),
                User.username.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )
    
    # Limit to 1000 results
    query = query.limit(1000)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Convert to response format (simplified, without roles for performance)
    users_response = []
    for user in users:
        users_response.append({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active
        })
    
    return users_response

