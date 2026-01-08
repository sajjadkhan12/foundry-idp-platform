"""User management service"""
from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_

from app.models.rbac import User, Role, Organization
from app.services.security_service import security_service
from app.utils.response_helpers import user_to_response
from app.core.casbin import get_enforcer
from app.core.organization import get_user_organization, get_organization_domain


class UserService:
    """Service for user management operations"""
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str],
        organization_id: str,
        role_names: List[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Create a new user"""
        # Validate password
        is_valid, error = security_service.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email.lower()))
        if result.scalar_one_or_none():
            raise ValueError("User with this email already exists")
        
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise ValueError("User with this username already exists")
        
        # Get organization
        org_result = await db.execute(
            select(Organization).where(Organization.id == uuid.UUID(organization_id))
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise ValueError("Organization not found")
        
        # Hash password
        hashed_password = security_service.hash_password(password)
        
        # Create user
        user = User(
            email=email.lower(),
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            organization_id=org.id,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user, ["organization"])
        
        # Assign roles if provided
        if role_names:
            org_domain = get_organization_domain(org)
            enforcer = get_enforcer()
            enforcer.set_org_domain(org_domain)
            
            for role_name in role_names:
                if not enforcer.has_grouping_policy(str(user.id), role_name):
                    enforcer.add_grouping_policy(str(user.id), role_name, org_domain)
            enforcer.save_policy()
        
        # Get user response
        enforcer = get_enforcer()
        enforcer.set_org_domain(get_organization_domain(org))
        return await user_to_response(user, enforcer, db, include_admin_check=True)
    
    async def update_user(
        self,
        user_id: str,
        email: Optional[str],
        full_name: Optional[str],
        password: Optional[str],
        is_active: Optional[bool],
        role_names: Optional[List[str]],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update user"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        if email and email != user.email:
            # Check if email exists
            result = await db.execute(select(User).where(User.email == email.lower()))
            if result.scalar_one_or_none():
                raise ValueError("Email already in use")
            user.email = email.lower()
        
        if full_name is not None:
            user.full_name = full_name
        
        if password:
            is_valid, error = security_service.validate_password_strength(password)
            if not is_valid:
                raise ValueError(error)
            user.hashed_password = security_service.hash_password(password)
        
        if is_active is not None:
            user.is_active = is_active
        
        await db.commit()
        await db.refresh(user, ["organization"])
        
        # Update roles if provided
        if role_names is not None:
            org = await get_user_organization(user, db)
            org_domain = get_organization_domain(org)
            enforcer = get_enforcer()
            enforcer.set_org_domain(org_domain)
            
            # Remove all existing roles
            existing_roles = enforcer.get_roles_for_user(str(user.id))
            for role in existing_roles:
                enforcer.remove_grouping_policy(str(user.id), role, org_domain)
            
            # Add new roles
            for role_name in role_names:
                enforcer.add_grouping_policy(str(user.id), role_name, org_domain)
            enforcer.save_policy()
        
        # Get user response
        org = await get_user_organization(user, db)
        enforcer = get_enforcer()
        enforcer.set_org_domain(get_organization_domain(org))
        return await user_to_response(user, enforcer, db, include_admin_check=True)
    
    async def delete_user(self, user_id: str, db: AsyncSession):
        """Delete user"""
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        await db.delete(user)
        await db.commit()
    
    async def get_user(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get user by ID"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        org = await get_user_organization(user, db)
        enforcer = get_enforcer()
        enforcer.set_org_domain(get_organization_domain(org))
        return await user_to_response(user, enforcer, db, include_admin_check=True)
    
    async def list_users(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        role_filter: Optional[str],
        organization_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """List users with pagination and filters"""
        query = select(User).options(selectinload(User.organization))
        count_query = select(func.count(User.id))
        
        if organization_id:
            org_uuid = uuid.UUID(organization_id)
            query = query.where(User.organization_id == org_uuid)
            count_query = count_query.where(User.organization_id == org_uuid)
        
        if search:
            search_pattern = f"%{search}%"
            search_filter = or_(
                User.email.ilike(search_pattern),
                User.username.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Convert to response format
        user_responses = []
        for user in users:
            org = await get_user_organization(user, db)
            enforcer = get_enforcer()
            enforcer.set_org_domain(get_organization_domain(org))
            user_resp = await user_to_response(user, enforcer, db, include_admin_check=False)
            
            # Filter by role if specified
            if role_filter:
                if role_filter not in user_resp.get("roles", []):
                    continue
            
            user_responses.append(user_resp)
        
        return {
            "users": user_responses,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    async def get_current_user(self, token: str, db: AsyncSession) -> Dict[str, Any]:
        """Get current user from token"""
        from app.services.auth_service import auth_service
        user_info = await auth_service.validate_token(token, db)
        
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_info["user_id"]))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        org = await get_user_organization(user, db)
        enforcer = get_enforcer()
        enforcer.set_org_domain(get_organization_domain(org))
        return await user_to_response(user, enforcer, db, include_admin_check=True)
    
    async def update_current_user(
        self,
        token: str,
        email: Optional[str],
        full_name: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update current user"""
        user_info = await self.get_current_user(token, db)
        return await self.update_user(
            user_info["id"],
            email,
            full_name,
            None,  # password
            None,  # is_active
            None,  # role_names
            db
        )
    
    async def change_password(
        self,
        token: str,
        current_password: str,
        new_password: str,
        db: AsyncSession
    ):
        """Change user password"""
        user_info = await self.get_current_user(token, db)
        
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_info["id"])))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not security_service.verify_password(current_password, user.hashed_password):
            raise ValueError("Incorrect current password")
        
        # Validate new password
        is_valid, error = security_service.validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(error)
        
        # Update password
        user.hashed_password = security_service.hash_password(new_password)
        await db.commit()


user_service = UserService()
