"""Group management service - Simplified implementation"""
from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.rbac import Group
from app.core.casbin import get_enforcer


class GroupService:
    """Service for group management operations"""
    
    async def create_group(
        self,
        name: str,
        description: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Create a new group"""
        # Check if group exists
        result = await db.execute(select(Group).where(Group.name == name))
        if result.scalar_one_or_none():
            raise ValueError("Group already exists")
        
        group = Group(
            name=name,
            description=description
        )
        db.add(group)
        await db.commit()
        await db.refresh(group)
        
        return {
            "id": str(group.id),
            "name": group.name,
            "description": group.description or "",
            "created_at": group.created_at.isoformat() if group.created_at else ""
        }
    
    async def update_group(
        self,
        group_id: str,
        name: Optional[str],
        description: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update group"""
        result = await db.execute(select(Group).where(Group.id == uuid.UUID(group_id)))
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        if name and name != group.name:
            result = await db.execute(select(Group).where(Group.name == name))
            if result.scalar_one_or_none():
                raise ValueError("Group name already exists")
            group.name = name
        
        if description is not None:
            group.description = description
        
        await db.commit()
        await db.refresh(group)
        
        return {
            "id": str(group.id),
            "name": group.name,
            "description": group.description or "",
            "created_at": group.created_at.isoformat() if group.created_at else ""
        }
    
    async def delete_group(self, group_id: str, db: AsyncSession):
        """Delete group"""
        result = await db.execute(select(Group).where(Group.id == uuid.UUID(group_id)))
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        await db.delete(group)
        await db.commit()
    
    async def get_group(self, group_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get group by ID"""
        result = await db.execute(select(Group).where(Group.id == uuid.UUID(group_id)))
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        return {
            "id": str(group.id),
            "name": group.name,
            "description": group.description or "",
            "created_at": group.created_at.isoformat() if group.created_at else ""
        }
    
    async def list_groups(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """List groups"""
        result = await db.execute(select(Group))
        groups = result.scalars().all()
        
        return [
            {
                "id": str(group.id),
                "name": group.name,
                "description": group.description or "",
                "created_at": group.created_at.isoformat() if group.created_at else ""
            }
            for group in groups
        ]
    
    async def add_group_member(
        self,
        group_id: str,
        user_id: str,
        organization_id: str,
        db: AsyncSession
    ):
        """Add user to group"""
        result = await db.execute(select(Group).where(Group.id == uuid.UUID(group_id)))
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        enforcer = get_enforcer()
        enforcer.set_org_domain(organization_id)
        
        # Add grouping policy: user -> group
        if not enforcer.has_grouping_policy(user_id, group.name, organization_id):
            enforcer.add_grouping_policy(user_id, group.name, organization_id)
            enforcer.save_policy()
    
    async def remove_group_member(
        self,
        group_id: str,
        user_id: str,
        organization_id: str,
        db: AsyncSession
    ):
        """Remove user from group"""
        result = await db.execute(select(Group).where(Group.id == uuid.UUID(group_id)))
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        enforcer = get_enforcer()
        enforcer.set_org_domain(organization_id)
        
        if enforcer.has_grouping_policy(user_id, group.name, organization_id):
            enforcer.remove_grouping_policy(user_id, group.name, organization_id)
            enforcer.save_policy()


group_service = GroupService()
