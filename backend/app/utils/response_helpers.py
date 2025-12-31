"""Response helpers to convert models to response schemas"""
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.rbac import User, Role
from app.models.business_unit import BusinessUnitMember
from app.schemas.user import UserResponse


async def get_valid_role_names(db: AsyncSession) -> Set[str]:
    """Get all valid role names from database"""
    result = await db.execute(select(Role.name))
    return {name for name in result.scalars().all()}


def filter_user_roles(user_roles: List[str], valid_role_names: Set[str]) -> List[str]:
    """Filter user roles to only include valid role names (exclude group names)"""
    if not user_roles:
        return []
    filtered = [role for role in user_roles if role in valid_role_names]
    return list(set(filtered))  # Remove duplicates


async def user_to_response(
    user: User,
    enforcer,
    db: AsyncSession,
    include_admin_check: bool = True
) -> UserResponse:
    """
    Convert User model to UserResponse with roles.
    
    This is a centralized function to avoid duplication across:
    - users.py
    - auth.py
    - Any other file needing user responses
    """
    from app.core.organization import get_user_organization, get_organization_domain
    from app.api.deps.helpers import is_platform_admin
    
    # Get organization domain
    org = await get_user_organization(user, db)
    org_domain = get_organization_domain(org)
    
    # Get roles from Casbin
    user_roles = enforcer.get_roles_for_user(str(user.id))
    
    # Filter to valid roles only
    valid_role_names = await get_valid_role_names(db)
    user_roles = filter_user_roles(user_roles, valid_role_names)
    
    # Add BU roles
    bu_result = await db.execute(
        select(BusinessUnitMember, Role)
        .join(Role, BusinessUnitMember.role_id == Role.id)
        .where(BusinessUnitMember.user_id == user.id)
    )
    for bu_member, bu_role in bu_result.all():
        if bu_role.name not in user_roles:
            user_roles.append(bu_role.name)
    
    # Check admin status
    user_is_admin = False
    if include_admin_check:
        user_is_admin = await is_platform_admin(user, db, enforcer)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_admin=user_is_admin,
        created_at=user.created_at,
        roles=user_roles
    )
