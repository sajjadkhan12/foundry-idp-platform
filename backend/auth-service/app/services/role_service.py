"""Role management service - Implementation with Casbin integration"""
from typing import Optional, List, Dict, Any
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.rbac import Role
from app.core.casbin import get_enforcer, invalidate_policy_cache
from app.core.permission_registry import parse_permission_slug, find_permission_by_resource_action


class RoleService:
    """Service for role management operations"""
    
    async def create_role(
        self,
        name: str,
        description: Optional[str],
        is_platform_role: bool,
        db: AsyncSession,
        permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new role"""
        # Check if role exists
        result = await db.execute(select(Role).where(Role.name == name))
        if result.scalar_one_or_none():
            raise ValueError("Role already exists")
        
        role = Role(
            name=name,
            description=description,
            is_platform_role=is_platform_role
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        
        # Add permissions to Casbin
        if permissions:
            enforcer = get_enforcer()
            for perm_slug in permissions:
                try:
                    obj, act = parse_permission_slug(perm_slug)
                    # Use "*" as domain for global roles
                    enforcer.add_policy(name, "*", obj, act)
                except Exception as e:
                    logging.error(f"Failed to add permission {perm_slug} to role {name}: {e}")
            
            enforcer.save_policy()
            invalidate_policy_cache()
        
        return {
            "id": str(role.id),
            "name": role.name,
            "description": role.description or "",
            "is_platform_role": role.is_platform_role,
            "created_at": role.created_at.isoformat() if role.created_at else "",
            "permissions": permissions or []
        }
    
    async def update_role(
        self,
        role_id: str,
        name: Optional[str],
        description: Optional[str],
        is_platform_role: Optional[bool],
        db: AsyncSession,
        permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update role"""
        result = await db.execute(select(Role).where(Role.id == uuid.UUID(role_id)))
        role = result.scalar_one_or_none()
        if not role:
            raise ValueError("Role not found")
        
        old_name = role.name
        
        if name and name != role.name:
            # Check if new name exists
            result = await db.execute(select(Role).where(Role.name == name))
            if result.scalar_one_or_none():
                raise ValueError("Role name already exists")
            
            # If name changed, we need to update Casbin policies
            enforcer = get_enforcer()
            # This is complex in Casbin, usually we'd rename sub in all policies
            # For simplicity, we'll handle permissions separately below
            role.name = name
        
        if description is not None:
            role.description = description
        
        if is_platform_role is not None:
            role.is_platform_role = is_platform_role
        
        await db.commit()
        await db.refresh(role)
        
        # Update permissions in Casbin
        if permissions is not None:
            enforcer = get_enforcer()
            # Remove all existing policies for this role (using old name)
            enforcer.enforcer.remove_filtered_policy(0, old_name)
            
            # Add new policies
            for perm_slug in permissions:
                try:
                    obj, act = parse_permission_slug(perm_slug)
                    enforcer.add_policy(role.name, "*", obj, act)
                except Exception as e:
                    logging.error(f"Failed to add permission {perm_slug} to role {role.name}: {e}")
            
            enforcer.save_policy()
            invalidate_policy_cache()
        elif name and name != old_name:
            # If only name changed, migrate existing policies
            enforcer = get_enforcer()
            old_policies = enforcer.enforcer.get_filtered_policy(0, old_name)
            enforcer.enforcer.remove_filtered_policy(0, old_name)
            for policy in old_policies:
                if len(policy) >= 4:
                    enforcer.add_policy(role.name, policy[1], policy[2], policy[3])
            enforcer.save_policy()
            invalidate_policy_cache()
            
        return await self.get_role(str(role.id), db)
    
    async def delete_role(self, role_id: str, db: AsyncSession):
        """Delete role"""
        result = await db.execute(select(Role).where(Role.id == uuid.UUID(role_id)))
        role = result.scalar_one_or_none()
        if not role:
            raise ValueError("Role not found")
        
        role_name = role.name
        await db.delete(role)
        await db.commit()
        
        # Remove all policies for this role from Casbin
        enforcer = get_enforcer()
        enforcer.enforcer.remove_filtered_policy(0, role_name)
        enforcer.enforcer.remove_filtered_grouping_policy(1, role_name)
        enforcer.save_policy()
        invalidate_policy_cache()
    
    async def get_role(self, role_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get role by ID with permissions"""
        result = await db.execute(select(Role).where(Role.id == uuid.UUID(role_id)))
        role = result.scalar_one_or_none()
        if not role:
            raise ValueError("Role not found")
        
        # Fetch permissions from Casbin
        enforcer = get_enforcer()
        policies = enforcer.enforcer.get_filtered_policy(0, role.name)
        
        permissions = []
        for p in policies:
            if len(p) >= 4:
                dom, obj, act = p[1], p[2], p[3]
                # Try to find slug from obj/act
                perm_def = find_permission_by_resource_action(obj, act)
                if perm_def:
                    permissions.append(perm_def["slug"])
                else:
                    # Fallback if not found in registry
                    permissions.append(f"{obj}:{act}")
        
        return {
            "id": str(role.id),
            "name": role.name,
            "description": role.description or "",
            "is_platform_role": role.is_platform_role,
            "created_at": role.created_at.isoformat() if role.created_at else "",
            "permissions": list(set(permissions))
        }
    
    async def list_roles(
        self,
        platform_roles_only: bool,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """List roles with permissions"""
        query = select(Role)
        if platform_roles_only:
            query = query.where(Role.is_platform_role == True)
        
        result = await db.execute(query)
        roles = result.scalars().all()
        
        enforcer = get_enforcer()
        all_roles_data = []
        
        for role in roles:
            # Fetch permissions for each role
            policies = enforcer.enforcer.get_filtered_policy(0, role.name)
            permissions = []
            for p in policies:
                if len(p) >= 4:
                    dom, obj, act = p[1], p[2], p[3]
                    perm_def = find_permission_by_resource_action(obj, act)
                    if perm_def:
                        permissions.append(perm_def["slug"])
                    else:
                        permissions.append(f"{obj}:{act}")
            
            all_roles_data.append({
                "id": str(role.id),
                "name": role.name,
                "description": role.description or "",
                "is_platform_role": role.is_platform_role,
                "created_at": role.created_at.isoformat() if role.created_at else "",
                "permissions": list(set(permissions))
            })
            
        return all_roles_data
    
    async def assign_role(
        self,
        user_id: str,
        role_name: str,
        organization_id: str,
        db: AsyncSession
    ):
        """Assign role to user"""
        enforcer = get_enforcer()
        enforcer.set_org_domain(organization_id)
        
        if not enforcer.has_grouping_policy(user_id, role_name, organization_id):
            enforcer.add_grouping_policy(user_id, role_name, organization_id)
            enforcer.save_policy()
            invalidate_policy_cache()
    
    async def remove_role(
        self,
        user_id: str,
        role_name: str,
        organization_id: str,
        db: AsyncSession
    ):
        """Remove role from user"""
        enforcer = get_enforcer()
        enforcer.set_org_domain(organization_id)
        
        if enforcer.has_grouping_policy(user_id, role_name, organization_id):
            enforcer.remove_grouping_policy(user_id, role_name, organization_id)
            enforcer.save_policy()
            invalidate_policy_cache()


role_service = RoleService()


role_service = RoleService()
