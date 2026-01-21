"""
REST to gRPC adapter for plugin microservice
This provides REST API endpoints for all plugin service functionality
"""
import logging
# Configure logging to reduce verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from fastapi import FastAPI, HTTPException, Depends, Query, Header, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel
from typing import Optional, List, Dict
import grpc
import json

logger = logging.getLogger(__name__)

from app.config import settings
from app.grpc.plugin_servicer import PluginServicer
from app.services.plugin_service import plugin_service
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# Import generated proto modules
try:
    from proto import plugin_pb2, plugin_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    plugin_pb2 = None
    plugin_pb2_grpc = None

app = FastAPI(title="Plugin Service REST API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage path for plugins
STORAGE_PATH = os.environ.get("PLUGINS_STORAGE_PATH", "/app/storage/plugins")


# Request/Response models
class RequestPluginAccessRequest(BaseModel):
    note: Optional[str] = None


class GrantPluginAccessRequest(BaseModel):
    user_id: str


class RejectPluginAccessRequest(BaseModel):
    user_id: str


class ProvisionPluginRequest(BaseModel):
    plugin_id: str
    version: str
    inputs: Dict
    environment: str
    tags: Optional[Dict] = None
    deployment_name: Optional[str] = None
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    business_unit_id: Optional[str] = None
    organization_id: Optional[str] = None


# Create servicer instance
plugin_servicer = PluginServicer()


class MockContext:
    """Mock gRPC context for REST adapter"""
    def __init__(self, metadata=None):
        self.code = None
        self.details = None
        self.metadata = metadata or []
    
    def set_code(self, code):
        self.code = code
    
    def set_details(self, details):
        self.details = details
        
    def invocation_metadata(self):
        return self.metadata


async def _get_user_info_from_token(token: Optional[str]) -> Optional[Dict]:
    """Extract user info from token by calling auth-service"""
    if not token:
        return None
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://auth-service:8000/api/v1/auth/validate",
                json={"token": token},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                # Also fetch full user data to get is_admin and active_business_unit_id
                user_id = data.get("user_id")
                if user_id:
                    user_response = await client.get(
                        f"http://auth-service:8000/api/v1/users/{user_id}",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=5.0
                    )
                    if user_response.status_code == 200:
                        user_details = user_response.json()
                        return {
                            "token": token,
                            "user_id": user_id,
                            "email": user_details.get("email"),
                            "is_admin": user_details.get("is_admin", False),
                            "active_business_unit_id": user_details.get("active_business_unit_id"),
                            "organization_id": user_details.get("organization_id")
                        }
                    else:
                        logger.warning(f"Failed to get user details for {user_id}: {user_response.status_code}")
                
                # Fallback to info from validate_token if user details fails
                return {
                    "token": token,
                    "user_id": user_id,
                    "email": data.get("email"),
                    "is_admin": False,
                    "active_business_unit_id": None,
                    "organization_id": data.get("organization_id")
                }
    except Exception as e:
        print(f"Error validating token: {e}")
    return None


async def _get_user_email_from_token(token: Optional[str]) -> Optional[str]:
    """Extract user email from token by calling auth-service"""
    if not token:
        return None
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://auth-service:8000/api/v1/auth/validate",
                json={"token": token},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("email")
    except Exception as e:
        print(f"Error validating token: {e}")
    return None


def _get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header"""
    if authorization:
        if authorization.startswith("Bearer "):
            return authorization[7:]
        elif authorization.startswith("bearer "):
            return authorization[7:]
    return None


async def verify_token(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Dependency to verify token and return user info.
    Raises HTTPException(401) if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
    user_info = await _get_user_info_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    return user_info


# ==================== Plugin CRUD Endpoints ====================

@app.get("/api/v1/plugins")
async def list_plugins(
    business_unit_id: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token),
    authorization: Optional[str] = Header(None)
):
    """List all plugins"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # User is already authenticated via verify_token dependency
    # current_user_info contains user_id, email, etc.
    user_id = current_user_info["user_id"]
    token = _get_token_from_header(authorization)
    
    # Check if user is super admin FIRST - super admins should NOT see organization-specific resources
    # BUT Foundry super admins CAN see their own organization's resources
    is_super_admin = False
    is_foundry = False
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"http://auth-service:8000/api/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"} if token else {},
                timeout=5.0
            )
            if user_response.status_code == 200:
                user_data = user_response.json()
                roles = user_data.get("roles", [])
                is_super_admin = any(role.lower() in ["super-admin", "platform-admin"] for role in roles)
                # Check if user belongs to Foundry organization
                org_slug = user_data.get("organization", {}).get("slug") if isinstance(user_data.get("organization"), dict) else None
                if not org_slug:
                    # Try to get from organization_id
                    org_id = user_data.get("organization_id")
                    if org_id:
                        org_response = await client.get(
                            f"http://auth-service:8000/api/v1/organizations/{org_id}",
                            headers={"Authorization": f"Bearer {current_user_info['token']}"} if current_user_info.get("token") else {},
                            timeout=5.0
                        )
                        if org_response.status_code == 200:
                            org_data = org_response.json()
                            org_slug = org_data.get("slug")
                is_foundry = org_slug == "foundry"
    except Exception as e:
        logger.error(f"Error checking super admin status: {e}")
    
    # Super admins should NOT see organization-specific resources from OTHER organizations
    # BUT Foundry super admins CAN see their own organization's resources
    # Everyone is filtered by their own organization_id
    organization_id = current_user_info.get("organization_id")

    actual_business_unit_id = business_unit_id
    
    # If not in token, fetch from auth-service
    if not organization_id or not actual_business_unit_id:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"} if token else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    if not organization_id:
                        organization_id = user_data.get("organization_id")
                    if not actual_business_unit_id:
                        active_bu = user_data.get("active_business_unit_id")
                        actual_business_unit_id = active_bu if active_bu else ""
        except Exception as e:
            logger.error(f"Error fetching user info for isolation: {e}")
    
    if not organization_id:
        # Fallback for old tokens or broken setups - don't allow global access
        logger.warning(f"WARNING: No organization_id found for user {user_id}, returning empty plugin list")
        return []


    
    logger.info(f"DEBUG: Calling ListPlugins with organization_id: {organization_id}")
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.ListPluginsRequest(
        user_id=user_id,
        business_unit_id=actual_business_unit_id or "",
        organization_id=organization_id or ""
    )
    response = await plugin_servicer.ListPlugins(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list plugins")
    
    def get_icon_url(plugin_id: str, versions: list) -> str:
        """Construct icon URL from manifest"""
        if versions:
            latest = versions[0]
            manifest = json.loads(latest.manifest) if latest.manifest else {}
            icon_path = manifest.get("icon")
            if icon_path:
                return f"/storage/plugins/{plugin_id}/{latest.version}/{icon_path}"
        return ""
    
    return [{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "author": p.author,
        "is_locked": p.is_locked,
        "deployment_type": p.deployment_type,
        "has_access": p.has_access,
        "has_pending_request": p.has_pending_request,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
        "cloud_provider": p.cloud_provider,
        "category": p.category,
        "latest_version": p.latest_version,
        "icon": get_icon_url(p.id, list(p.versions)),
        "versions": [
            {
                "id": v.id,
                "version": v.version,
                "manifest": json.loads(v.manifest) if v.manifest else {},
                "created_at": v.created_at
            }
            for v in p.versions
        ]
    } for p in response.plugins]


@app.get("/api/v1/plugins/{plugin_id}")
async def get_plugin(
    plugin_id: str,
    user_id: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token),
    authorization: Optional[str] = Header(None)
):
    """Get plugin by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id from query or from authorization token
    actual_user_id = user_id
    if not actual_user_id:
        actual_user_id = current_user_info["user_id"]
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get active business unit and organization_id from user profile if not provided
    actual_business_unit_id = business_unit_id
    organization_id = current_user_info.get("organization_id")
    
    if not actual_business_unit_id or not organization_id:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{actual_user_id}",
                    headers={"Authorization": f"Bearer {current_user_info['token']}"} if current_user_info.get("token") else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    if not actual_business_unit_id:
                        active_bu = user_data.get("active_business_unit_id")
                        actual_business_unit_id = active_bu if active_bu else ""
                    if not organization_id:
                        organization_id = user_data.get("organization_id")
                    print(f"DEBUG: Fetched active_business_unit_id: {actual_business_unit_id}, organization_id: {organization_id} for user {actual_user_id}")
        except Exception as e:
            print(f"Error fetching user info: {e}")
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID is required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.GetPluginRequest(
        plugin_id=plugin_id,
        user_id=actual_user_id,
        business_unit_id=actual_business_unit_id or "",
        organization_id=organization_id or ""
    )
    response = await plugin_servicer.GetPlugin(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Plugin not found")
    
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "author": response.author,
        "is_locked": response.is_locked,
        "deployment_type": response.deployment_type,
        "has_access": response.has_access,
        "has_pending_request": response.has_pending_request,
        "created_at": response.created_at,
        "updated_at": response.updated_at,
        "git_repo_url": response.git_repo_url if response.git_repo_url else None,
        "git_branch": response.git_branch if response.git_branch else None,
        "versions": [
            {
                "id": v.id,
                "version": v.version,
                "manifest": json.loads(v.manifest) if v.manifest else {},
                "created_at": v.created_at
            }
            for v in response.versions
        ]
    }


@app.delete("/api/v1/plugins/{plugin_id}")
async def delete_plugin(
    plugin_id: str,
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """Delete plugin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id and organization_id from query or from authorization token
    actual_user_id = user_id
    organization_id = None
    
    if not actual_user_id:
        token = _get_token_from_header(authorization)
        if token:
            user_info = await _get_user_info_from_token(token)
            if user_info:
                actual_user_id = user_info["user_id"]
                organization_id = user_info.get("organization_id")
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not organization_id:
        # Fetch organization_id from auth-service
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{actual_user_id}",
                    headers={"Authorization": f"Bearer {user_info['token']}"} if user_info.get("token") else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    organization_id = user_data.get("organization_id")
        except Exception as e:
            print(f"Error fetching user organization: {e}")
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID is required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {token}")]) if token else MockContext()
    grpc_request = plugin_pb2.DeletePluginRequest(
        plugin_id=plugin_id,
        user_id=actual_user_id,
        organization_id=organization_id or ""
    )
    await plugin_servicer.DeletePlugin(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete plugin")
    
    return {"message": "Plugin deleted successfully"}


@app.put("/api/v1/plugins/{plugin_id}/lock")
async def lock_plugin(
    plugin_id: str,
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """Lock plugin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id and organization_id from query or from authorization token
    actual_user_id = user_id
    organization_id = None
    
    if not actual_user_id:
        token = _get_token_from_header(authorization)
        if token:
            user_info = await _get_user_info_from_token(token)
            if user_info:
                actual_user_id = user_info["user_id"]
                organization_id = user_info.get("organization_id")
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not organization_id:
        # Fetch organization_id from auth-service
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{actual_user_id}",
                    headers={"Authorization": f"Bearer {user_info['token']}"} if user_info.get("token") else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    organization_id = user_data.get("organization_id")
        except Exception as e:
            print(f"Error fetching user organization: {e}")
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID is required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {token}")]) if token else MockContext()
    grpc_request = plugin_pb2.LockPluginRequest(
        plugin_id=plugin_id,
        user_id=actual_user_id,
        organization_id=organization_id or ""
    )
    await plugin_servicer.LockPlugin(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to lock plugin")
    
    return {"message": "Plugin locked successfully", "is_locked": True}


@app.put("/api/v1/plugins/{plugin_id}/unlock")
async def unlock_plugin(
    plugin_id: str,
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """Unlock plugin"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id and organization_id from query or from authorization token
    actual_user_id = user_id
    organization_id = None
    
    if not actual_user_id:
        token = _get_token_from_header(authorization)
        if token:
            user_info = await _get_user_info_from_token(token)
            if user_info:
                actual_user_id = user_info["user_id"]
                organization_id = user_info.get("organization_id")
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not organization_id:
        # Fetch organization_id from auth-service
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{actual_user_id}",
                    headers={"Authorization": f"Bearer {user_info['token']}"} if user_info.get("token") else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    organization_id = user_data.get("organization_id")
        except Exception as e:
            print(f"Error fetching user organization: {e}")
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID is required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {token}")]) if token else MockContext()
    grpc_request = plugin_pb2.UnlockPluginRequest(
        plugin_id=plugin_id,
        user_id=actual_user_id,
        organization_id=organization_id or ""
    )
    await plugin_servicer.UnlockPlugin(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to unlock plugin")
    
    return {"message": "Plugin unlocked successfully", "is_locked": False}


# ==================== Plugin Versions Endpoints ====================

@app.get("/api/v1/plugins/{plugin_id}/versions")
async def list_plugin_versions(
    plugin_id: str,
    current_user_info: Dict = Depends(verify_token)
):
    """List plugin versions"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.ListPluginVersionsRequest(plugin_id=plugin_id)
    response = await plugin_servicer.ListPluginVersions(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list versions")
    
    return [{
        "id": v.id,
        "plugin_id": v.plugin_id,
        "version": v.version,
        "manifest": json.loads(v.manifest) if v.manifest else {},
        "storage_path": v.storage_path,
        "git_repo_url": v.git_repo_url,
        "git_branch": v.git_branch,
        "template_repo_url": v.template_repo_url,
        "template_path": v.template_path,
        "created_at": v.created_at
    } for v in response.versions]


@app.get("/api/v1/plugins/{plugin_id}/versions/{version}")
async def get_plugin_version(
    plugin_id: str, 
    version: str,
    current_user_info: Dict = Depends(verify_token)
):
    """Get plugin version"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.GetPluginVersionRequest(plugin_id=plugin_id, version=version)
    response = await plugin_servicer.GetPluginVersion(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Version not found")
    
    return {
        "id": response.id,
        "plugin_id": response.plugin_id,
        "version": response.version,
        "manifest": json.loads(response.manifest) if response.manifest else {},
        "storage_path": response.storage_path,
        "git_repo_url": response.git_repo_url,
        "git_branch": response.git_branch,
        "template_repo_url": response.template_repo_url,
        "template_path": response.template_path,
        "created_at": response.created_at
    }


# ==================== Plugin Access Endpoints ====================

@app.post("/api/v1/plugins/{plugin_id}/access/request", status_code=201)
async def request_plugin_access(
    plugin_id: str,
    request: RequestPluginAccessRequest,
    user_id: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token)
):
    """Request plugin access"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id from query or from token
    actual_user_id = user_id or current_user_info.get("user_id")
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.RequestPluginAccessRequest(
        plugin_id=plugin_id,
        user_id=actual_user_id,
        business_unit_id=business_unit_id or "",
        note=request.note or "",
        organization_id=current_user_info.get("organization_id") or ""
    )
    response = await plugin_servicer.RequestPluginAccess(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to request access")
    
    return {
        "id": response.id,
        "plugin_id": response.plugin_id,
        "user_id": response.user_id,
        "status": response.status,
        "note": response.note,
        "requested_at": response.requested_at
    }


@app.post("/api/v1/plugins/{plugin_id}/access/grant")
async def grant_plugin_access(
    plugin_id: str,
    request: GrantPluginAccessRequest,
    granted_by_user_id: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token)
):
    """Grant plugin access"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get granted_by_user_id from query or from token
    actual_granted_by = granted_by_user_id or current_user_info.get("user_id")
    
    if not actual_granted_by:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # business_unit_id will be extracted from the pending request in the service method
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.GrantPluginAccessRequest(
        plugin_id=plugin_id,
        user_id=request.user_id,
        granted_by_user_id=actual_granted_by,
        business_unit_id=business_unit_id or "",  # Optional - service will get from pending request
        organization_id=current_user_info.get("organization_id") or ""
    )
    response = await plugin_servicer.GrantPluginAccess(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to grant access")
    
    return {
        "id": response.id,
        "plugin_id": response.plugin_id,
        "user_id": response.user_id,
        "granted_at": response.granted_at
    }


@app.post("/api/v1/plugins/{plugin_id}/access/reject")
async def reject_plugin_access(
    plugin_id: str,
    request: RejectPluginAccessRequest,
    rejected_by_user_id: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token)
):
    """Reject plugin access request"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get rejected_by_user_id from query or from token
    actual_rejected_by = rejected_by_user_id or current_user_info.get("user_id")
    
    if not actual_rejected_by:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.RejectPluginAccessRequest(
        plugin_id=plugin_id,
        user_id=request.user_id,
        rejected_by_user_id=actual_rejected_by,
        organization_id=current_user_info.get("organization_id") or ""
    )
    await plugin_servicer.RejectPluginAccess(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to reject access")
    
    return {"message": "Access request rejected"}


@app.delete("/api/v1/plugins/{plugin_id}/access/{user_id}")
async def revoke_plugin_access(
    plugin_id: str,
    user_id: str,
    revoked_by_user_id: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token)
):
    """Revoke plugin access"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get revoked_by_user_id from query or from token
    actual_revoked_by = revoked_by_user_id or current_user_info.get("user_id")
    
    if not actual_revoked_by:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.RevokePluginAccessRequest(
        plugin_id=plugin_id,
        user_id=user_id,
        revoked_by_user_id=actual_revoked_by,
        organization_id=current_user_info.get("organization_id") or ""
    )
    await plugin_servicer.RevokePluginAccess(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to revoke access")
    
    return {"message": "Access revoked"}


@app.post("/api/v1/plugins/{plugin_id}/access/{user_id}/restore")
async def restore_plugin_access(
    plugin_id: str,
    user_id: str,
    restored_by_user_id: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token)
):
    """Restore plugin access"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get restored_by_user_id from query or from token
    actual_restored_by = restored_by_user_id or current_user_info.get("user_id")
    
    if not actual_restored_by:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.RestorePluginAccessRequest(
        plugin_id=plugin_id,
        user_id=user_id,
        restored_by_user_id=actual_restored_by,
        organization_id=current_user_info.get("organization_id") or ""
    )
    await plugin_servicer.RestorePluginAccess(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=400, detail=context.details or "Failed to restore access")
    
    return {"message": "Access restored"}


@app.get("/api/v1/plugins/access/requests")
async def list_access_requests(
    plugin_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token)
):
    """List access requests (admins see all, BU owners see only their BUs)"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    user_id = current_user_info.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.ListAccessRequestsRequest(
        plugin_id=plugin_id or "",
        status=status or "",
        search=search or "",
        user_id=user_id,  # Pass user_id for filtering
        organization_id=current_user_info.get("organization_id") or ""
    )
    response = await plugin_servicer.ListAccessRequests(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list requests")
    
    return {
        "requests": [{
            "id": r.id,
            "plugin_id": r.plugin_id,
            "user_id": r.user_id,
            "user_email": r.user_email,
            "user_name": r.user_name,
            "status": r.status,
            "note": r.note,
            "requested_at": r.requested_at
        } for r in response.requests],
        "total": response.total
    }


@app.get("/api/v1/plugins/{plugin_id}/access")
async def list_access_grants(
    plugin_id: Optional[str] = None,
    current_user_info: Dict = Depends(verify_token)
):
    """List access grants"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.ListAccessGrantsRequest(plugin_id=plugin_id or "")
    response = await plugin_servicer.ListAccessGrants(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list grants")
    
    return {
        "grants": [{
            "id": g.id,
            "plugin_id": g.plugin_id,
            "user_id": g.user_id,
            "user_email": g.user_email,
            "user_name": g.user_name,
            "granted_at": g.granted_at
        } for g in response.grants],
        "total": response.total
    }


# ==================== Plugin Upload Endpoints ====================

@app.post("/api/v1/plugins/upload", status_code=201)
async def upload_plugin(
    file: UploadFile = File(...),
    git_repo_url: Optional[str] = Form(None),
    git_branch: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    current_user_info: Dict = Depends(verify_token)
):
    """Upload plugin ZIP file"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id from form or from authorization token
    # Always prioritize authenticated user, unless user_id is explicitly passed AND the user is admin (logic not fully here, so safer to just take current user)
    # Actually, let's just use the current authenticated user as the uploader
    actual_user_id = current_user_info["user_id"]
    organization_id = current_user_info.get("organization_id")
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get organization_id if not in token
    if not organization_id:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{actual_user_id}",
                    headers={"Authorization": f"Bearer {current_user_info['token']}"} if current_user_info.get("token") else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    organization_id = user_data.get("organization_id")
        except Exception as e:
            logger.error(f"Error fetching user organization: {e}")
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID is required for plugin upload")
    
    # Read file content with error handling
    try:
        file_content = await file.read()
        filename = file.filename or "plugin.zip"
        
        if not file_content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Log file size for debugging
        file_size_mb = len(file_content) / (1024 * 1024)
        logger.info(f"Uploading plugin file: {filename}, size: {file_size_mb:.2f} MB")
        
    except Exception as e:
        logger.error(f"Error reading upload file: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    try:
        grpc_request = plugin_pb2.UploadPluginRequest(
            file_content=file_content,
            filename=filename,
            git_repo_url=git_repo_url or "",
            git_branch=git_branch or "",
            user_id=actual_user_id,
            organization_id=organization_id or ""
        )
        response = await plugin_servicer.UploadPlugin(grpc_request, context)
        
        if context.code:
            status_code = 400 if context.code.value == 3 else 500
            raise HTTPException(status_code=status_code, detail=context.details or "Failed to upload plugin")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading plugin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    return {
        "id": response.id,
        "plugin_id": response.plugin_id,
        "version": response.version,
        "manifest": json.loads(response.manifest) if response.manifest else {},
        "storage_path": response.storage_path,
        "created_at": response.created_at
    }


@app.post("/api/v1/plugins/upload-template", status_code=201)
async def upload_microservice_template(
    plugin_id: str = Form(...),
    name: str = Form(...),
    version: str = Form(...),
    description: str = Form(...),
    template_repo_url: str = Form(...),
    template_path: str = Form(...),
    inputs: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    current_user_info: Dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Upload microservice template"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id and organization_id from form or from authorization token
    actual_user_id = user_id
    organization_id = None
    
    if not actual_user_id:
        actual_user_id = current_user_info["user_id"]
        organization_id = current_user_info.get("organization_id")
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get organization_id if not in token
    if not organization_id:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{actual_user_id}",
                    headers={"Authorization": f"Bearer {current_user_info['token']}"} if current_user_info.get("token") else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    organization_id = user_data.get("organization_id")
        except Exception as e:
            logger.error(f"Error fetching user organization: {e}")
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID is required for plugin upload")
    
    # Parse inputs JSON if provided
    parsed_inputs = None
    if inputs:
        try:
            parsed_inputs = json.loads(inputs)
        except Exception as e:
            logger.error(f"Failed to parse inputs JSON: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON in inputs field: {str(e)}")

    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    response = await plugin_service.upload_microservice_template(
        plugin_id=plugin_id,
        name=name,
        version=version,
        description=description,
        template_repo_url=template_repo_url,
        template_path=template_path,
        author=author or "",
        user_id=actual_user_id,
        organization_id=organization_id,
        db=db,
        inputs=parsed_inputs
    )
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to upload template")
    
    return {
        "id": response["id"],
        "plugin_id": response["plugin_id"],
        "version": response["version"],
        "manifest": json.loads(response["manifest"]) if response.get("manifest") else {},
        "created_at": response["created_at"]
    }


# ==================== Provision Endpoints ====================

@app.post("/api/v1/provision", status_code=202)
async def provision_plugin(
    request: ProvisionPluginRequest,
    current_user_info: Dict = Depends(verify_token)
):
    """Provision plugin infrastructure"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Extract user info from token
    user_id = current_user_info["user_id"]
    user_email = current_user_info.get("email")
    
    if not user_id or not user_email:
         raise HTTPException(status_code=401, detail="Invalid token data")
    
    # Get active business unit from user profile if not provided
    actual_business_unit_id = request.business_unit_id
    if not actual_business_unit_id:
        # Try to get from current_user_info first (it's populated by verify_token)
        actual_business_unit_id = current_user_info.get("active_business_unit_id")
        
        # If still missing, fallback to fetching from auth-service
        if not actual_business_unit_id:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    user_response = await client.get(
                        f"http://auth-service:8000/api/v1/users/{user_id}",
                        headers={"Authorization": f"Bearer {current_user_info['token']}"} if current_user_info.get("token") else {},
                        timeout=5.0
                    )
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        active_bu = user_data.get("active_business_unit_id")
                        actual_business_unit_id = active_bu if active_bu else ""
            except Exception as e:
                print(f"Error fetching user active BU: {e}")
    
    # Get organization_id from token (safe source)
    organization_id = current_user_info.get("organization_id")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.ProvisionPluginRequest(
        plugin_id=request.plugin_id,
        version=request.version,
        inputs=json.dumps(request.inputs),
        environment=request.environment,
        tags=json.dumps(request.tags) if request.tags else "{}",
        deployment_name=request.deployment_name or "",
        cost_center=request.cost_center or "",
        project_code=request.project_code or "",
        user_id=user_id,
        user_email=user_email,
        business_unit_id=actual_business_unit_id or "",
        organization_id=organization_id or ""
    )
    response = await plugin_servicer.ProvisionPlugin(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to provision")
    
    return {
        "job_id": response.job_id,
        "deployment_id": response.deployment_id,
        "status": response.status,
        "message": response.message
    }


@app.get("/api/v1/provision/jobs/{job_id}")
async def get_job(job_id: str, current_user_info: Dict = Depends(verify_token)):
    """Get job by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.GetJobRequest(job_id=job_id)
    response = await plugin_servicer.GetJob(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Job not found")
    
    return {
        "id": response.id,
        "plugin_version_id": response.plugin_version_id,
        "deployment_id": response.deployment_id,
        "status": response.status,
        "triggered_by": response.triggered_by,
        "inputs": json.loads(response.inputs) if response.inputs else {},
        "outputs": json.loads(response.outputs) if response.outputs else {},
        "retry_count": response.retry_count,
        "error_state": response.error_state,
        "error_message": response.error_message,
        "created_at": response.created_at,
        "finished_at": response.finished_at
    }


@app.get("/api/v1/provision/jobs")
async def list_jobs(
    business_unit_id: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    status: Optional[str] = Query(None),
    job_id: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user_info: Dict = Depends(verify_token)
):
    """List jobs"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Extract user info from token
    user_info = current_user_info
    
    if not user_info:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    user_organization_id = user_info.get("organization_id")
    
    # Check if user is super admin
    is_super_admin = False
    if user_organization_id:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{user_id}",
                    headers={"Authorization": f"Bearer {current_user_info.get('token', '')}"} if current_user_info.get('token') else {},
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    roles = user_data.get("roles", [])
                    is_super_admin = any(role.lower() in ["super-admin", "platform-admin"] for role in roles)
        except Exception:
            pass
    
    # For organization admins, filter by organization's business units
    # For super admins, allow all business units
    actual_business_unit_id = business_unit_id
    if not actual_business_unit_id and not is_admin:
        actual_business_unit_id = user_info.get("active_business_unit_id") or ""
    elif is_admin and not is_super_admin and user_organization_id and not business_unit_id:
        # Organization admin: get all business units for their organization
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                bu_response = await client.get(
                    f"http://auth-service:8000/api/v1/business-units",
                    params={"organization_id": user_organization_id},
                    headers={"Authorization": f"Bearer {current_user_info.get('token', '')}"} if current_user_info.get('token') else {},
                    timeout=5.0
                )
                if bu_response.status_code == 200:
                    bus = bu_response.json()
                    # If only one BU, use it; otherwise we'll filter in the service layer
                    if len(bus) == 1:
                        actual_business_unit_id = bus[0]["id"]
        except Exception:
            pass
    
    # Determine organization_id filter
    org_id_filter = None
    if not is_super_admin:
        org_id_filter = user_organization_id

    try:
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            result = await plugin_service.list_jobs(
                user_id=user_id,
                business_unit_id=actual_business_unit_id,
                organization_id=org_id_filter,
                skip=skip,
                limit=limit,
                status=status,
                db=db
            )
            
            # Extract jobs from result
            jobs_data = result.get("jobs", [])
            
            # Apply client-side filters (legacy support)
            filtered_jobs = jobs_data
            if job_id:
                filtered_jobs = [j for j in filtered_jobs if j["id"] == job_id]
            if email:
                filtered_jobs = [j for j in filtered_jobs if email.lower() in j["triggered_by"].lower()]
            if start_date or end_date:
                final_filtered = []
                for j in filtered_jobs:
                    job_date = j.get("created_at")
                    if job_date:
                        try:
                            from datetime import datetime
                            # Handle empty string or invalid format gracefully
                            job_dt = datetime.fromisoformat(job_date.replace('Z', '+00:00'))
                            
                            if start_date:
                                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                                if job_dt < start_dt:
                                    continue
                            if end_date:
                                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                if job_dt > end_dt:
                                    continue
                            final_filtered.append(j)
                        except Exception as e:
                            # Log error but include job to be safe
                            # logger.warning(f"Date parsing error: {e}")
                            final_filtered.append(j)
                    else:
                        final_filtered.append(j)
                filtered_jobs = final_filtered
            
            return {
                "items": filtered_jobs,
                "jobs": filtered_jobs,
                "total": result.get("total", 0),
                "skip": result.get("skip", skip),
                "limit": result.get("limit", limit)
            }
    except Exception as e:
        import traceback
        print(f"Error in list_jobs endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
            


@app.get("/api/v1/provision/jobs/{job_id}/logs")
async def get_job_logs(
    job_id: str, 
    skip: int = Query(0), 
    limit: int = Query(100),
    current_user_info: Dict = Depends(verify_token)
):
    """Get job logs"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Validate job_id
    if not job_id or job_id == "undefined" or job_id.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.GetJobLogsRequest(job_id=job_id, skip=skip, limit=limit)
    response = await plugin_servicer.GetJobLogs(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Job not found")
    
    return {
        "logs": [{
            "id": log.id,
            "job_id": log.job_id,
            "timestamp": log.timestamp,
            "level": log.level,
            "message": log.message
        } for log in response.logs],
        "total": response.total
    }


@app.delete("/api/v1/provision/jobs/{job_id}")
async def delete_job(job_id: str, user_id: str = Query(...)):
    """Delete job"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext(metadata=[('authorization', f"Bearer {current_user_info['token']}")]) if current_user_info.get("token") else MockContext()
    grpc_request = plugin_pb2.DeleteJobRequest(job_id=job_id, user_id=user_id)
    await plugin_servicer.DeleteJob(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Job not found")
    
    return {"message": "Job deleted successfully"}


@app.get("/storage/plugins/{plugin_id}/{version}/{asset_path:path}")
async def serve_plugin_asset(plugin_id: str, version: str, asset_path: str):
    """Serve plugin assets (icons, etc.) from the extracted directory"""
    # Try both extracted and direct paths
    paths_to_try = [
        os.path.join(STORAGE_PATH, plugin_id, version, "extracted", asset_path),
        os.path.join(STORAGE_PATH, plugin_id, version, asset_path),
    ]
    
    for file_path in paths_to_try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
    
    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "plugin-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=300,  # 5 minutes keep-alive timeout
        timeout_graceful_shutdown=30,
        limit_concurrency=100,
        limit_max_requests=1000
    )
