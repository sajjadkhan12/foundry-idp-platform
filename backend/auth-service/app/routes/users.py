import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.schemas.users import (
    CreateUserRequest, 
    UpdateUserRequest, 
    UpdateCurrentUserRequest, 
    ChangePasswordRequest
)
from app.core.dependencies import (
    user_servicer, 
    authz_servicer, 
    MockContext, 
    auth_pb2, 
    verify_token, 
    PROTO_AVAILABLE, 
    _get_token_from_header, 
    _get_user_id_from_token
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/users/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    context = MockContext()
    grpc_request = auth_pb2.GetCurrentUserRequest(token=token)
    response = await user_servicer.GetCurrentUser(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to get user")
    
    # Fetch organization name for dynamic branding
    organization_name = None
    if response.organization_id:
        from app.database import AsyncSessionLocal
        from app.models.rbac import Organization
        from sqlalchemy.future import select
        async with AsyncSessionLocal() as db:
            org_result = await db.execute(
                select(Organization).where(Organization.id == uuid.UUID(response.organization_id))
            )
            org = org_result.scalar_one_or_none()
            if org:
                organization_name = org.name

    return {
        "id": response.id,
        "email": response.email,
        "username": response.username,
        "full_name": response.full_name,
        "roles": list(response.roles),
        "avatar_url": response.avatar_url,
        "is_active": response.is_active,
        "is_admin": response.is_admin,
        "created_at": response.created_at,
        "organization_id": response.organization_id,
        "organization_name": organization_name,
    }


@router.get("/users/me/permissions")
async def get_user_permissions(authorization: Optional[str] = Header(None)):
    """Get current user permissions"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    # Get user ID from token
    user_id = await _get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    context = MockContext()
    grpc_request = auth_pb2.GetUserPermissionsRequest(
        user_id=user_id,
        business_unit_id="",
        organization_id=""
    )
    response = await authz_servicer.GetUserPermissions(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to get permissions")
    
    # Return permissions in the format expected by frontend
    return [{"slug": perm} for perm in response.permissions]


@router.put("/users/me")
async def update_current_user(
    request: UpdateCurrentUserRequest,
    authorization: Optional[str] = Header(None)
):
    """Update current user"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    context = MockContext()
    grpc_request = auth_pb2.UpdateCurrentUserRequest(
        token=token,
        email=request.email or "",
        full_name=request.full_name or ""
    )
    response = await user_servicer.UpdateCurrentUser(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update user")
    
    return {
        "id": response.id,
        "email": response.email,
        "username": response.username,
        "full_name": response.full_name,
        "roles": list(response.roles),
        "avatar_url": response.avatar_url,
        "is_active": response.is_active,
        "is_admin": response.is_admin,
        "created_at": response.created_at,
        "organization_id": response.organization_id,
    }


@router.post("/users/me/change-password")
async def change_password(
    request: ChangePasswordRequest,
    authorization: Optional[str] = Header(None)
):
    """Change password"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    context = MockContext()
    grpc_request = auth_pb2.ChangePasswordRequest(
        token=token,
        current_password=request.current_password,
        new_password=request.new_password
    )
    await user_servicer.ChangePassword(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to change password")
    
    return {"message": "Password changed successfully"}


@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None),
    role_filter: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """List users - automatically filtered by current user's organization unless super admin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get current user's organization_id
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    organization_id = None
    is_super = False
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if current_user:
            enforcer = get_enforcer()
            is_super = await is_super_admin(current_user, db, enforcer)
            if not is_super:
                organization_id = str(current_user.organization_id)
    
    # Super admins should only see users from their own organization
    if is_super and not organization_id:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
            current_user = result.scalar_one_or_none()
            if current_user:
                organization_id = str(current_user.organization_id)

    
    context = MockContext()
    grpc_request = auth_pb2.ListUsersRequest(
        skip=skip,
        limit=limit,
        search=search or "",
        role_filter=role_filter or "",
        organization_id=organization_id or ""
    )
    response = await user_servicer.ListUsers(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list users")
    
    return {
        "users": [{
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "roles": list(u.roles),
            "avatar_url": u.avatar_url,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "created_at": u.created_at,
            "organization_id": u.organization_id,
        } for u in response.users],
        "total": response.total,
        "skip": response.skip,
        "limit": response.limit
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Get user by ID - verify user belongs to same organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify user belongs to same organization
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
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
            raise HTTPException(status_code=404, detail="Current user not found")
        
        # Get target user
        target_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        target_user = target_user_result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if current user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Allow super admins to access any user
        if is_super:
             pass
        # Users can always access their own data
        elif str(current_user.id) == user_id:
             pass
        # Organization admins can only access users from their organization
        elif target_user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: User belongs to a different organization")
    
    context = MockContext()
    grpc_request = auth_pb2.GetUserRequest(user_id=user_id)
    response = await user_servicer.GetUser(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "User not found")
    
    return {
        "id": response.id,
        "email": response.email,
        "username": response.username,
        "full_name": response.full_name,
        "roles": list(response.roles),
        "avatar_url": response.avatar_url,
        "is_active": response.is_active,
        "is_admin": response.is_admin,
        "created_at": response.created_at,
        "organization_id": response.organization_id,
        "active_business_unit_id": response.active_business_unit_id if response.active_business_unit_id else None,
    }


@router.post("/users")
async def create_user(
    request: CreateUserRequest, 
    current_user_id: str = Depends(verify_token)
):
    """Create user - automatically uses current user's organization unless super admin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get current user's organization_id
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
    from sqlalchemy.future import select
    from app.utils.helpers import is_super_admin
    from app.core.casbin import get_enforcer
    
    organization_id = request.organization_id
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="Current user not found")
        
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        if not is_super:
            # Organization admin: must create users in their own organization
            if not current_user.organization_id:
                raise HTTPException(status_code=400, detail="Current user must belong to an organization")
            organization_id = str(current_user.organization_id)
        else:
            # Super admin: can specify organization_id, or use current user's, or foundry organization
            if not organization_id:
                if current_user.organization_id:
                    # Use current user's organization
                    organization_id = str(current_user.organization_id)
                else:
                    # Get foundry organization (platform owner)
                    from app.models.rbac import Organization
                    org_result = await db.execute(
                        select(Organization).where(Organization.slug == "foundry")
                    )
                    foundry_org = org_result.scalar_one_or_none()
                    if foundry_org:
                        organization_id = str(foundry_org.id)
                    else:
                        # Get first organization as fallback
                        org_result = await db.execute(select(Organization).limit(1))
                        first_org = org_result.scalar_one_or_none()
                        if first_org:
                            organization_id = str(first_org.id)
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="organization_id is required. Please specify an organization or ensure the foundry organization exists.")
    
    context = MockContext()
    grpc_request = auth_pb2.CreateUserRequest(
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name or "",
        organization_id=organization_id,
        role_names=request.role_names or []
    )
    response = await user_servicer.CreateUser(grpc_request, context)
    
    if context.code:
        status_code = 409 if context.code.value == 6 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create user")
    
    return {
        "id": response.id,
        "email": response.email,
        "username": response.username,
        "full_name": response.full_name,
        "roles": list(response.roles),
        "avatar_url": response.avatar_url,
        "is_active": response.is_active,
        "is_admin": response.is_admin,
        "created_at": response.created_at,
        "organization_id": response.organization_id,
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: str, 
    request: UpdateUserRequest,
    current_user_id: str = Depends(verify_token)
):
    """Update user - validate user belongs to same organization unless super admin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Validate organization ownership
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
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
        
        # Get target user
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        target_user = result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # If not super admin, ensure target user is in same organization
        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="You can only update users in your organization")
    
    context = MockContext()
    grpc_request = auth_pb2.UpdateUserRequest()
    grpc_request.user_id = user_id
    if request.email:
        grpc_request.email = request.email
    if request.full_name:
        grpc_request.full_name = request.full_name
    if request.password:
        grpc_request.password = request.password
    if request.role_names:
        grpc_request.role_names.extend(request.role_names)
    
    if request.is_active is not None:
        grpc_request.is_active = request.is_active
        
    response = await user_servicer.UpdateUser(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update user")
    
    return {
        "id": response.id,
        "email": response.email,
        "username": response.username,
        "full_name": response.full_name,
        "roles": list(response.roles),
        "avatar_url": response.avatar_url,
        "is_active": response.is_active,
        "is_admin": response.is_admin,
        "created_at": response.created_at,
        "organization_id": response.organization_id,
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Delete user - validate user belongs to same organization unless super admin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Validate organization ownership
    from app.database import AsyncSessionLocal
    from app.models.rbac import User
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
        
        # Get target user
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        target_user = result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # If not super admin, ensure target user is in same organization
        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="You can only delete users in your organization")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteUserRequest(user_id=user_id)
    await user_servicer.DeleteUser(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete user")
    
    return {"message": "User deleted successfully"}
