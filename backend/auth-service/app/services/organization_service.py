"""Organization service for managing organizations"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.rbac import Organization, User, Role
from app.models.business_unit import BusinessUnit
from typing import Optional, Dict, List
import uuid
import logging

logger = logging.getLogger(__name__)


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
        
        # Prevent deletion of foundry organization (platform owner)
        if organization.slug == "foundry":
            raise ValueError("Cannot delete the foundry organization (platform owner)")
        
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
    
    async def create_organization_with_admin(
        self,
        name: str,
        slug: str,
        description: Optional[str],
        admin_email: str,
        admin_username: str,
        admin_password: str,
        admin_full_name: Optional[str],
        db: AsyncSession,
        created_by_user_id: Optional[str] = None
    ) -> Dict:
        """Create organization with admin user, default business unit, and initial setup"""
        from app.services.security_service import security_service
        from app.core.casbin import get_enforcer
        from app.core.organization import get_organization_domain
        from sqlalchemy import func
        
        # 1. Validate admin password FIRST (before creating anything)
        is_valid, error = security_service.validate_password_strength(admin_password)
        if not is_valid:
            raise ValueError(f"Admin password does not meet requirements: {error}")
        
        # 2. Check if admin email/username already exists BEFORE creating organization
        # Use case-insensitive check for both email and username
        existing_user_result = await db.execute(
            select(User).where(
                (func.lower(User.email) == admin_email.lower()) | 
                (func.lower(User.username) == admin_username.lower())
            )
        )
        existing_user = existing_user_result.scalar_one_or_none()
        if existing_user:
            # Provide more specific error message
            if existing_user.email.lower() == admin_email.lower():
                raise ValueError(f"User with email '{admin_email}' already exists")
            else:
                raise ValueError(f"User with username '{admin_username}' already exists")
        
        # 3. Create organization (only after validation passes)
        org = await self.create_organization(name, slug, description, db)
        org_uuid = uuid.UUID(org["id"])
        
        # 4. Hash password and create admin user
        hashed_password = security_service.hash_password(admin_password)
        
        admin_user = User(
            email=admin_email.lower(),
            username=admin_username,
            hashed_password=hashed_password,
            full_name=admin_full_name or f"{name} Administrator",
            organization_id=org_uuid,
            is_active=True
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        logger.info(f"Created admin user: {admin_email} for organization: {name}")
        
        # 5. Create organization-specific organization-admin role as Platform role with all permissions
        # Each organization gets its own instance of the organization-admin role
        role_result = await db.execute(
            select(Role).where(
                Role.name == "organization-admin",
                Role.organization_id == org_uuid
            )
        )
        org_admin_role = role_result.scalar_one_or_none()
        
        role_created = False
        if not org_admin_role:
            org_admin_role = Role(
                name="organization-admin",
                description="Organization administrator with full access within organization",
                is_platform_role=True,
                organization_id=org_uuid  # Org-specific role
            )
            db.add(org_admin_role)
            await db.commit()
            await db.refresh(org_admin_role)
            logger.info(f"Created organization-specific organization-admin role for organization: {name}")
            role_created = True
        
        # Assign all platform permissions to this organization's organization-admin role
        from app.core.permission_registry import parse_permission_slug, get_platform_permissions, get_bu_permissions, get_user_permissions
        
        # Combine all permissions to ensure full access
        platform_perms = get_platform_permissions()
        bu_perms = get_bu_permissions()
        user_perms = get_user_permissions()
        
        all_admin_permissions = platform_perms + bu_perms + user_perms
        logger.info(f"Assigning {len(all_admin_permissions)} permissions (Platform: {len(platform_perms)}, BU: {len(bu_perms)}, User: {len(user_perms)}) to organization-admin")
        
        # Fetch organization object ensuring we have the ORM object for domain generation
        org_result = await db.execute(
            select(Organization).where(Organization.id == org_uuid)
        )
        organization_obj = org_result.scalar_one()
        
        org_domain = get_organization_domain(organization_obj)
        enforcer_temp = get_enforcer()
        enforcer_temp.set_org_domain(org_domain)
        
        for perm_slug in all_admin_permissions:
            try:
                obj, act = parse_permission_slug(perm_slug)
                # Check if policy already exists before adding (scoped to this organization's domain)
                existing_policies = enforcer_temp.get_filtered_policy(0, "organization-admin", org_domain, obj, act)
                if not existing_policies:
                    enforcer_temp.add_policy("organization-admin", org_domain, obj, act)
            except Exception as e:
                logger.warning(f"Failed to add permission {perm_slug} to organization-admin role: {e}")
        enforcer_temp.save_policy()
        if role_created:
            logger.info(f"Assigned all permissions to organization-admin role for {name}")
        
        # 6. Assign organization-admin role to admin user via Casbin
        # Organization object is already fetched above
        org_domain = get_organization_domain(organization_obj)
        enforcer = get_enforcer()
        enforcer.set_org_domain(org_domain)
        
        if not enforcer.has_grouping_policy(str(admin_user.id), "organization-admin", org_domain):
            enforcer.add_grouping_policy(str(admin_user.id), "organization-admin", org_domain)
            enforcer.save_policy()
            logger.info(f"Assigned organization-admin role to {admin_username}")
        
        # 7. Create default business unit for the organization
        from app.services.business_unit_service import business_unit_service
        
        default_bu = await business_unit_service.create_business_unit(
            name=f"{name} Default",
            slug="default",
            description=f"Default business unit for {name}",
            organization_id=org["id"],
            db=db
        )
        logger.info(f"Created default business unit: {default_bu['name']}")
        
        # Also assign organization-admin role to admin user for the Default BU domain
        # This ensures they have permissions within the BU context immediately
        from app.core.business_unit import get_business_unit_domain_by_uuid
        bu_domain = get_business_unit_domain_by_uuid(default_bu["id"])
        enforcer.set_org_domain(bu_domain) # Set context for next operation
        
        if not enforcer.has_grouping_policy(str(admin_user.id), "organization-admin", bu_domain):
            enforcer.add_grouping_policy(str(admin_user.id), "organization-admin", bu_domain)
            enforcer.save_policy()
            logger.info(f"Assigned organization-admin role to {admin_username} for Default BU")
        
        # 8. Set default business unit as active for admin user
        admin_user.active_business_unit_id = uuid.UUID(default_bu["id"])
        await db.commit()
        await db.refresh(admin_user)
        
        return {
            "organization": org,
            "admin_user": {
                "id": str(admin_user.id),
                "email": admin_user.email,
                "username": admin_user.username,
                "full_name": admin_user.full_name
            },
            "default_business_unit": default_bu
        }


organization_service = OrganizationService()
