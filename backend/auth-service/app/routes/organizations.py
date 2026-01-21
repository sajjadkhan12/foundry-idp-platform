import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.schemas.organizations import CreateOrganizationRequest, UpdateOrganizationRequest, CreateOrganizationWithAdminRequest
from app.core.dependencies import org_servicer, MockContext, auth_pb2, verify_token, PROTO_AVAILABLE
from app.database import AsyncSessionLocal
from app.models.rbac import User, Organization
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.utils.helpers import is_super_admin
from app.core.casbin import get_enforcer

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/organizations", status_code=201)
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


@router.get("/organizations")
async def list_organizations(
    skip: int = Query(0), 
    limit: int = Query(100),
    current_user_id: str = Depends(verify_token)
):
    """List organizations"""
    # Check if user is super admin
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        enforcer = get_enforcer()
        if not await is_super_admin(current_user, db, enforcer):
            raise HTTPException(status_code=403, detail="Only super admins can list all organizations")

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


@router.get("/organizations/{org_id}")
async def get_organization(org_id: str, current_user_id: str = Depends(verify_token)):
    """Get organization by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Check authorization: super admin can access any org, others only their own
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # If not super admin, check if accessing own organization
        if not is_super:
            if str(current_user.organization_id) != org_id:
                raise HTTPException(status_code=403, detail="Access denied")
    
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


@router.post("/organizations/create-with-admin", status_code=201)
async def create_organization_with_admin(
    request: CreateOrganizationWithAdminRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create organization with admin user (Super Admin only)"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Check if user is super admin
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        if not is_super:
            raise HTTPException(status_code=403, detail="Only super admins can create organizations")
    
    # Create gRPC request and call servicer (servicer will create its own DB session)
    context = MockContext()
    grpc_request = auth_pb2.CreateOrganizationWithAdminRequest(
        name=request.name,
        slug=request.slug,
        description=request.description or "",
        admin_email=request.admin_email,
        admin_username=request.admin_username,
        admin_password=request.admin_password,
        admin_full_name=request.admin_full_name or ""
    )
    response = await org_servicer.CreateOrganizationWithAdmin(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create organization")
    
    return {
        "organization": {
            "id": response.organization.id,
            "name": response.organization.name,
            "slug": response.organization.slug,
            "description": response.organization.description,
            "is_active": response.organization.is_active,
            "created_at": response.organization.created_at,
            "updated_at": response.organization.updated_at
        },
        "admin_user": {
            "id": response.admin_user.id,
            "email": response.admin_user.email,
            "username": response.admin_user.username,
            "full_name": response.admin_user.full_name
        },
        "default_business_unit": {
            "id": response.default_business_unit.id,
            "name": response.default_business_unit.name,
            "slug": response.default_business_unit.slug,
            "description": response.default_business_unit.description,
            "organization_id": response.default_business_unit.organization_id,
            "is_active": response.default_business_unit.is_active
        }
    }


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Delete organization (Super Admin only)"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Check if user is super admin
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == uuid.UUID(current_user_id)))
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        enforcer = get_enforcer()
        if not await is_super_admin(current_user, db, enforcer):
            raise HTTPException(status_code=403, detail="Only super admins can delete organizations")
    
    context = MockContext()
    grpc_request = auth_pb2.DeleteOrganizationRequest(organization_id=org_id)
    await org_servicer.DeleteOrganization(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 400
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete organization")
    
    return {"message": "Organization deleted successfully"}
