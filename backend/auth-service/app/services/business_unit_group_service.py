"""Business Unit Group service for managing groups within business units"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.business_unit import BusinessUnitGroup, BusinessUnitGroupMember
from app.models.rbac import User, Role
from typing import Optional, Dict, List
import uuid


class BusinessUnitGroupService:
    """Service for business unit group operations"""
    
    async def create_business_unit_group(
        self,
        business_unit_id: str,
        name: str,
        description: Optional[str],
        role_id: str,
        db: AsyncSession
    ) -> Dict:
        """Create a new group in a business unit"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
            role_uuid = uuid.UUID(role_id)
        except ValueError:
            raise ValueError("Invalid business unit ID or role ID")
        
        # Check if group with same name exists in this BU
        result = await db.execute(
            select(BusinessUnitGroup).where(
                BusinessUnitGroup.business_unit_id == bu_uuid,
                BusinessUnitGroup.name == name
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError("Group with this name already exists in this business unit")
        
        # Verify role exists
        result = await db.execute(
            select(Role).where(Role.id == role_uuid)
        )
        role = result.scalar_one_or_none()
        if not role:
            raise ValueError("Role not found")
        
        # Create new group
        group = BusinessUnitGroup(
            id=uuid.uuid4(),
            business_unit_id=bu_uuid,
            name=name,
            description=description,
            role_id=role_uuid
        )
        
        db.add(group)
        await db.commit()
        await db.refresh(group)
        
        return {
            "id": str(group.id),
            "business_unit_id": str(group.business_unit_id),
            "name": group.name,
            "description": group.description,
            "created_at": group.created_at.isoformat(),
            "updated_at": group.updated_at.isoformat()
        }
    
    async def update_business_unit_group(
        self,
        business_unit_id: str,
        group_id: str,
        name: Optional[str],
        description: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """Update a business unit group"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
            group_uuid = uuid.UUID(group_id)
        except ValueError:
            raise ValueError("Invalid business unit ID or group ID")
        
        result = await db.execute(
            select(BusinessUnitGroup).where(
                BusinessUnitGroup.id == group_uuid,
                BusinessUnitGroup.business_unit_id == bu_uuid
            )
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise ValueError("Group not found")
        
        # Update fields
        if name is not None:
            # Check if name is taken by another group in this BU
            result = await db.execute(
                select(BusinessUnitGroup).where(
                    (BusinessUnitGroup.name == name) &
                    (BusinessUnitGroup.business_unit_id == bu_uuid) &
                    (BusinessUnitGroup.id != group_uuid)
                )
            )
            if result.scalar_one_or_none():
                raise ValueError("Group name already in use in this business unit")
            group.name = name
        
        if description is not None:
            group.description = description
        
        await db.commit()
        await db.refresh(group)
        
        return {
            "id": str(group.id),
            "business_unit_id": str(group.business_unit_id),
            "name": group.name,
            "description": group.description,
            "created_at": group.created_at.isoformat(),
            "updated_at": group.updated_at.isoformat()
        }
    
    async def delete_business_unit_group(
        self,
        business_unit_id: str,
        group_id: str,
        db: AsyncSession
    ) -> None:
        """Delete a business unit group"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
            group_uuid = uuid.UUID(group_id)
        except ValueError:
            raise ValueError("Invalid business unit ID or group ID")
        
        result = await db.execute(
            select(BusinessUnitGroup).where(
                BusinessUnitGroup.id == group_uuid,
                BusinessUnitGroup.business_unit_id == bu_uuid
            )
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise ValueError("Group not found")
        
        await db.delete(group)
        await db.commit()
    
    async def get_business_unit_group(
        self,
        business_unit_id: str,
        group_id: str,
        db: AsyncSession
    ) -> Dict:
        """Get a business unit group by ID"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
            group_uuid = uuid.UUID(group_id)
        except ValueError:
            raise ValueError("Invalid business unit ID or group ID")
        
        result = await db.execute(
            select(BusinessUnitGroup)
            .options(selectinload(BusinessUnitGroup.role))
            .where(
                BusinessUnitGroup.id == group_uuid,
                BusinessUnitGroup.business_unit_id == bu_uuid
            )
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise ValueError("Group not found")
        
        return {
            "id": str(group.id),
            "business_unit_id": str(group.business_unit_id),
            "name": group.name,
            "description": group.description,
            "created_at": group.created_at.isoformat(),
            "updated_at": group.updated_at.isoformat()
        }
    
    async def list_business_unit_groups(
        self,
        business_unit_id: str,
        db: AsyncSession
    ) -> List[Dict]:
        """List all groups in a business unit"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
        except ValueError:
            raise ValueError("Invalid business unit ID")
        
        result = await db.execute(
            select(BusinessUnitGroup)
            .options(selectinload(BusinessUnitGroup.role))
            .where(BusinessUnitGroup.business_unit_id == bu_uuid)
        )
        groups = result.scalars().all()
        
        return [
            {
                "id": str(group.id),
                "business_unit_id": str(group.business_unit_id),
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at.isoformat(),
                "updated_at": group.updated_at.isoformat()
            }
            for group in groups
        ]
    
    async def add_business_unit_group_member(
        self,
        business_unit_id: str,
        group_id: str,
        user_id: str,
        db: AsyncSession
    ) -> None:
        """Add a user to a business unit group"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
            group_uuid = uuid.UUID(group_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid business unit ID, group ID, or user ID")
        
        # Verify group exists and belongs to business unit
        result = await db.execute(
            select(BusinessUnitGroup).where(
                BusinessUnitGroup.id == group_uuid,
                BusinessUnitGroup.business_unit_id == bu_uuid
            )
        )
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        # Verify user exists
        result = await db.execute(
            select(User).where(User.id == user_uuid)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Check if member already exists
        result = await db.execute(
            select(BusinessUnitGroupMember).where(
                BusinessUnitGroupMember.group_id == group_uuid,
                BusinessUnitGroupMember.user_id == user_uuid
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("User is already a member of this group")
        
        # Create membership
        member = BusinessUnitGroupMember(
            id=uuid.uuid4(),
            group_id=group_uuid,
            user_id=user_uuid
        )
        
        db.add(member)
        await db.commit()
    
    async def remove_business_unit_group_member(
        self,
        business_unit_id: str,
        group_id: str,
        user_id: str,
        db: AsyncSession
    ) -> None:
        """Remove a user from a business unit group"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
            group_uuid = uuid.UUID(group_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid business unit ID, group ID, or user ID")
        
        # Verify group exists and belongs to business unit
        result = await db.execute(
            select(BusinessUnitGroup).where(
                BusinessUnitGroup.id == group_uuid,
                BusinessUnitGroup.business_unit_id == bu_uuid
            )
        )
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        # Find and delete membership
        result = await db.execute(
            select(BusinessUnitGroupMember).where(
                BusinessUnitGroupMember.group_id == group_uuid,
                BusinessUnitGroupMember.user_id == user_uuid
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise ValueError("User is not a member of this group")
        
        await db.delete(member)
        await db.commit()
    
    async def list_business_unit_group_members(
        self,
        business_unit_id: str,
        group_id: str,
        db: AsyncSession
    ) -> List[Dict]:
        """List all members of a business unit group"""
        try:
            bu_uuid = uuid.UUID(business_unit_id)
            group_uuid = uuid.UUID(group_id)
        except ValueError:
            raise ValueError("Invalid business unit ID or group ID")
        
        # Verify group exists and belongs to business unit
        result = await db.execute(
            select(BusinessUnitGroup).where(
                BusinessUnitGroup.id == group_uuid,
                BusinessUnitGroup.business_unit_id == bu_uuid
            )
        )
        group = result.scalar_one_or_none()
        if not group:
            raise ValueError("Group not found")
        
        result = await db.execute(
            select(BusinessUnitGroupMember)
            .options(selectinload(BusinessUnitGroupMember.user))
            .where(BusinessUnitGroupMember.group_id == group_uuid)
        )
        members = result.scalars().all()
        
        return [
            {
                "id": str(member.id),
                "business_unit_id": str(bu_uuid),
                "group_id": str(member.group_id),
                "user_id": str(member.user_id),
                "user_email": member.user.email,
                "user_name": member.user.full_name or member.user.username,
                "created_at": member.created_at.isoformat()
            }
            for member in members
        ]


business_unit_group_service = BusinessUnitGroupService()
