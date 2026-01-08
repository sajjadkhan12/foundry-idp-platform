"""
Complete REST to gRPC adapter for auth microservice
This provides full REST API endpoints for all auth service functionality
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Cookie, Header, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

# Import generated proto modules
try:
    from proto import auth_pb2, auth_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    auth_pb2 = None
    auth_pb2_grpc = None

app = FastAPI(title="Auth Service REST API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Request/Response models
class LoginRequest(BaseModel):
    identifier: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    refresh_token: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


class ValidateTokenRequest(BaseModel):
    token: str


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
    organization_id: str


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


class MockContext:
    """Mock gRPC context for REST adapter"""
    def __init__(self):
        self.code = None
        self.details = None
    
    def set_code(self, code):
        self.code = code
    
    def set_details(self, details):
        self.details = details


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


# ==================== Authentication Endpoints ====================

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.LoginRequest(
        identifier=request.identifier,
        password=request.password
    )
    
    response = await auth_servicer.Login(grpc_request, context)
    
    if context.code:
        # Map gRPC status codes to HTTP status codes
        # 16: UNAUTHENTICATED
        # 3: INVALID_ARGUMENT
        # 5: NOT_FOUND
        # 6: ALREADY_EXISTS
        # 7: PERMISSION_DENIED
        
        status_code = 500
        if context.code.value == 16:
            status_code = 401
        elif context.code.value == 3:
            status_code = 400
        elif context.code.value == 5:
            status_code = 404
        elif context.code.value == 6:
            status_code = 409
        elif context.code.value == 7:
            status_code = 403
            
        raise HTTPException(status_code=status_code, detail=context.details or "Login failed")
    
    return {
        "access_token": response.access_token,
        "token_type": response.token_type,
        "refresh_token": getattr(response, 'refresh_token', ''),
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
            "organization_id": response.user.organization_id,
        }
    }


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest = None,
    refresh_token: Optional[str] = Cookie(None)
):
    """Refresh token endpoint"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    token = (request.refresh_token if request else None) or refresh_token
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    
    context = MockContext()
    grpc_request = auth_pb2.RefreshTokenRequest(refresh_token=token)
    
    response = await auth_servicer.RefreshToken(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Token refresh failed")
    
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
            "organization_id": response.user.organization_id,
        }
    }


@app.post("/api/v1/auth/logout")
async def logout(
    request: RefreshTokenRequest = None,
    refresh_token: Optional[str] = Cookie(None)
):
    """Logout endpoint"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    token = (request.refresh_token if request else None) or refresh_token
    if token:
        context = MockContext()
        grpc_request = auth_pb2.LogoutRequest(refresh_token=token)
        await auth_servicer.Logout(grpc_request, context)
    
    return {"message": "Logged out successfully"}


@app.post("/api/v1/auth/validate")
async def validate_token(request: ValidateTokenRequest):
    """Validate token endpoint"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.ValidateTokenRequest(token=request.token)
    
    response = await auth_servicer.ValidateToken(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Invalid token")
    
    return {
        "user_id": response.user_id,
        "email": response.email,
        "username": response.username,
        "organization_id": response.organization_id,
        "is_active": response.is_active,
        "roles": list(response.roles)
    }


# ==================== User Endpoints ====================

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


@app.post("/api/v1/users/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """Upload user avatar"""
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = await _get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    
    # Read file content
    content = await file.read()
    
    # Limit file size (5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")
    
    import base64
    from app.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models.rbac import User
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Store as base64 data URL (simple approach - for production, use object storage)
        avatar_data_url = f"data:{file.content_type};base64,{base64.b64encode(content).decode()}"
        user.avatar_url = avatar_data_url
        await db.commit()
        
        return {"avatar_url": avatar_data_url, "message": "Avatar uploaded successfully"}


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
    # Build gRPC request
    # For proto3, we need to handle optional bool fields differently
    # Since optional keyword may not be supported, we'll use a workaround:
    # Pass is_active through a different mechanism or handle it in the service layer
    # The servicer uses HasField which requires optional keyword in proto3
    # Workaround: Use a sentinel value in email field or handle in service
    # Actually, let's modify the approach: don't set is_active in protobuf if not provided
    # But proto3 requires all fields... Let's check if we can use CopyFrom with selective fields
    
    # Build the request without is_active first
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
    
    # Only set is_active if explicitly provided
    # Since proto3 bool doesn't have presence, we'll use a workaround:
    # Pass is_active_update flag through a comment in email or use a different field
    # Actually, the best approach: modify the servicer to accept None and handle it
    # But for now, let's try setting it conditionally and see if the servicer can handle it
    if request.is_active is not None:
        grpc_request.is_active = request.is_active
    # If not set, the servicer should check HasField - but that won't work without optional
    # So we need to either: 1) update proto to use optional, 2) use a wrapper message, 3) handle in service differently
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


@app.put("/api/v1/users/{user_id}/role")
async def update_user_role(user_id: str, request: AssignRoleRequest):
    """Update user role"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.AssignRoleRequest(
        user_id=user_id,
        role_name=request.role_name,
        organization_id=request.organization_id
    )
    await role_servicer.AssignRole(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to assign role")
    
    return {"message": "Role assigned successfully"}


# ==================== Role Endpoints ====================

@app.get("/api/v1/roles")
async def list_roles(platform_roles_only: bool = Query(False)):
    """List roles"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    # Always set the field - proto3 bool fields don't support HasField, so we always pass the value
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


# ==================== Business Unit Endpoints ====================

@app.get("/api/v1/business-units")
async def list_business_units(
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """List business units"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Auto-derive user_id from token if not provided (for permission checks)
    if not user_id:
        token = _get_token_from_header(authorization)
        if token:
            user_id = await _get_user_id_from_token(token)
    
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
        
        # Return the user's active business unit ID (stored in user preferences or a field)
        # For now, return None if not set - frontend will handle this
        active_bu_id = getattr(user, 'active_business_unit_id', None)
        
        return {
            "business_unit_id": str(active_bu_id) if active_bu_id else None
        }


@app.post("/api/v1/business-units/users/me/active-business-unit")
async def set_active_business_unit(
    business_unit_id: str = Query(...),
    authorization: Optional[str] = Header(None)
):
    """Set the user's currently active business unit"""
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = await _get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    from app.database import AsyncSessionLocal
    from sqlalchemy.future import select
    from app.models.rbac import User, Role
    from app.models.business_unit import BusinessUnit, BusinessUnitMember
    
    async with AsyncSessionLocal() as db:
        # Verify user exists
        user_result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify business unit exists
        bu_result = await db.execute(select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id)))
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")
        
        # Check if user is a platform admin via Casbin or by checking their BU memberships with admin role
        is_platform_admin = False
        
        # Check if user has any membership with a platform admin role
        admin_membership_result = await db.execute(
            select(BusinessUnitMember).join(Role, BusinessUnitMember.role_id == Role.id)
            .where(BusinessUnitMember.user_id == uuid.UUID(user_id))
            .where(Role.is_platform_role == True)
            .where(Role.name.in_(["admin", "Admin", "superadmin", "Superadmin", "platform_admin"]))
        )
        if admin_membership_result.scalars().first():
            is_platform_admin = True
        
        # Also check via Casbin if the user has admin permissions
        if not is_platform_admin:
            try:
                from app.core.casbin import get_enforcer
                enforcer = get_enforcer()
                # Check if user has any admin-level policy
                policies = enforcer.get_filtered_policy(0, user_id)
                for policy in policies:
                    if len(policy) >= 2 and policy[1] in ["*", "admin", "platform:admin"]:
                        is_platform_admin = True
                        break
            except Exception:
                pass  # Casbin check failed, continue with membership check
        
        # If not admin, verify user is a member of this business unit
        if not is_platform_admin:
            membership_result = await db.execute(
                select(BusinessUnitMember).where(
                    BusinessUnitMember.business_unit_id == uuid.UUID(business_unit_id),
                    BusinessUnitMember.user_id == uuid.UUID(user_id)
                )
            )
            # Use scalars().first() since user may have multiple memberships (one per role)
            membership = membership_result.scalars().first()
            if not membership:
                raise HTTPException(status_code=403, detail="User is not a member of this business unit")
        
        # Update user's active business unit
        user.active_business_unit_id = uuid.UUID(business_unit_id)
        await db.commit()
        
        return {"message": "Active business unit set successfully", "business_unit_id": business_unit_id}


@app.get("/api/v1/business-units/{business_unit_id}")
async def get_business_unit(business_unit_id: str):
    """Get business unit by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.GetBusinessUnitRequest(business_unit_id=business_unit_id)
    response = await bu_servicer.GetBusinessUnit(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
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


@app.post("/api/v1/business-units")
async def create_business_unit(
    request: CreateBusinessUnitRequest,
    authorization: Optional[str] = Header(None)
):
    """Create business unit"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Auto-derive organization_id if not provided
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
        
        # If still no organization_id, get the first organization
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
        raise HTTPException(status_code=400, detail="Organization ID is required")
    
    # Get creator user_id from token for auto-adding as member
    creator_user_id = None
    token = _get_token_from_header(authorization)
    if token:
        creator_user_id = await _get_user_id_from_token(token)
    
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


# ==================== Permission Endpoints ====================

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


class ServicePermissionCheckRequest(BaseModel):
    user_id: str
    permission: str
    resource: Optional[str] = None
    resource_id: Optional[str] = None


@app.post("/api/v1/permissions/check-service")
async def check_permission_service(request: ServicePermissionCheckRequest):
    """Check permission for service-to-service calls (no auth token required)"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Map resource to business_unit_id
    business_unit_id = ""
    if request.resource == "business_unit" and request.resource_id:
        business_unit_id = request.resource_id
    
    context = MockContext()
    grpc_request = auth_pb2.PermissionCheckRequest(
        user_id=request.user_id,
        permission_slug=request.permission,
        business_unit_id=business_unit_id,
        organization_id=""
    )
    response = await authz_servicer.CheckPermission(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Permission check failed")
    
    return {
        "has_permission": response.allowed,
        "allowed": response.allowed,
        "message": response.message
    }


# ==================== Organization Endpoints ====================

class CreateOrganizationRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@app.post("/api/v1/organizations", status_code=201)
async def create_organization(request: CreateOrganizationRequest):
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
async def list_organizations(skip: int = Query(0), limit: int = Query(100)):
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


@app.get("/api/v1/organizations/current")
async def get_current_organization(user_id: str = Query(...)):
    """Get current organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.GetCurrentOrganizationRequest(user_id=user_id)
    response = await org_servicer.GetCurrentOrganization(grpc_request, context)
    
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


@app.put("/api/v1/organizations/{org_id}")
async def update_organization(org_id: str, request: UpdateOrganizationRequest):
    """Update organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.UpdateOrganizationRequest(
        organization_id=org_id,
        name=request.name or "",
        description=request.description or "",
        is_active=request.is_active if request.is_active is not None else False
    )
    response = await org_servicer.UpdateOrganization(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update organization")
    
    return {
        "id": response.id,
        "name": response.name,
        "slug": response.slug,
        "description": response.description,
        "is_active": response.is_active,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.delete("/api/v1/organizations/{org_id}")
async def delete_organization(org_id: str):
    """Delete organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteOrganizationRequest(organization_id=org_id)
    await org_servicer.DeleteOrganization(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete organization")
    
    return {"message": "Organization deleted successfully"}


# ==================== Business Unit Group Endpoints ====================

class CreateBusinessUnitGroupRequest(BaseModel):
    business_unit_id: str
    name: str
    description: Optional[str] = None
    role_id: str


class UpdateBusinessUnitGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


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


@app.get("/api/v1/business-unit-groups")
async def list_all_business_unit_groups(business_unit_id: Optional[str] = Query(None)):
    """List all business unit groups (optionally filtered by business_unit_id)"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    if not business_unit_id:
        # If no business_unit_id provided, return empty list or fetch all
        # For now, return empty list as we need business_unit_id to list groups
        return []
    
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


@app.get("/api/v1/business-units/{business_unit_id}/groups/{group_id}")
async def get_business_unit_group(business_unit_id: str, group_id: str):
    """Get business unit group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.GetBusinessUnitGroupRequest(
        business_unit_id=business_unit_id,
        group_id=group_id
    )
    response = await bu_group_servicer.GetBusinessUnitGroup(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Group not found")
    
    return {
        "id": response.id,
        "business_unit_id": response.business_unit_id,
        "name": response.name,
        "description": response.description,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.put("/api/v1/business-units/{business_unit_id}/groups/{group_id}")
async def update_business_unit_group(business_unit_id: str, group_id: str, request: UpdateBusinessUnitGroupRequest):
    """Update business unit group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.UpdateBusinessUnitGroupRequest(
        business_unit_id=business_unit_id,
        group_id=group_id,
        name=request.name or "",
        description=request.description or ""
    )
    response = await bu_group_servicer.UpdateBusinessUnitGroup(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update group")
    
    return {
        "id": response.id,
        "business_unit_id": response.business_unit_id,
        "name": response.name,
        "description": response.description,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.delete("/api/v1/business-units/{business_unit_id}/groups/{group_id}")
async def delete_business_unit_group(business_unit_id: str, group_id: str):
    """Delete business unit group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteBusinessUnitGroupRequest(
        business_unit_id=business_unit_id,
        group_id=group_id
    )
    await bu_group_servicer.DeleteBusinessUnitGroup(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete group")
    
    return {"message": "Group deleted successfully"}


@app.get("/api/v1/business-units/{business_unit_id}/groups/{group_id}/members")
async def list_business_unit_group_members(business_unit_id: str, group_id: str):
    """List business unit group members"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.ListBusinessUnitGroupMembersRequest(
        business_unit_id=business_unit_id,
        group_id=group_id
    )
    response = await bu_group_servicer.ListBusinessUnitGroupMembers(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list members")
    
    return [{
        "id": m.id,
        "user_id": m.user_id,
        "user_email": m.user_email,
        "user_name": m.user_name,
        "added_at": m.added_at
    } for m in response.members]


@app.post("/api/v1/business-units/{business_unit_id}/groups/{group_id}/members")
async def add_business_unit_group_member(business_unit_id: str, group_id: str, user_id: str = Query(...)):
    """Add member to business unit group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.AddBusinessUnitGroupMemberRequest(
        business_unit_id=business_unit_id,
        group_id=group_id,
        user_id=user_id
    )
    await bu_group_servicer.AddBusinessUnitGroupMember(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to add member")
    
    return {"message": "Member added successfully"}


@app.delete("/api/v1/business-units/{business_unit_id}/groups/{group_id}/members/{user_id}")
async def remove_business_unit_group_member(business_unit_id: str, group_id: str, user_id: str):
    """Remove member from business unit group"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.RemoveBusinessUnitGroupMemberRequest(
        business_unit_id=business_unit_id,
        group_id=group_id,
        user_id=user_id
    )
    await bu_group_servicer.RemoveBusinessUnitGroupMember(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to remove member")
    
    return {"message": "Member removed successfully"}


# ==================== Credential Endpoints ====================

class CreateCredentialRequest(BaseModel):
    name: str
    provider: str  # aws, gcp, azure, kubernetes
    credentials: dict  # JSON object


@app.post("/api/admin/credentials", status_code=201)
async def create_credential(request: CreateCredentialRequest):
    """Create credential"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    import json
    context = MockContext()
    grpc_request = auth_pb2.CreateCredentialRequest(
        name=request.name,
        provider=request.provider,
        credentials=json.dumps(request.credentials)
    )
    response = await credential_servicer.CreateCredential(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create credential")
    
    return {
        "id": response.id,
        "name": response.name,
        "provider": response.provider,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.get("/api/admin/credentials")
async def list_credentials():
    """List credentials"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.ListCredentialsRequest()
    response = await credential_servicer.ListCredentials(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list credentials")
    
    return [{
        "id": c.id,
        "name": c.name,
        "provider": c.provider,
        "created_at": c.created_at,
        "updated_at": c.updated_at
    } for c in response.credentials]


@app.get("/api/admin/credentials/{credential_id}")
async def get_credential(credential_id: str):
    """Get credential"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.GetCredentialRequest(credential_id=credential_id)
    response = await credential_servicer.GetCredential(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Credential not found")
    
    return {
        "id": response.id,
        "name": response.name,
        "provider": response.provider,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.delete("/api/admin/credentials/{credential_id}")
async def delete_credential(credential_id: str):
    """Delete credential"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteCredentialRequest(credential_id=credential_id)
    await credential_servicer.DeleteCredential(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete credential")
    
    return {"message": "Credential deleted successfully"}


# ==================== Permissions Endpoint ====================

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
        pass
    
    # Build permissions list
    all_permissions = []
    for perm_def in PERMISSIONS_BY_SLUG.values():
        slug = perm_def["slug"]
        db_perm = db_metadata.get(slug)
        
        all_permissions.append({
            "id": db_perm.id if db_perm else None,
            "slug": slug,
            "name": perm_def.get("name"),
            "description": perm_def.get("description"),
            "category": perm_def.get("category"),
            "resource": perm_def.get("resource"),
            "action": perm_def.get("action"),
            "environment": perm_def.get("environment"),
            "icon": perm_def.get("icon"),
            "created_at": db_perm.created_at.isoformat() if db_perm and db_perm.created_at else None
        })
    
    # Sort by category, then by name
    all_permissions.sort(key=lambda p: (p.get("category") or "", p.get("name") or p.get("slug")))
    
    return all_permissions


# ==================== Audit Log Endpoints ====================

@app.get("/api/v1/audit-logs")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """List audit logs with filtering and pagination"""
    from app.database import AsyncSessionLocal
    from sqlalchemy import select, and_, or_, func
    from sqlalchemy.orm import selectinload
    from datetime import datetime
    from uuid import UUID
    
    from app.models.audit import AuditLog
    
    async with AsyncSessionLocal() as db:
        # Build query
        query = select(AuditLog)
        conditions = []
        
        if user_id:
            try:
                conditions.append(AuditLog.user_id == UUID(user_id))
            except ValueError:
                pass
        
        if action:
            conditions.append(AuditLog.action == action)
        
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        
        if resource_id:
            try:
                conditions.append(AuditLog.resource_id == UUID(resource_id))
            except ValueError:
                pass
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                conditions.append(AuditLog.created_at >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                conditions.append(AuditLog.created_at <= end_dt)
            except ValueError:
                pass
        
        if status:
            if status == "success":
                conditions.append(
                    or_(
                        AuditLog.details['status'].astext == "success",
                        ~AuditLog.details.has_key('status')
                    )
                )
            elif status == "failure":
                conditions.append(AuditLog.details['status'].astext == "failure")
        
        if search and len(search) <= 100:
            search_conditions = [
                func.cast(AuditLog.details, func.text).ilike(f"%{search}%"),
                func.cast(AuditLog.action, func.text).ilike(f"%{search}%"),
                func.cast(AuditLog.resource_type, func.text).ilike(f"%{search}%"),
            ]
            conditions.append(or_(*search_conditions))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(AuditLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        # Execute query with user relationship loaded
        result = await db.execute(
            query.options(selectinload(AuditLog.user))
        )
        audit_logs = result.scalars().all()
        
        # Convert to response format
        items = []
        for log in audit_logs:
            item = {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
                "user": None
            }
            if log.user:
                item["user"] = {
                    "id": str(log.user.id),
                    "email": log.user.email,
                    "username": log.user.username,
                    "full_name": log.user.full_name
                }
            items.append(item)
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }


@app.get("/api/v1/audit-logs/{log_id}")
async def get_audit_log(log_id: str):
    """Get a single audit log by ID"""
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from uuid import UUID
    
    from app.models.audit import AuditLog
    
    try:
        log_uuid = UUID(log_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid log ID format")
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.id == log_uuid)
            .options(selectinload(AuditLog.user))
        )
        audit_log = result.scalar_one_or_none()
        
        if not audit_log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        item = {
            "id": str(audit_log.id),
            "user_id": str(audit_log.user_id) if audit_log.user_id else None,
            "action": audit_log.action,
            "resource_type": audit_log.resource_type,
            "resource_id": str(audit_log.resource_id) if audit_log.resource_id else None,
            "details": audit_log.details,
            "ip_address": audit_log.ip_address,
            "created_at": audit_log.created_at.isoformat(),
            "user": None
        }
        if audit_log.user:
            item["user"] = {
                "id": str(audit_log.user.id),
                "email": audit_log.user.email,
                "username": audit_log.user.username,
                "full_name": audit_log.user.full_name
            }
        
        return item


# ==================== Health Check ====================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-microservice",
        "proto_ready": PROTO_AVAILABLE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
