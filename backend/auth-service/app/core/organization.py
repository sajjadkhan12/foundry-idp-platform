"""Organization context helpers for multi-tenancy support"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rbac import Organization, User
import uuid


async def get_user_organization(user: User, db: AsyncSession) -> Organization:
    """Get the organization for a user."""
    # Always query the organization directly - never access user.organization 
    # as it triggers lazy loading in async context
    result = await db.execute(
        select(Organization).where(Organization.id == user.organization_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise ValueError(f"Organization not found for user {user.email}")
    
    return org


def get_organization_domain(organization: Organization) -> str:
    """Get the domain string for Casbin enforcement."""
    return str(organization.id)


def get_organization_domain_from_id(org_id: uuid.UUID) -> str:
    """Get the domain string from organization ID."""
    return str(org_id)
