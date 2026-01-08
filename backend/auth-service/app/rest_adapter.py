"""
REST to gRPC adapter for auth microservice
This allows REST endpoints to call gRPC services
"""
import logging
# Configure logging to reduce verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from fastapi import FastAPI, HTTPException, Depends, Query, Header, Cookie, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import grpc
import uuid

from app.config import settings
from app.grpc.auth_servicer import AuthenticationServicer
from app.grpc.authorization_servicer import AuthorizationServicer
from app.grpc.user_servicer import UserServicer
from app.grpc.role_servicer import RoleServicer
from app.grpc.group_servicer import GroupServicer
from app.grpc.business_unit_servicer import BusinessUnitServicer
from app.grpc.organization_servicer import OrganizationServicer
from app.grpc.business_unit_group_servicer import BusinessUnitGroupServicer
from app.grpc.credential_servicer import CredentialServicer
from app.core.db_init import init_database
from contextlib import asynccontextmanager

# Import generated proto modules
try:
    from proto import auth_pb2, auth_pb2_grpc
except ImportError:
    # Proto files not generated yet
    auth_pb2 = None
    auth_pb2_grpc = None

# App will be created with lifespan in the next block


# Request/Response models
class LoginRequest(BaseModel):
    identifier: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


class ValidateTokenRequest(BaseModel):
    token: str


# Create servicer instances
auth_servicer = AuthenticationServicer()
authz_servicer = AuthorizationServicer()
user_servicer = UserServicer()
role_servicer = RoleServicer()
group_servicer = GroupServicer()
bu_servicer = BusinessUnitServicer()
org_servicer = OrganizationServicer()
bu_group_servicer = BusinessUnitGroupServicer()
credential_servicer = CredentialServicer()

# Audit Stub (Client)
try:
    if auth_pb2_grpc:
        # Create a channel to the audit service
        # In docker-compose, hostname is audit-service, port 50057
        audit_channel = grpc.aio.insecure_channel('audit-service:50057')
        # We need audit_pb2_grpc from audit.proto, but auth-service might not have it yet unless we copy/gen it
        # For now, we assume it's generated in same proto package
        from proto import audit_pb2_grpc
        audit_stub = audit_pb2_grpc.AuditServiceStub(audit_channel)
    else:
        audit_stub = None
except Exception as e:
    print(f"Failed to init audit stub: {e}")
    audit_stub = None

PROTO_AVAILABLE = auth_pb2 is not None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup: Initialize database
    try:
        await init_database()
    except Exception as e:
        import logging
        logging.error(f"Database initialization failed: {e}", exc_info=True)
        # Continue startup even if init fails
    
    yield
    # Shutdown (if needed)


# Create FastAPI app with lifespan
app = FastAPI(title="Auth Service REST Adapter", lifespan=lifespan)


class MockContext:
    """Mock gRPC context for REST adapter"""
    def __init__(self):
        self.code = None
        self.details = None
    
    def set_code(self, code):
        self.code = code
    
    def set_details(self, details):
        self.details = details


class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None
    organization_id: Optional[str] = None
    role_names: Optional[List[str]] = None


class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_names: Optional[List[str]] = None


class UpdateCurrentUserRequest(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class CreateRoleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_platform_role: bool = False
    permissions: Optional[List[str]] = None


class UpdateRoleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_platform_role: Optional[bool] = None
    permissions: Optional[List[str]] = None


class AssignRoleRequest(BaseModel):
    role_name: str
    organization_id: Optional[str] = None


class CreateGroupRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CreateBusinessUnitRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    organization_id: Optional[str] = None


class UpdateBusinessUnitRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AddBusinessUnitMemberRequest(BaseModel):
    user_email: str
    role_ids: Optional[List[str]] = None


class PermissionCheckRequest(BaseModel):
    permission_slug: str
    business_unit_id: Optional[str] = None
    organization_id: Optional[str] = None


class CreateOrganizationRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CreateBusinessUnitGroupRequest(BaseModel):
    business_unit_id: str
    name: str
    description: Optional[str] = None
    role_id: str


class UpdateBusinessUnitGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


def _get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract token from Authorization header"""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None


async def _get_user_id_from_token(token: Optional[str]) -> Optional[str]:
    """Extract user ID from token"""
    if not token or not PROTO_AVAILABLE:
        return None
    try:
        context = MockContext()
        grpc_request = auth_pb2.ValidateTokenRequest(token=token)
        response = await auth_servicer.ValidateToken(grpc_request, context)
        if not context.code:
            return response.user_id
    except:
        pass
    return None


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency to verify token and return user ID.
    Raises HTTPException(401) if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
    user_id = await _get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    return user_id


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint - REST wrapper for gRPC"""
    if not auth_pb2:
        raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
    
    context = MockContext()
    grpc_request = auth_pb2.LoginRequest(
        identifier=request.identifier,
        password=request.password
    )
    
    response = await auth_servicer.Login(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500  # UNAUTHENTICATED = 16
        raise HTTPException(status_code=status_code, detail=context.details)
    
    return {
        "access_token": response.access_token,
        "token_type": response.token_type,
        "user": {
            "id": response.user.id,
            "email": response.user.email,
            "username": response.user.username,
            "full_name": response.user.full_name,
            "roles": list(response.user.roles),
            "avatar_url": response.user.avatar_url,
            "is_active": response.user.is_active,
            "is_admin": response.user.is_admin,
            "created_at": response.user.created_at,
        }
    }


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh token endpoint"""
    if not auth_pb2:
        raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
    
    if not request.refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    
    context = MockContext()
    grpc_request = auth_pb2.RefreshTokenRequest(refresh_token=request.refresh_token)
    
    response = await auth_servicer.RefreshToken(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details)
    
    return {
        "access_token": response.access_token,
        "token_type": response.token_type,
        "user": {
            "id": response.user.id,
            "email": response.user.email,
            "username": response.user.username,
            "full_name": response.user.full_name,
            "roles": list(response.user.roles),
            "avatar_url": response.user.avatar_url,
            "is_active": response.user.is_active,
            "is_admin": response.user.is_admin,
            "created_at": response.user.created_at,
        }
    }


@app.post("/api/v1/auth/logout")
async def logout(
    request: Optional[RefreshTokenRequest] = None,
    refresh_token: Optional[str] = Cookie(None)
):
    """Logout endpoint"""
    if not auth_pb2:
        raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
    
    # Get refresh token from request body or cookie
    token = (request.refresh_token if request else None) or refresh_token
    
    # Only call logout service if we have a token
    if token:
        context = MockContext()
        grpc_request = auth_pb2.LogoutRequest(refresh_token=token)
        await auth_servicer.Logout(grpc_request, context)
        
        if context.code:
            raise HTTPException(status_code=500, detail=context.details)
    
    return {"message": "Logged out successfully"}


@app.post("/api/v1/auth/validate")
async def validate_token(request: ValidateTokenRequest):
    """Validate token endpoint"""
    if not auth_pb2:
        raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
    
    context = MockContext()
    grpc_request = auth_pb2.ValidateTokenRequest(token=request.token)
    
    response = await auth_servicer.ValidateToken(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details)
    
    return {
        "user_id": response.user_id,
        "email": response.email,
        "username": response.username,
        "organization_id": response.organization_id,
        "is_active": response.is_active,
        "roles": list(response.roles)
    }



# ==================== Business Unit Endpoints ====================

@app.get("/api/v1/business-units")
async def list_business_units(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """List business units"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Auto-derive user_id from token if not provided (for permission checks)
    if not user_id:
        user_id = current_user_id
    
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


@app.get("/api/v1/business-units/users/available")
async def get_available_users_for_business_unit(
    search: Optional[str] = Query(None)
):
    """Get users available to be added to a business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    from app.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models.rbac import User
    
    async with AsyncSessionLocal() as db:
        query = select(User).where(User.is_active == True)
        
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


@app.get("/api/v1/business-units/roles/available")
async def get_available_roles_for_business_unit():
    """Get roles available to be assigned in a business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    from app.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models.rbac import Role
    
    async with AsyncSessionLocal() as db:
        # Get all roles (both platform and BU roles can be assigned)
        query = select(Role)
        result = await db.execute(query)
        roles = result.scalars().all()
        
        return [{
            "id": str(role.id),
            "name": role.name,
            "description": role.description or "",
            "is_platform_role": role.is_platform_role
        } for role in roles]


@app.get("/api/v1/business-units/users/me/active-business-unit")
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


@app.post("/api/v1/business-units/users/me/active-business-unit")
@app.post("/api/v1/business-units/users/me/active-business-unit/{bu_id}")
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
        
    # We already have valid token from dependency, but need it for downstream if needed
    # Actually, current_user_id is enough proof of auth.
    pass
    
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


@app.post("/api/v1/business-units")
async def create_business_unit(
    request: CreateBusinessUnitRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Auto-derive organization_id if not provided
    organization_id = request.organization_id
    if not organization_id:
        # Get current user to extract organization_id
        from app.database import AsyncSessionLocal
        from sqlalchemy.future import select
        from app.models.rbac import User
        import uuid
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
            user = result.scalar_one_or_none()
            if user and user.organization_id:
                organization_id = str(user.organization_id)
        
        # If still no organization_id, get the first organization
        if not organization_id:
            from app.models.rbac import Organization
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Organization).limit(1))
                org = result.scalar_one_or_none()
                if org:
                    organization_id = str(org.id)
    
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
            import uuid
            
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
        "member_count": 1 if creator_user_id else 0,  # Creator was added
        "can_manage_members": response.can_manage_members,
        "created_at": response.created_at,
        "updated_at": response.updated_at,
    }


@app.put("/api/v1/business-units/{business_unit_id}")
async def update_business_unit(business_unit_id: str, request: UpdateBusinessUnitRequest):
    """Update business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.delete("/api/v1/business-units/{business_unit_id}")
async def delete_business_unit(business_unit_id: str):
    """Delete business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteBusinessUnitRequest(business_unit_id=business_unit_id)
    await bu_servicer.DeleteBusinessUnit(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete business unit")
    
    return {"message": "Business unit deleted successfully"}


@app.get("/api/v1/business-units/{business_unit_id}/members")
async def list_business_unit_members(business_unit_id: str):
    """List business unit members"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.post("/api/v1/business-units/{business_unit_id}/members")
async def add_business_unit_member(business_unit_id: str, request: AddBusinessUnitMemberRequest):
    """Add member to business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.delete("/api/v1/business-units/{business_unit_id}/members/{user_id}")
async def remove_business_unit_member(business_unit_id: str, user_id: str):
    """Remove member from business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.RemoveBusinessUnitMemberRequest(
        business_unit_id=business_unit_id,
        user_id=user_id
    )
    await bu_servicer.RemoveBusinessUnitMember(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to remove member")
    
    return {"message": "Member removed successfully"}


# NOTE: This route MUST come AFTER all specific /business-units/... routes
# to avoid matching "users", "roles" etc. as business_unit_id
@app.get("/api/v1/business-units/{business_unit_id}")
async def get_business_unit(business_unit_id: str):
    """Get business unit by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.get("/api/v1/users/me")
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


@app.get("/api/v1/users/me/permissions")
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


@app.put("/api/v1/users/me")
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


@app.post("/api/v1/users/me/change-password")
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


@app.get("/api/v1/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None),
    role_filter: Optional[str] = Query(None)
):
    """List users"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.ListUsersRequest(
        skip=skip,
        limit=limit,
        search=search or "",
        role_filter=role_filter or ""
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


@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.post("/api/v1/users")
async def create_user(request: CreateUserRequest, authorization: Optional[str] = Header(None)):
    """Create user"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # If organization_id not provided, get it from the current user's token
    organization_id = request.organization_id
    if not organization_id:
        token = _get_token_from_header(authorization)
        if token:
            user_id = await _get_user_id_from_token(token)
            if user_id:
                # Get current user to extract organization_id
                context_temp = MockContext()
                grpc_request_temp = auth_pb2.GetCurrentUserRequest(token=token)
                response_temp = await user_servicer.GetCurrentUser(grpc_request_temp, context_temp)
                if not context_temp.code and response_temp.organization_id:
                    organization_id = response_temp.organization_id
                # If still no organization_id, try to get the first organization or default
                if not organization_id:
                    from app.database import AsyncSessionLocal
                    from sqlalchemy.future import select
                    from app.models.rbac import Organization
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(select(Organization).limit(1))
                        org = result.scalar_one_or_none()
                        if org:
                            organization_id = str(org.id)
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="organization_id is required. Please ensure you have an organization set up.")
    
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


@app.put("/api/v1/users/{user_id}")
async def update_user(user_id: str, request: UpdateUserRequest):
    """Update user"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteUserRequest(user_id=user_id)
    await user_servicer.DeleteUser(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete user")
    
    return {"message": "User deleted successfully"}


# ==================== Role Endpoints ====================

@app.get("/api/v1/roles")
async def list_roles(platform_roles_only: bool = Query(False)):
    """List roles"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.ListRolesRequest(platform_roles_only=platform_roles_only)
    response = await role_servicer.ListRoles(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list roles")
    
    return [{
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "is_platform_role": r.is_platform_role,
        "created_at": r.created_at,
        "permissions": list(r.permissions) if r.permissions else []
    } for r in response.roles]


@app.get("/api/v1/roles/{role_id}")
async def get_role(role_id: str):
    """Get role by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.GetRoleRequest(role_id=role_id)
    response = await role_servicer.GetRole(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Role not found")
    
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "is_platform_role": response.is_platform_role,
        "created_at": response.created_at,
        "permissions": list(response.permissions) if response.permissions else []
    }


@app.post("/api/v1/roles")
async def create_role(request: CreateRoleRequest):
    """Create role"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.CreateRoleRequest(
        name=request.name,
        description=request.description or "",
        is_platform_role=request.is_platform_role,
        permissions=request.permissions or []
    )
    response = await role_servicer.CreateRole(grpc_request, context)
    
    if context.code:
        status_code = 409 if context.code.value == 6 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create role")
    
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "is_platform_role": response.is_platform_role,
        "created_at": response.created_at,
        "permissions": list(response.permissions) if response.permissions else []
    }


@app.put("/api/v1/roles/{role_id}")
async def update_role(role_id: str, request: UpdateRoleRequest):
    """Update role"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.UpdateRoleRequest(
        role_id=role_id,
        name=request.name or "",
        description=request.description or "",
        is_platform_role=request.is_platform_role if request.is_platform_role is not None else False,
        permissions=request.permissions if request.permissions is not None else []
    )
    response = await role_servicer.UpdateRole(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update role")
    
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "is_platform_role": response.is_platform_role,
        "created_at": response.created_at,
        "permissions": list(response.permissions) if response.permissions else []
    }


@app.delete("/api/v1/roles/{role_id}")
async def delete_role(role_id: str):
    """Delete role"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteRoleRequest(role_id=role_id)
    await role_servicer.DeleteRole(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete role")
    
    return {"message": "Role deleted successfully"}


# ==================== Group Endpoints ====================

@app.get("/api/v1/groups")
async def list_groups():
    """List groups"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.ListGroupsRequest()
    response = await group_servicer.ListGroups(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list groups")
    
    return [{
        "id": g.id,
        "name": g.name,
        "description": g.description,
        "created_at": g.created_at,
    } for g in response.groups]


@app.get("/api/v1/groups/{group_id}")
async def get_group(group_id: str):
    """Get group by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.GetGroupRequest(group_id=group_id)
    response = await group_servicer.GetGroup(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Group not found")
    
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "created_at": response.created_at,
    }


@app.post("/api/v1/groups")
async def create_group(request: CreateGroupRequest):
    """Create group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.CreateGroupRequest(
        name=request.name,
        description=request.description or ""
    )
    response = await group_servicer.CreateGroup(grpc_request, context)
    
    if context.code:
        status_code = 409 if context.code.value == 6 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create group")
    
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "created_at": response.created_at,
    }


@app.put("/api/v1/groups/{group_id}")
async def update_group(group_id: str, request: UpdateGroupRequest):
    """Update group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.UpdateGroupRequest(
        group_id=group_id,
        name=request.name or "",
        description=request.description or ""
    )
    response = await group_servicer.UpdateGroup(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update group")
    
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "created_at": response.created_at,
    }


@app.delete("/api/v1/groups/{group_id}")
async def delete_group(group_id: str):
    """Delete group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteGroupRequest(group_id=group_id)
    await group_servicer.DeleteGroup(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete group")
    
    return {"message": "Group deleted successfully"}


@app.post("/api/v1/groups/{group_id}/users/{user_id}")
async def add_user_to_group(group_id: str, user_id: str):
    """Add user to group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.AddGroupMemberRequest(
        group_id=group_id,
        user_id=user_id
    )
    await group_servicer.AddGroupMember(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to add user to group")
    
    return {"message": "User added to group successfully"}


@app.delete("/api/v1/groups/{group_id}/users/{user_id}")
async def remove_user_from_group(group_id: str, user_id: str):
    """Remove user from group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.RemoveGroupMemberRequest(
        group_id=group_id,
        user_id=user_id
    )
    await group_servicer.RemoveGroupMember(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to remove user from group")
    
    return {"message": "User removed from group successfully"}


@app.get("/api/v1/permissions")
async def list_permissions():
    """List all permissions with metadata"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Import permission registry
    from app.core.permission_registry import PERMISSIONS_BY_SLUG
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.rbac import PermissionMetadata
    
    # Get metadata from database
    db_metadata = {}
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(PermissionMetadata))
            db_metadata = {perm.slug: perm for perm in result.scalars().all()}
    except Exception:
        # Fallback if DB table doesn't exist yet or other error
        pass
    
    # Combine registry with DB metadata
    result = []
    for slug, perm_def in PERMISSIONS_BY_SLUG.items():
        meta = db_metadata.get(slug)
        result.append({
            "slug": slug,
            "name": meta.name if meta else perm_def.get("name", ""),
            "description": meta.description if meta else perm_def.get("description", ""),
            "category": meta.category if meta else perm_def.get("category", ""),
            "resource": meta.resource if meta else perm_def.get("resource", ""),
            "action": meta.action if meta else perm_def.get("action", ""),
            "environment": meta.environment if meta else perm_def.get("environment"),
            "icon": meta.icon if meta else perm_def.get("icon", ""),
        })
    
    return result


@app.post("/api/v1/organizations", status_code=201)
async def create_organization(
    request: CreateOrganizationRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.CreateOrganizationRequest(
        name=request.name,
        slug=request.slug,
        description=request.description or ""
    )
    response = await org_servicer.CreateOrganization(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create organization")
    
    return {
        "id": response.id,
        "name": response.name,
        "slug": response.slug,
        "description": response.description,
        "is_active": response.is_active,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.get("/api/v1/organizations")
async def list_organizations(
    skip: int = Query(0), 
    limit: int = Query(100),
    current_user_id: str = Depends(verify_token)
):
    """List organizations"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.ListOrganizationsRequest(skip=skip, limit=limit)
    response = await org_servicer.ListOrganizations(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list organizations")
    
    return [{
        "id": org.id,
        "name": org.name,
        "slug": org.slug,
        "description": org.description,
        "is_active": org.is_active,
        "created_at": org.created_at,
        "updated_at": org.updated_at
    } for org in response.organizations]


@app.get("/api/v1/organizations/{org_id}")
async def get_organization(org_id: str):
    """Get organization by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.GetOrganizationRequest(organization_id=org_id)
    response = await org_servicer.GetOrganization(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Organization not found")
    
    return {
        "id": response.id,
        "name": response.name,
        "slug": response.slug,
        "description": response.description,
        "is_active": response.is_active,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.post("/api/v1/business-units/{business_unit_id}/groups", status_code=201)
async def create_business_unit_group(business_unit_id: str, request: CreateBusinessUnitGroupRequest):
    """Create business unit group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.get("/api/v1/business-units/{business_unit_id}/groups")
async def list_business_unit_groups(business_unit_id: str):
    """List business unit groups"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
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


@app.post("/api/v1/permissions/check")
async def check_permission(
    request: PermissionCheckRequest,
    authorization: Optional[str] = Header(None)
):
    """Check permission"""
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
    grpc_request = auth_pb2.PermissionCheckRequest(
        user_id=user_id,
        permission_slug=request.permission_slug,
        business_unit_id=request.business_unit_id or "",
        organization_id=request.organization_id or ""
    )
    response = await authz_servicer.CheckPermission(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Permission check failed")
    
    return {
        "allowed": response.allowed,
        "message": response.message
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-microservice",
        "proto_ready": auth_pb2 is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
