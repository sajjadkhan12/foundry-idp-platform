import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.schemas.business_units import (
    CreateBusinessUnitRequest, 
    UpdateBusinessUnitRequest, 
    AddBusinessUnitMemberRequest, 
    CreateBusinessUnitGroupRequest
)
from app.core.dependencies import (
    bu_servicer, 
    bu_group_servicer, 
    MockContext, 
    auth_pb2, 
    verify_token, 
    PROTO_AVAILABLE, 
    _get_token_from_header, 
    _get_user_id_from_token
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/business-units")
async def list_business_units(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """List business units - automatically filtered by current user's organization unless super admin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Auto-derive user_id from token if not provided (for permission checks)
    if not user_id:
        user_id = current_user_id
    
    # Get current user's organization_id if not provided and user is not super admin
    if not organization_id:
        from app.database import AsyncSessionLocal
        from app.models.rbac import User
        from sqlalchemy.future import select
        from app.utils.helpers import is_super_admin
        from app.core.casbin import get_enforcer
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.id == uuid.UUID(current_user_id))
            )
            current_user = result.scalar_one_or_none()
            if current_user:
                enforcer = get_enforcer()
                is_super = await is_super_admin(current_user, db, enforcer)
                # Everyone is filtered by their own organization_id
                organization_id = str(current_user.organization_id) if current_user.organization_id else None

    context = MockContext()
    grpc_request = auth_pb2.ListBusinessUnitsRequest(
        user_id=user_id or "",
        organization_id=organization_id or ""
    )
    response = await bu_servicer.ListBusinessUnits(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list business units")
    
    return [{
        "id": bu.id,
        "name": bu.name,
        "slug": bu.slug,
        "description": bu.description,
        "organization_id": bu.organization_id,
        "is_active": bu.is_active,
        "role": bu.role,
        "member_count": bu.member_count,
        "can_manage_members": bu.can_manage_members,
        "created_at": bu.created_at,
        "updated_at": bu.updated_at,
    } for bu in response.business_units]


@router.get("/business-units/users/available")
async def get_available_users_for_business_unit(
    search: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """Get users available to be added to a business unit - filtered by organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    organization_id = None
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if current_user:
            enforcer = get_enforcer()
            is_super = await is_super_admin(current_user, db, enforcer)
            if is_super:
                # Super admins should NOT see organization-specific resources
                return []
            if not is_super:
                # Organization admins can only see users from their organization
                organization_id = str(current_user.organization_id)
    
    async with AsyncSessionLocal() as db:
        query = select(User).where(User.is_active == True)
        
        # Filter by organization
        if organization_id:
            org_uuid = uuid.UUID(organization_id)
            query = query.where(User.organization_id == org_uuid)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (User.email.ilike(search_filter)) |
                (User.username.ilike(search_filter)) |
                (User.full_name.ilike(search_filter))
            )
        
        query = query.limit(50)
        result = await db.execute(query)
        users = result.scalars().all()
        
        return [{
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name or "",
            "is_active": user.is_active
        } for user in users]


@router.get("/business-units/roles/available")
async def get_available_roles_for_business_unit(
    current_user_id: str = Depends(verify_token)
):
    """Get roles available to be assigned in a business unit - filtered by organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    from app.database import AsyncSessionLocal
    from app.models.rbac import User, Role
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    from sqlalchemy import or_, and_
    
    organization_id = None
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if current_user:
            enforcer = get_enforcer()
            is_super = await is_super_admin(current_user, db, enforcer)
            if is_super:
                # Super admins should NOT see organization-specific resources
                return []
            if not is_super:
                organization_id = str(current_user.organization_id)
    
    async with AsyncSessionLocal() as db:
        # Get roles: org roles + organization-admin system role
        query = select(Role)
        if organization_id:
            org_uuid = uuid.UUID(organization_id)
            query = query.where(
                or_(
                    Role.organization_id == org_uuid,
                    and_(Role.organization_id.is_(None), Role.name == "organization-admin")
                )
            )
        else:
            # Super admins see all system roles
            query = query.where(Role.organization_id.is_(None))
        
        result = await db.execute(query)
        roles = result.scalars().all()
        
        return [{
            "id": str(role.id),
            "name": role.name,
            "description": role.description or "",
            "is_platform_role": role.is_platform_role
        } for role in roles]


@router.get("/business-units/users/me/active-business-unit")
async def get_active_business_unit(
    authorization: Optional[str] = Header(None)
):
    """Get the user's currently active business unit"""
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = await _get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    from app.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models.rbac import User
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not user.active_business_unit_id:
            return None
            
        # Get BU details from gRPC
        context = MockContext()
        grpc_request = auth_pb2.GetBusinessUnitRequest(business_unit_id=str(user.active_business_unit_id))
        bu = await bu_servicer.GetBusinessUnit(grpc_request, context)
        
        if context.code:
            return None
            
        return {
            "id": bu.id,
            "name": bu.name,
            "slug": bu.slug,
            "description": bu.description,
            "organization_id": bu.organization_id,
            "is_active": bu.is_active
        }


@router.post("/business-units/users/me/active-business-unit")
@router.post("/business-units/users/me/active-business-unit/{bu_id}")
async def set_active_business_unit(
    bu_id: Optional[str] = None,
    business_unit_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    current_user_id: str = Depends(verify_token)
):
    """Set the user's currently active business unit"""
    # Use business_unit_id from query params if bu_id in path is not provided
    actual_bu_id = bu_id or business_unit_id
    if not actual_bu_id:
        raise HTTPException(status_code=400, detail="business_unit_id required")
        
    user_id = current_user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    from app.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models.rbac import User
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.active_business_unit_id = uuid.UUID(actual_bu_id)
        await db.commit()
        
        return {"id": actual_bu_id, "message": "Active business unit updated"}


@router.post("/business-units")
async def create_business_unit(
    request: CreateBusinessUnitRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Auto-derive organization_id from current user unless super admin
    organization_id = request.organization_id
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        user = result.scalar_one_or_none()
        if user:
            enforcer = get_enforcer()
            is_super = await is_super_admin(user, db, enforcer)
            if not is_super:
                # Organization admin: must create BU in their own organization
                organization_id = str(user.organization_id)
            # Super admin: can specify organization_id or use current user's
            elif not organization_id and user.organization_id:
                organization_id = str(user.organization_id)
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID is required")
    
    # Get creator user_id from token for auto-adding as member
    creator_user_id = current_user_id
    
    context = MockContext()
    grpc_request = auth_pb2.CreateBusinessUnitRequest(
        name=request.name,
        slug=request.slug,
        description=request.description or "",
        organization_id=organization_id
    )
    response = await bu_servicer.CreateBusinessUnit(grpc_request, context)
    
    if context.code:
        status_code = 409 if context.code.value == 6 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create business unit")
    
    # Auto-add creator as a member of the BU with admin role
    if creator_user_id and response.id:
        try:
            from app.database import AsyncSessionLocal
            from sqlalchemy.future import select
            from app.models.rbac import User, Role
            from app.models.business_unit import BusinessUnitMember
            
            async with AsyncSessionLocal() as db:
                # Get creator user
                user_result = await db.execute(select(User).where(User.id == uuid.UUID(creator_user_id)))
                creator = user_result.scalar_one_or_none()
                
                if creator:
                    # Get admin role (or any platform role) to assign
                    role_result = await db.execute(
                        select(Role).where(Role.is_platform_role == True).limit(1)
                    )
                    admin_role = role_result.scalar_one_or_none()
                    
                    # Create membership
                    membership = BusinessUnitMember(
                        business_unit_id=uuid.UUID(response.id),
                        user_id=creator.id,
                        role_id=admin_role.id if admin_role else None
                    )
                    db.add(membership)
                    await db.commit()
        except Exception as e:
            # Log but don't fail - BU was created successfully
            print(f"Warning: Could not auto-add creator to BU: {e}")
    
    return {
        "id": response.id,
        "name": response.name,
        "slug": response.slug,
        "description": response.description,
        "organization_id": response.organization_id,
        "is_active": response.is_active,
        "role": response.role,
        "member_count": 1 if creator_user_id else 0,
        "can_manage_members": response.can_manage_members,
        "created_at": response.created_at,
        "updated_at": response.updated_at,
    }


@router.put("/business-units/{business_unit_id}")
async def update_business_unit(
    business_unit_id: str, 
    request: UpdateBusinessUnitRequest,
    current_user_id: str = Depends(verify_token)
):
    """Update business unit - validate BU belongs to same organization unless super admin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Validate organization ownership
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        # Get target business unit
        result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        target_bu = result.scalar_one_or_none()
        if not target_bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Check if super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins can access everything
        if not is_super:
            # If not super admin, ensure BU is in same organization
            if target_bu.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="You can only update business units in your organization")
    
    context = MockContext()
    grpc_request = auth_pb2.UpdateBusinessUnitRequest(
        business_unit_id=business_unit_id,
        name=request.name or "",
        description=request.description or "",
        is_active=request.is_active if request.is_active is not None else False
    )
    response = await bu_servicer.UpdateBusinessUnit(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update business unit")
    
    return {
        "id": response.id,
        "name": response.name,
        "slug": response.slug,
        "description": response.description,
        "organization_id": response.organization_id,
        "is_active": response.is_active,
        "role": response.role,
        "member_count": response.member_count,
        "can_manage_members": response.can_manage_members,
        "created_at": response.created_at,
        "updated_at": response.updated_at,
    }


@router.delete("/business-units/{business_unit_id}")
async def delete_business_unit(
    business_unit_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Delete business unit - validate BU belongs to same organization unless super admin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Validate organization ownership
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        # Get target business unit
        result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        target_bu = result.scalar_one_or_none()
        if not target_bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Check if super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins can access everything
        if not is_super:
            # If not super admin, ensure BU is in same organization
            if target_bu.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="You can only delete business units in your organization")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteBusinessUnitRequest(business_unit_id=business_unit_id)
    await bu_servicer.DeleteBusinessUnit(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete business unit")
    
    return {"message": "Business unit deleted successfully"}


@router.get("/business-units/{business_unit_id}/members")
async def list_business_unit_members(
    business_unit_id: str,
    current_user_id: str = Depends(verify_token)
):
    """List business unit members - verify BU belongs to user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify business unit belongs to user's organization
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get business unit
        bu_result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # Organization admins can only access business units from their organization
        if bu.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Business unit belongs to a different organization")
    
    context = MockContext()
    grpc_request = auth_pb2.ListBusinessUnitMembersRequest(business_unit_id=business_unit_id)
    response = await bu_servicer.ListBusinessUnitMembers(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list members")
    
    return [{
        "id": m.id,
        "business_unit_id": m.business_unit_id,
        "user_id": m.user_id,
        "user_email": m.user_email,
        "user_name": m.user_name,
        "role": m.role,
        "role_id": m.role_id,
        "created_at": m.created_at,
    } for m in response.members]


@router.post("/business-units/{business_unit_id}/members")
async def add_business_unit_member(
    business_unit_id: str, 
    request: AddBusinessUnitMemberRequest,
    current_user_id: str = Depends(verify_token)
):
    """Add member to business unit - verify BU and user belong to same organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify business unit and user belong to same organization
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        current_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = current_user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get business unit
        bu_result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Get target user by email
        target_user_result = await db.execute(
            select(User).where(User.email == request.user_email.lower())
        )
        target_user = target_user_result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if current user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins can access everything
        if not is_super:
            # Organization admins can only add users from their organization to BUs from their organization
            if bu.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: Business unit belongs to a different organization")
            if target_user.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: User belongs to a different organization")
    
    context = MockContext()
    grpc_request = auth_pb2.AddBusinessUnitMemberRequest(
        business_unit_id=business_unit_id,
        user_email=request.user_email,
        role_ids=request.role_ids or []
    )
    await bu_servicer.AddBusinessUnitMember(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to add member")
    
    return {"message": "Member added successfully"}


@router.delete("/business-units/{business_unit_id}/members/{user_id}")
async def remove_business_unit_member(
    business_unit_id: str, 
    user_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Remove member from business unit - verify BU and user belong to same organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify business unit and user belong to same organization
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        current_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = current_user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get business unit
        bu_result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Get target user
        target_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        target_user = target_user_result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Check if current user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # Organization admins can only remove users from their organization from BUs from their organization
        if bu.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Business unit belongs to a different organization")
        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: User belongs to a different organization")
    
    context = MockContext()
    grpc_request = auth_pb2.RemoveBusinessUnitMemberRequest(
        business_unit_id=business_unit_id,
        user_id=user_id
    )
    await bu_servicer.RemoveBusinessUnitMember(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to remove member")
    
    return {"message": "Member removed successfully"}


@router.post("/business-units/{business_unit_id}/groups", status_code=201)
async def create_business_unit_group(
    business_unit_id: str, 
    request: CreateBusinessUnitGroupRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create business unit group - verify BU belongs to user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify business unit belongs to user's organization
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get business unit
        bu_result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Organization admins can only create groups in business units from their organization
        if not is_super and bu.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Business unit belongs to a different organization")
    
    context = MockContext()
    grpc_request = auth_pb2.CreateBusinessUnitGroupRequest(
        business_unit_id=business_unit_id,
        name=request.name,
        description=request.description or "",
        role_id=request.role_id
    )
    response = await bu_group_servicer.CreateBusinessUnitGroup(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create group")
    
    return {
        "id": response.id,
        "business_unit_id": response.business_unit_id,
        "name": response.name,
        "description": response.description,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@router.get("/business-units/{business_unit_id}/groups")
async def list_business_unit_groups(
    business_unit_id: str,
    current_user_id: str = Depends(verify_token)
):
    """List business unit groups - verify BU belongs to user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify business unit belongs to user's organization
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get business unit
        bu_result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # Organization admins can only access business units from their organization
        if bu.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Business unit belongs to a different organization")
    
    context = MockContext()
    grpc_request = auth_pb2.ListBusinessUnitGroupsRequest(business_unit_id=business_unit_id)
    response = await bu_group_servicer.ListBusinessUnitGroups(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list groups")
    
    return [{
        "id": g.id,
        "business_unit_id": g.business_unit_id,
        "name": g.name,
        "description": g.description,
        "created_at": g.created_at,
        "updated_at": g.updated_at
    } for g in response.groups]


@router.get("/business-units/{business_unit_id}")
async def get_business_unit(
    business_unit_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Get business unit by ID - verify it belongs to user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify business unit belongs to user's organization
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from app.models.business_unit import BusinessUnit
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    async with AsyncSessionLocal() as db:
        # Get current user
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get business unit
        bu_result = await db.execute(
            select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id))
        )
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # Organization admins can only access business units from their organization
        if bu.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Business unit belongs to a different organization")
    
    context = MockContext()
    grpc_request = auth_pb2.GetBusinessUnitRequest(business_unit_id=business_unit_id)
    response = await bu_servicer.GetBusinessUnit(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500  # NOT_FOUND = 5
        raise HTTPException(status_code=status_code, detail=context.details or "Business unit not found")
    
    return {
        "id": response.id,
        "name": response.name,
        "slug": response.slug,
        "description": response.description,
        "organization_id": response.organization_id,
        "is_active": response.is_active,
        "role": response.role,
        "member_count": response.member_count,
        "can_manage_members": response.can_manage_members,
        "created_at": response.created_at,
        "updated_at": response.updated_at,
    }
