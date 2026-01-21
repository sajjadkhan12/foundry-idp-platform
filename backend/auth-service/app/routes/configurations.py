import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.schemas.configurations import SetConfigurationRequest
from app.core.dependencies import config_servicer, MockContext, auth_pb2, verify_token, PROTO_AVAILABLE
from app.database import AsyncSessionLocal
from app.models.rbac import User
from sqlalchemy.future import select
from app.utils.helpers import is_platform_admin
from app.core.casbin import get_enforcer

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/configurations")
async def list_configurations(
    business_unit_id: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """List configurations for current organization/BU"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user's organization
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        organization_id = str(current_user.organization_id)
        
        context = MockContext()
        grpc_request = auth_pb2.ListConfigurationsRequest(
            organization_id=organization_id,
            business_unit_id=business_unit_id or ""
        )
        response = await config_servicer.ListConfigurations(grpc_request, context)
        
        if context.code:
            raise HTTPException(status_code=500, detail=context.details or "Failed to list configurations")
        
        return response.configurations


@router.post("/configurations")
async def set_configuration(
    request: SetConfigurationRequest,
    current_user_id: str = Depends(verify_token)
):
    """Set configuration value"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user's organization and check permissions
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Only org admins can set configurations
        enforcer = get_enforcer()
        if not await is_platform_admin(current_user, db, enforcer):
            raise HTTPException(status_code=403, detail="Only organization administrators can set configurations")
        
        organization_id = str(current_user.organization_id)
        
        context = MockContext()
        grpc_request = auth_pb2.SetConfigurationRequest(
            organization_id=organization_id,
            config_key=request.config_key,
            config_value=request.config_value,
            user_id=current_user_id,
            business_unit_id=request.business_unit_id or ""
        )
        response = await config_servicer.SetConfiguration(grpc_request, context)
        
        if context.code:
            raise HTTPException(status_code=400, detail=context.details or "Failed to set configuration")
        
        return {
            "config_key": response.config_key,
            "organization_id": response.organization_id,
            "business_unit_id": response.business_unit_id or None,
            "is_active": response.is_active
        }


@router.get("/configurations/{config_key}")
async def get_configuration(
    config_key: str,
    business_unit_id: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """Get configuration value"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user's organization
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        organization_id = str(current_user.organization_id)
        
        context = MockContext()
        grpc_request = auth_pb2.GetConfigurationRequest(
            organization_id=organization_id,
            config_key=config_key,
            business_unit_id=business_unit_id or ""
        )
        response = await config_servicer.GetConfiguration(grpc_request, context)
        
        if context.code:
            if context.code.value == 5:  # NOT_FOUND
                raise HTTPException(status_code=404, detail=context.details or "Configuration not found")
            raise HTTPException(status_code=400, detail=context.details or "Failed to get configuration")
        
        return {
            "config_key": response.config_key,
            "config_value": response.config_value,
            "organization_id": response.organization_id,
            "business_unit_id": response.business_unit_id or None
        }


@router.delete("/configurations/{config_key}")
async def delete_configuration(
    config_key: str,
    business_unit_id: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """Delete configuration"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user's organization and check permissions
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Only org admins can delete configurations
        enforcer = get_enforcer()
        if not await is_platform_admin(current_user, db, enforcer):
            raise HTTPException(status_code=403, detail="Only organization administrators can delete configurations")
        
        organization_id = str(current_user.organization_id)
        
        context = MockContext()
        grpc_request = auth_pb2.DeleteConfigurationRequest(
            organization_id=organization_id,
            config_key=config_key,
            business_unit_id=business_unit_id or ""
        )
        await config_servicer.DeleteConfiguration(grpc_request, context)
        
        if context.code:
            if context.code.value == 5:  # NOT_FOUND
                raise HTTPException(status_code=404, detail=context.details or "Configuration not found")
            raise HTTPException(status_code=400, detail=context.details or "Failed to delete configuration")
        
        return {"message": "Configuration deleted successfully"}
