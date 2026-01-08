"""Business unit management service - Simplified implementation"""
from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.models.business_unit import BusinessUnit, BusinessUnitMember
from app.models.rbac import User, Role
from app.core.casbin import get_enforcer
from app.core.organization import get_user_organization, get_organization_domain


class BusinessUnitService:
    """Service for business unit management operations"""
    
    async def create_business_unit(
        self,
        name: str,
        slug: str,
        description: Optional[str],
        organization_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Create a new business unit"""
        # Check if BU exists
        result = await db.execute(
            select(BusinessUnit).where(
                BusinessUnit.slug == slug,
                BusinessUnit.organization_id == uuid.UUID(organization_id)
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Business unit with this slug already exists")
        
        bu = BusinessUnit(
            name=name,
            slug=slug,
            description=description,
            organization_id=uuid.UUID(organization_id),
            is_active=True
        )
        db.add(bu)
        await db.commit()
        await db.refresh(bu)
        
        return {
            "id": str(bu.id),
            "name": bu.name,
            "slug": bu.slug,
            "description": bu.description or "",
            "organization_id": str(bu.organization_id),
            "is_active": bu.is_active,
            "role": None,
            "member_count": 0,
            "can_manage_members": False,
            "created_at": bu.created_at.isoformat() if bu.created_at else "",
            "updated_at": bu.updated_at.isoformat() if bu.updated_at else ""
        }
    
    async def update_business_unit(
        self,
        business_unit_id: str,
        name: Optional[str],
        description: Optional[str],
        is_active: Optional[bool],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update business unit"""
        result = await db.execute(select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id)))
        bu = result.scalar_one_or_none()
        if not bu:
            raise ValueError("Business unit not found")
        
        if name:
            bu.name = name
        if description is not None:
            bu.description = description
        if is_active is not None:
            bu.is_active = is_active
        
        await db.commit()
        await db.refresh(bu)
        
        # Get member count - count distinct users (not role assignments)
        count_result = await db.execute(
            select(func.count(func.distinct(BusinessUnitMember.user_id))).where(
                BusinessUnitMember.business_unit_id == bu.id
            )
        )
        member_count = count_result.scalar() or 0
        
        return {
            "id": str(bu.id),
            "name": bu.name,
            "slug": bu.slug,
            "description": bu.description or "",
            "organization_id": str(bu.organization_id),
            "is_active": bu.is_active,
            "role": None,
            "member_count": member_count,
            "can_manage_members": False,
            "created_at": bu.created_at.isoformat() if bu.created_at else "",
            "updated_at": bu.updated_at.isoformat() if bu.updated_at else ""
        }
    
    async def delete_business_unit(self, business_unit_id: str, db: AsyncSession):
        """Delete business unit"""
        result = await db.execute(select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id)))
        bu = result.scalar_one_or_none()
        if not bu:
            raise ValueError("Business unit not found")
        
        await db.delete(bu)
        await db.commit()
    
    async def get_business_unit(self, business_unit_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get business unit by ID"""
        result = await db.execute(select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id)))
        bu = result.scalar_one_or_none()
        if not bu:
            raise ValueError("Business unit not found")
        
        # Get member count - count distinct users (not role assignments)
        count_result = await db.execute(
            select(func.count(func.distinct(BusinessUnitMember.user_id))).where(
                BusinessUnitMember.business_unit_id == bu.id
            )
        )
        member_count = count_result.scalar() or 0
        
        return {
            "id": str(bu.id),
            "name": bu.name,
            "slug": bu.slug,
            "description": bu.description or "",
            "organization_id": str(bu.organization_id),
            "is_active": bu.is_active,
            "role": None,
            "member_count": member_count,
            "can_manage_members": False,
            "created_at": bu.created_at.isoformat() if bu.created_at else "",
            "updated_at": bu.updated_at.isoformat() if bu.updated_at else ""
        }
    
    async def list_business_units(
        self,
        user_id: Optional[str],
        organization_id: Optional[str],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """List business units"""
        query = select(BusinessUnit)
        
        if organization_id:
            query = query.where(BusinessUnit.organization_id == uuid.UUID(organization_id))
        
        if user_id:
            # Filter by user membership
            query = query.join(
                BusinessUnitMember,
                BusinessUnitMember.business_unit_id == BusinessUnit.id
            ).where(BusinessUnitMember.user_id == uuid.UUID(user_id))
        
        result = await db.execute(query)
        bus = result.scalars().all()
        
        # Deduplicate BUs (user might have multiple roles in the same BU)
        seen_bus = set()
        unique_bus = []
        for bu in bus:
            if bu.id not in seen_bus:
                seen_bus.add(bu.id)
                unique_bus.append(bu)
        bus = unique_bus
        
        response = []
        for bu in bus:
            # Get member count - count distinct users (not role assignments)
            count_result = await db.execute(
                select(func.count(func.distinct(BusinessUnitMember.user_id))).where(
                    BusinessUnitMember.business_unit_id == bu.id
                )
            )
            member_count = count_result.scalar() or 0
            
            # Check if user can manage members (has the manage_members permission via their role)
            can_manage_members = False
            user_role = None
            
            if user_id:
                # Get the user's memberships in this BU with their roles
                membership_result = await db.execute(
                    select(BusinessUnitMember, Role)
                    .outerjoin(Role, BusinessUnitMember.role_id == Role.id)
                    .where(
                        BusinessUnitMember.business_unit_id == bu.id,
                        BusinessUnitMember.user_id == uuid.UUID(user_id)
                    )
                )
                memberships = membership_result.all()
                
                for membership, role in memberships:
                    if role:
                        user_role = role.name
                        
                        # Platform admins can always manage members
                        if role.is_platform_role and role.name.lower() in ["admin", "superadmin", "platform_admin"]:
                            can_manage_members = True
                            break
                        
                        # Check via Casbin if role has manage_members permission
                        try:
                            enforcer = get_enforcer()
                            # Get all policies for this role
                            policies = enforcer.get_filtered_policy(0, role.name)
                            for policy in policies:
                                # Policy format: [role, domain, obj, act]
                                # obj = "business_unit:business_units", act = "manage_members"
                                if len(policy) >= 4:
                                    obj = policy[2]
                                    act = policy[3]
                                    if obj == "business_unit:business_units" and act == "manage_members":
                                        can_manage_members = True
                                        break
                        except Exception as e:
                            import logging
                            logging.warning(f"Error checking Casbin permissions: {e}")
                    
                    if can_manage_members:
                        break
            
            response.append({
                "id": str(bu.id),
                "name": bu.name,
                "slug": bu.slug,
                "description": bu.description or "",
                "organization_id": str(bu.organization_id),
                "is_active": bu.is_active,
                "role": user_role,
                "member_count": member_count,
                "can_manage_members": can_manage_members,
                "created_at": bu.created_at.isoformat() if bu.created_at else "",
                "updated_at": bu.updated_at.isoformat() if bu.updated_at else ""
            })
        
        return response
    
    async def add_business_unit_member(
        self,
        business_unit_id: str,
        user_email: str,
        role_ids: List[str],
        db: AsyncSession
    ):
        """Add member to business unit"""
        # Get user
        user_result = await db.execute(select(User).where(User.email == user_email.lower()))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Get business unit
        bu_result = await db.execute(select(BusinessUnit).where(BusinessUnit.id == uuid.UUID(business_unit_id)))
        bu = bu_result.scalar_one_or_none()
        if not bu:
            raise ValueError("Business unit not found")
        
        # If no roles specified, create a membership without a role (member only)
        if not role_ids:
            # Check if user already has any membership in this BU
            existing = await db.execute(
                select(BusinessUnitMember).where(
                    BusinessUnitMember.business_unit_id == bu.id,
                    BusinessUnitMember.user_id == user.id
                )
            )
            if not existing.scalar_one_or_none():
                # Create membership without role
                membership = BusinessUnitMember(
                    business_unit_id=bu.id,
                    user_id=user.id,
                    role_id=None  # No role assigned yet
                )
                db.add(membership)
        else:
            # Add memberships for each role
            for role_id_str in role_ids:
                role_id = uuid.UUID(role_id_str)
                
                # Check if membership already exists
                existing = await db.execute(
                    select(BusinessUnitMember).where(
                        BusinessUnitMember.business_unit_id == bu.id,
                        BusinessUnitMember.user_id == user.id,
                        BusinessUnitMember.role_id == role_id
                    )
                )
                if existing.scalar_one_or_none():
                    continue  # Already a member with this role
                
                # Create membership
                membership = BusinessUnitMember(
                    business_unit_id=bu.id,
                    user_id=user.id,
                    role_id=role_id
                )
                db.add(membership)
        
        await db.commit()
    
    async def remove_business_unit_member(
        self,
        business_unit_id: str,
        user_id: str,
        db: AsyncSession
    ):
        """Remove member from business unit"""
        result = await db.execute(
            select(BusinessUnitMember).where(
                BusinessUnitMember.business_unit_id == uuid.UUID(business_unit_id),
                BusinessUnitMember.user_id == uuid.UUID(user_id)
            )
        )
        memberships = result.scalars().all()
        
        for membership in memberships:
            await db.delete(membership)
        
        await db.commit()
    
    async def list_business_unit_members(
        self,
        business_unit_id: str,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """List business unit members"""
        result = await db.execute(
            select(BusinessUnitMember, User, Role)
            .join(User, BusinessUnitMember.user_id == User.id)
            .outerjoin(Role, BusinessUnitMember.role_id == Role.id)
            .where(BusinessUnitMember.business_unit_id == uuid.UUID(business_unit_id))
        )
        
        members = []
        for membership, user, role in result.all():
            members.append({
                "id": str(membership.id),
                "business_unit_id": str(membership.business_unit_id),
                "user_id": str(membership.user_id),
                "user_email": user.email,
                "user_name": user.full_name or "",
                "role": role.name if role else "",
                "role_id": str(role.id) if role else "",
                "created_at": membership.created_at.isoformat() if membership.created_at else ""
            })
        
        return members


business_unit_service = BusinessUnitService()
