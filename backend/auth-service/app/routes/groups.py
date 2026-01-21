import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from app.schemas.groups import CreateGroupRequest, UpdateGroupRequest
from app.core.dependencies import verify_token, PROTO_AVAILABLE
from app.database import AsyncSessionLocal
from app.models.rbac import User, Group
from sqlalchemy.future import select
from app.utils.helpers import is_super_admin
from app.core.casbin import get_enforcer
from app.core.organization import get_user_organization, get_organization_domain
from app.services.group_service import group_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/groups")
async def list_groups(
    current_user_id: str = Depends(verify_token)
):
    """List groups - filtered by organization context"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    is_super = False
    organization_id = None
    org_domain = None
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = result.scalar_one_or_none()
        if current_user:
            enforcer = get_enforcer()
            is_super = await is_super_admin(current_user, db, enforcer)
            if not is_super:
                org = await get_user_organization(current_user, db)
                organization_id = str(org.id) if org else None
                org_domain = get_organization_domain(org) if org else None
    
    # SaaS Manager Visibility: Super admins only see groups within their own organization context
    if is_super and not organization_id:
        async with AsyncSessionLocal() as db:
            org = await get_user_organization(current_user, db)
            organization_id = str(org.id) if org else None
    
    if is_super and not organization_id:
        return []

    async with AsyncSessionLocal() as db:
        # For organization admins: only show their org's groups
        groups_list = await group_service.list_groups(
            db=db,
            organization_id=organization_id
        )
    
    return groups_list


@router.get("/groups/{group_id}")
async def get_group(
    group_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Get group by ID - verify it belongs to user's organization"""
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
        
        # Get group
        group_result = await db.execute(
            select(Group).where(Group.id == uuid.UUID(group_id))
        )
        group = group_result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Super admins should NOT access organization-specific resources
        if is_super:
            raise HTTPException(status_code=403, detail="Super admins cannot access organization-specific resources")
        
        # Organization admins can only access groups from their organization
        if group.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Group belongs to a different organization")
    
    # Use service to get group details
    async with AsyncSessionLocal() as db:
        group_data = await group_service.get_group(group_id, db)
        return group_data


@router.post("/groups")
async def create_group(
    request: CreateGroupRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create group - scoped to current user's organization"""
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
                # Organization admins: groups are scoped to their organization
                org = await get_user_organization(current_user, db)
                organization_id = str(org.id) if org else None
            else:
                raise HTTPException(status_code=403, detail="Super admins cannot create groups directly")
    
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization context required")
    
    # Use direct service call
    async with AsyncSessionLocal() as db:
        try:
            group = await group_service.create_group(
                name=request.name,
                description=request.description,
                db=db,
                organization_id=organization_id
            )
            return group
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create group: {str(e)}")


@router.put("/groups/{group_id}")
async def update_group(
    group_id: str, 
    request: UpdateGroupRequest,
    current_user_id: str = Depends(verify_token)
):
    """Update group - verify it belongs to user's organization"""
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
        
        # Get group
        group_result = await db.execute(
            select(Group).where(Group.id == uuid.UUID(group_id))
        )
        group = group_result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Organization admins can only update groups from their organization
        if not is_super and group.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Group belongs to a different organization")
    
    # Use service to update group
    async with AsyncSessionLocal() as db:
        try:
            group_data = await group_service.update_group(
                group_id=group_id,
                name=request.name,
                description=request.description,
                db=db
            )
            return group_data
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update group: {str(e)}")


@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Delete group - verify it belongs to user's organization"""
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
        
        # Get group
        group_result = await db.execute(
            select(Group).where(Group.id == uuid.UUID(group_id))
        )
        group = group_result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Organization admins can only delete groups from their organization
        if not is_super and group.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied: Group belongs to a different organization")
    
    # Use service to delete group
    async with AsyncSessionLocal() as db:
        try:
            await group_service.delete_group(group_id, db)
            return {"message": "Group deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete group: {str(e)}")


@router.post("/groups/{group_id}/users/{user_id}")
async def add_user_to_group(
    group_id: str, 
    user_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Add user to group - verify group and user belong to same organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify group and user belong to same organization
    async with AsyncSessionLocal() as db:
        # Get current user
        current_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = current_user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get target user
        target_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        target_user = target_user_result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Get group
        group_result = await db.execute(
            select(Group).where(Group.id == uuid.UUID(group_id))
        )
        group = group_result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if current user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Organization admins can only add users from their organization to groups from their organization
        if not is_super:
            if group.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: Group belongs to a different organization")
            if target_user.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: User belongs to a different organization")
    
    # Use service to add user to group
    async with AsyncSessionLocal() as db:
        try:
            await group_service.add_group_member(
                group_id=group_id,
                user_id=user_id,
                organization_id=str(target_user.organization_id),
                db=db
            )
            return {"message": "User added to group successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to add user to group: {str(e)}")


@router.delete("/groups/{group_id}/users/{user_id}")
async def remove_user_from_group(
    group_id: str, 
    user_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Remove user from group - verify group and user belong to same organization"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Verify group and user belong to same organization
    async with AsyncSessionLocal() as db:
        # Get current user
        current_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(current_user_id))
        )
        current_user = current_user_result.scalar_one_or_none()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get target user
        target_user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        target_user = target_user_result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found")
        
        # Get group
        group_result = await db.execute(
            select(Group).where(Group.id == uuid.UUID(group_id))
        )
        group = group_result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if current user is super admin
        enforcer = get_enforcer()
        is_super = await is_super_admin(current_user, db, enforcer)
        
        # Organization admins can only remove users from their organization from groups from their organization
        if not is_super:
            if group.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: Group belongs to a different organization")
            if target_user.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied: User belongs to a different organization")
    
    # Use service to remove user from group
    async with AsyncSessionLocal() as db:
        try:
            await group_service.remove_group_member(
                group_id=group_id,
                user_id=user_id,
                organization_id=str(target_user.organization_id),
                db=db
            )
            return {"message": "User removed from group successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to remove user from group: {str(e)}")
