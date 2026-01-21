import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.schemas.permissions import PermissionCheckRequest, ServicePermissionCheckRequest
from app.core.dependencies import (
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

@router.get("/permissions")
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


@router.post("/permissions/check")
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


@router.post("/permissions/check-service")
async def check_service_permission(
    request: ServicePermissionCheckRequest
):
    """Internal service permission check (no auth required, internal only)"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
        
    context = MockContext()
    grpc_request = auth_pb2.PermissionCheckRequest(
        user_id=request.user_id,
        permission_slug=request.permission_slug,
        business_unit_id=request.business_unit_id or "",
        organization_id=request.organization_id or ""
    )
    response = await authz_servicer.CheckPermission(grpc_request, context)
    
    if context.code:
        # Don't fail the request on logic errors, just return False allowed
        # But if it's a connection error, maybe 500
        return {
            "has_permission": False,
            "message": context.details or "Permission check failed"
        }
    
    return {
        "has_permission": response.allowed,
        "message": response.message
    }
