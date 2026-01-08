"""Authorization service"""
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.rbac import User, Role
from app.core.casbin import get_enforcer
from app.core.organization import get_user_organization, get_organization_domain
from app.core.authorization import check_permission, get_user_platform_roles
from app.core.permission_registry import get_permission_scope, parse_permission_slug
from app.utils.helpers import is_platform_admin


class AuthorizationService:
    """Service for authorization operations"""
    
    async def check_permission(
        self,
        user_id: str,
        permission_slug: str,
        business_unit_id: Optional[str],
        organization_id: Optional[str],
        db: AsyncSession
    ) -> bool:
        """Check if user has permission"""
        # Get user
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return False
        
        # Get organization
        org = await get_user_organization(user, db)
        org_domain = organization_id or get_organization_domain(org)
        
        # Get enforcer
        enforcer = get_enforcer()
        enforcer.set_org_domain(org_domain)
        
        # Check if platform admin (admins bypass permission checks)
        if await is_platform_admin(user, db, enforcer):
            return True
        
        # Parse business unit ID
        bu_id = None
        if business_unit_id:
            try:
                bu_id = uuid.UUID(business_unit_id)
            except ValueError:
                pass
        
        # Check permission
        return await check_permission(user, permission_slug, bu_id, db, enforcer)
    
    async def get_user_roles(
        self,
        user_id: str,
        organization_id: Optional[str],
        db: AsyncSession
    ) -> list[str]:
        """Get user roles"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return []
        
        org = await get_user_organization(user, db)
        org_domain = organization_id or get_organization_domain(org)
        
        enforcer = get_enforcer()
        enforcer.set_org_domain(org_domain)
        
        roles = enforcer.get_roles_for_user(str(user.id))
        
        # Filter to valid roles
        role_result = await db.execute(select(Role.name))
        valid_role_names = {name for name in role_result.scalars().all()}
        return [role for role in roles if role in valid_role_names]
    
    async def get_user_permissions(
        self,
        user_id: str,
        business_unit_id: Optional[str],
        organization_id: Optional[str],
        db: AsyncSession
    ) -> list[str]:
        """Get user permissions"""
        # This is a simplified version - in production you'd want to get all permissions
        # the user has access to based on their roles
        roles = await self.get_user_roles(user_id, organization_id, db)
        # Return role names as permissions for now
        # In production, you'd query Casbin for all permissions granted to these roles
        return roles
    
    async def is_platform_admin(
        self,
        user_id: str,
        organization_id: Optional[str],
        db: AsyncSession
    ) -> bool:
        """Check if user is platform admin"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        org = await get_user_organization(user, db)
        org_domain = organization_id or get_organization_domain(org)
        
        enforcer = get_enforcer()
        enforcer.set_org_domain(org_domain)
        
        return await is_platform_admin(user, db, enforcer)


authorization_service = AuthorizationService()
