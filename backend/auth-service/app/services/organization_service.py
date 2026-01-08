"""Organization service for managing organizations"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.rbac import Organization, User
from typing import Optional, Dict, List
import uuid


class OrganizationService:
    """Service for organization operations"""
    
    async def create_organization(
        self,
        name: str,
        slug: str,
        description: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """Create a new organization"""
        # Check if organization with same name or slug exists
        result = await db.execute(
            select(Organization).where(
                (Organization.name == name) | (Organization.slug == slug)
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            if existing.name == name:
                raise ValueError("Organization with this name already exists")
            else:
                raise ValueError("Organization with this slug already exists")
        
        # Create new organization
        organization = Organization(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            description=description,
            is_active=True
        )
        
        db.add(organization)
        await db.commit()
        await db.refresh(organization)
        
        return {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "description": organization.description,
            "is_active": organization.is_active,
            "created_at": organization.created_at.isoformat(),
            "updated_at": organization.updated_at.isoformat()
        }
    
    async def update_organization(
        self,
        organization_id: str,
        name: Optional[str],
        description: Optional[str],
        is_active: Optional[bool],
        db: AsyncSession
    ) -> Dict:
        """Update an organization"""
        try:
            org_uuid = uuid.UUID(organization_id)
        except ValueError:
            raise ValueError("Invalid organization ID")
        
        result = await db.execute(
            select(Organization).where(Organization.id == org_uuid)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise ValueError("Organization not found")
        
        # Update fields
        if name is not None:
            # Check if name is taken by another organization
            result = await db.execute(
                select(Organization).where(
                    (Organization.name == name) & (Organization.id != org_uuid)
                )
            )
            if result.scalar_one_or_none():
                raise ValueError("Organization name already in use")
            organization.name = name
        
        if description is not None:
            organization.description = description
        
        if is_active is not None:
            organization.is_active = is_active
        
        await db.commit()
        await db.refresh(organization)
        
        return {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "description": organization.description,
            "is_active": organization.is_active,
            "created_at": organization.created_at.isoformat(),
            "updated_at": organization.updated_at.isoformat()
        }
    
    async def delete_organization(
        self,
        organization_id: str,
        db: AsyncSession
    ) -> None:
        """Delete an organization"""
        try:
            org_uuid = uuid.UUID(organization_id)
        except ValueError:
            raise ValueError("Invalid organization ID")
        
        result = await db.execute(
            select(Organization).where(Organization.id == org_uuid)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise ValueError("Organization not found")
        
        # Prevent deletion of default organization
        if organization.slug == "default":
            raise ValueError("Cannot delete the default organization")
        
        # Check if organization has users
        result = await db.execute(
            select(func.count(User.id)).where(User.organization_id == org_uuid)
        )
        user_count = result.scalar()
        
        if user_count > 0:
            raise ValueError(f"Cannot delete organization with {user_count} users. Move or delete users first.")
        
        await db.delete(organization)
        await db.commit()
    
    async def get_organization(
        self,
        organization_id: str,
        db: AsyncSession
    ) -> Dict:
        """Get organization by ID"""
        try:
            org_uuid = uuid.UUID(organization_id)
        except ValueError:
            raise ValueError("Invalid organization ID")
        
        result = await db.execute(
            select(Organization).where(Organization.id == org_uuid)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise ValueError("Organization not found")
        
        return {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "description": organization.description,
            "is_active": organization.is_active,
            "created_at": organization.created_at.isoformat(),
            "updated_at": organization.updated_at.isoformat()
        }
    
    async def list_organizations(
        self,
        skip: int,
        limit: int,
        db: AsyncSession
    ) -> List[Dict]:
        """List all organizations"""
        result = await db.execute(
            select(Organization)
            .offset(skip)
            .limit(limit)
            .order_by(Organization.created_at.desc())
        )
        organizations = result.scalars().all()
        
        return [
            {
                "id": str(org.id),
                "name": org.name,
                "slug": org.slug,
                "description": org.description,
                "is_active": org.is_active,
                "created_at": org.created_at.isoformat(),
                "updated_at": org.updated_at.isoformat()
            }
            for org in organizations
        ]
    
    async def get_current_organization(
        self,
        user_id: str,
        db: AsyncSession
    ) -> Dict:
        """Get the current user's organization"""
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user ID")
        
        result = await db.execute(
            select(User).where(User.id == user_uuid)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        result = await db.execute(
            select(Organization).where(Organization.id == user.organization_id)
        )
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise ValueError("Organization not found")
        
        return {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "description": organization.description,
            "is_active": organization.is_active,
            "created_at": organization.created_at.isoformat(),
            "updated_at": organization.updated_at.isoformat()
        }


organization_service = OrganizationService()
