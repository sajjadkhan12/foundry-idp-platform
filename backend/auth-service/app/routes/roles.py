import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.schemas.roles import CreateRoleRequest, UpdateRoleRequest, AssignRoleRequest
from app.core.dependencies import role_servicer, MockContext, auth_pb2, verify_token, PROTO_AVAILABLE
from app.database import AsyncSessionLocal
from app.models.rbac import User, Role
from sqlalchemy.future import select
from app.utils.helpers import is_super_admin
from app.core.casbin import get_enforcer
from app.core.organization import get_user_organization
from app.services.role_service import role_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/roles")
async def list_roles(
    platform_roles_only: bool = Query(False),
    current_user_id: str = Depends(verify_token)
):
    """List roles - filtered by organization context"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    is_super = False
    organization_id = None
    is_foundry = False
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if current_user:
            enforcer = get_enforcer()
            is_super = await is_super_admin(current_user, db, enforcer)
            # Get user's organization for filtering (even for super admins)
            org = await get_user_organization(current_user, db)
            if org:
                organization_id = str(org.id)
                is_foundry = org.slug == "foundry"
    
    # SaaS Manager Visibility: Super admins only see roles within their own organization context
    # organization_id is already set above via get_user_organization
    if not organization_id:
        return []

    async with AsyncSessionLocal() as db:
        # For organization admins (including Foundry super admins): show their org roles + system roles
        logger.info(f"DEBUG list_roles: organization_id={organization_id}, is_foundry={is_foundry}, is_super={is_super}")
        roles_list = await role_service.list_roles(
            platform_roles_only=platform_roles_only,
            db=db,
            organization_id=organization_id,
            include_system_roles=True  # Org admins see system roles (filtered by service)
        )
        logger.info(f"DEBUG list_roles: service returned {len(roles_list)} roles")
    
    # For Foundry organization, the service already returns all system roles + org roles
    # So we can return the list directly (service handles Foundry special case)
    if is_foundry:
        return roles_list
    
    # Additional filtering for other organizations
    if organization_id:
        filtered_roles = []
        org_id_str = str(organization_id)
        for r in roles_list:
            role_org_id = r.get("organization_id")
            role_name = r.get("name", "")
            is_platform = r.get("is_platform_role", False)
            
            # For other organizations: exclude system platform roles (platform-admin, super-admin) - only show organization-admin
            if is_platform and role_name not in ["organization-admin"]:
                continue
            
            # Include: organization-admin system role OR business unit roles from this organization
            if role_name == "organization-admin":
                # Include organization-admin system role
                filtered_roles.append(r)
            elif not is_platform and role_org_id:
                # Include business unit roles from this organization (compare as strings)
                if str(role_org_id) == org_id_str:
                    filtered_roles.append(r)
        return filtered_roles
    
    return roles_list


@router.get("/roles/{role_id}")
async def get_role(
    role_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Get role by ID - verify it belongs to user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    async with AsyncSessionLocal() as db:
        # Get current user
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get role
        role_result = await db.execute(
            select(Role).where(Role.id == uuid.UUID(role_id))
        )
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # Organization admins can only access roles from their organization or organization-admin system role
        if role.organization_id is None:
            # System role - only allow organization-admin
            if role.name != "organization-admin":
                raise HTTPException(status_code=403, detail="Access denied: System roles are not accessible")
        elif role.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Role belongs to a different organization")
    
    # Use service to get role details
    async with AsyncSessionLocal() as db:
        role_data = await role_service.get_role(role_id, db)
        return role_data


@router.post("/roles")
async def create_role(
    request: CreateRoleRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create role - scoped to current user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    organization_id = None
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if current_user:
            enforcer = get_enforcer()
            is_super = await is_super_admin(current_user, db, enforcer)
            if not is_super:
                # Organization admins: roles are scoped to their organization
                org = await get_user_organization(current_user, db)
                organization_id = str(org.id) if org else None
            # Super admins can create system roles (organization_id = None)
    
    # Use direct service call for better control
    async with AsyncSessionLocal() as db:
        try:
            role = await role_service.create_role(
                name=request.name,
                description=request.description,
                is_platform_role=request.is_platform_role,
                db=db,
                permissions=request.permissions or [],
                organization_id=organization_id
            )
            return role
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create role: {str(e)}")


@router.put("/roles/{role_id}")
async def update_role(
    role_id: str, 
    request: UpdateRoleRequest,
    current_user_id: str = Depends(verify_token)
):
    """Update role - verify it belongs to user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    async with AsyncSessionLocal() as db:
        # Get current user
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get role
        role_result = await db.execute(
            select(Role).where(Role.id == uuid.UUID(role_id))
        )
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Organization admins can only update roles from their organization
        # System roles (organization-admin) can be updated by org admins, but not other system roles
        if not is_super:
            if role.organization_id is None:
                # System role - only allow updating organization-admin
                if role.name != "organization-admin":
                    raise HTTPException(status_code=403, detail="Access denied: Cannot update system roles")
            elif role.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: Role belongs to a different organization")
    
    # Use service to update role
    async with AsyncSessionLocal() as db:
        try:
            role_data = await role_service.update_role(
                role_id=role_id,
                name=request.name,
                description=request.description,
                is_platform_role=request.is_platform_role,
                db=db,
                permissions=request.permissions
            )
            return role_data
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update role: {str(e)}")


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Delete role - verify it belongs to user's organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    async with AsyncSessionLocal() as db:
        # Get current user
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get role
        role_result = await db.execute(
            select(Role).where(Role.id == uuid.UUID(role_id))
        )
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Organization admins can only delete roles from their organization
        if not is_super:
            if role.organization_id is None:
                # System role - cannot be deleted by org admins
                raise HTTPException(status_code=403, detail="Access denied: Cannot delete system roles")
            elif role.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: Role belongs to a different organization")
    
    # Use service to delete role
    async with AsyncSessionLocal() as db:
        try:
            await role_service.delete_role(role_id, db)
            return {"message": "Role deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete role: {str(e)}")
