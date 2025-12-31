"""Business unit dependencies"""
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.rbac import User
from app.models.business_unit import BusinessUnitMember
from .auth import get_current_user
from .helpers import get_org_domain, is_platform_admin
from app.core.casbin import get_enforcer


async def get_active_business_unit(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Optional[UUID]:
    """
    Dependency to get active business unit ID from request headers or query params.
    Validates that user has access to the business unit.
    Returns None if no business unit is specified or user doesn't have access.
    
    Usage in endpoints:
    - Header: X-Business-Unit-Id
    - Query param: business_unit_id
    """
    # Try header first, then query param
    business_unit_id_str = request.headers.get("X-Business-Unit-Id") or request.query_params.get("business_unit_id")
    
    if not business_unit_id_str:
        return None
    
    try:
        business_unit_uuid = UUID(business_unit_id_str)
    except (ValueError, TypeError):
        return None
    
    # Validate user has access to this business unit
    # A user can have multiple roles in a BU, so we get all memberships
    result = await db.execute(
        select(BusinessUnitMember).where(
            BusinessUnitMember.business_unit_id == business_unit_uuid,
            BusinessUnitMember.user_id == current_user.id
        )
    )
    memberships = result.scalars().all()
    membership = memberships[0] if memberships else None
    
    if not membership:
        # Check if user is super admin (they can access all business units)
        enforcer = get_enforcer()
        org_domain = await get_org_domain(current_user, db)
        is_admin = await is_platform_admin(current_user, db, enforcer)
        if is_admin:
            return business_unit_uuid
        return None
    
    return business_unit_uuid


async def require_business_unit(
    request: Request,
    business_unit_id: Optional[UUID] = Depends(get_active_business_unit),
    current_user: User = Depends(get_current_user)
) -> UUID:
    """
    Dependency that requires a business unit to be selected.
    Raises 400 error if no business unit is selected.
    """
    if business_unit_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business unit must be selected. Please select a business unit from the header dropdown."
        )
    return business_unit_id
