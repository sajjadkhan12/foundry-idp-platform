"""
Casbin Policy Migration for Business Unit-Scoped RBAC

This module migrates existing Casbin policies to support BU-scoped permissions.
It creates BU-scoped role assignments and permission policies.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid
from casbin import Enforcer

from app.models.business_unit import BusinessUnit, BusinessUnitMember
from app.models.rbac import Role
from app.core.organization import get_organization_domain
from app.core.permission_registry import get_bu_permissions, parse_permission_slug
from app.logger import logger


async def create_default_bu_role_permissions(
    role_name: str,
    business_unit_id: uuid.UUID,
    org_domain: str,
    enforcer: Enforcer
):
    """
    Create BU-scoped permissions for a role based on the permissions assigned to that role.
    
    This function:
    1. Gets the actual permissions assigned to the role from Casbin (not from templates)
    2. Filters for BU-scoped permissions (those starting with "business_unit:")
    3. Creates BU-scoped versions of those permissions (with "bu:{bu_id}:" prefix)
    
    This allows admins to create roles with any name and assign any permissions,
    and those permissions will be correctly applied when the role is used in a BU.
    
    Args:
        role_name: Name of the role (can be any name, e.g., "BU Owners", "Business Unit Manager", etc.)
        business_unit_id: UUID of the business unit
        org_domain: Organization domain
        enforcer: Casbin enforcer
    """
    logger.info(f"[create_default_bu_role_permissions] Creating BU permissions for role '{role_name}' in BU {business_unit_id}")
    
    # Get BU-scoped permission slugs for validation
    bu_perm_slugs = set(get_bu_permissions())
    
    # Get all policies for this role in the org domain (global scope)
    # These are the permissions that were assigned to the role when it was created/updated
    # Handle different enforcer types
    try:
        # Navigate to base enforcer if needed
        base_enforcer = enforcer
        if hasattr(enforcer, '_enforcer'):
            # It's an OrgAwareEnforcer, get the underlying enforcer
            base_enforcer = enforcer._enforcer
        if hasattr(base_enforcer, 'enforcer'):
            # It's a MultiTenantEnforcerWrapper, get the base Casbin enforcer
            base_enforcer = base_enforcer.enforcer
        
        # Get policies from base enforcer
        all_policies = base_enforcer.get_filtered_policy(0, role_name, org_domain)
        logger.info(f"[create_default_bu_role_permissions] Found {len(all_policies)} total policies for role '{role_name}' in org domain '{org_domain}'")
    except Exception as e:
        logger.error(f"[create_default_bu_role_permissions] Failed to get policies for role '{role_name}': {e}", exc_info=True)
        all_policies = []
    
    # Extract BU-scoped permissions from the role's policies
    # Format: [role, domain, obj, act, ...]
    # obj includes scope (e.g., "business_unit:deployments")
    bu_permission_slugs = []
    for policy in all_policies:
        if len(policy) >= 4:
            policy_obj = policy[2]  # e.g., "business_unit:deployments"
            policy_act = policy[3]   # e.g., "list" or "create:development"
            
            # Check if this is a BU-scoped permission
            # BU-scoped permissions have obj starting with "business_unit:"
            if policy_obj.startswith("business_unit:"):
                # Reconstruct the full permission slug
                perm_slug = f"{policy_obj}:{policy_act}"
                if perm_slug in bu_perm_slugs:
                    bu_permission_slugs.append(perm_slug)
                    logger.debug(f"[create_default_bu_role_permissions] Found BU permission: {perm_slug}")
    
    logger.info(f"[create_default_bu_role_permissions] Found {len(bu_permission_slugs)} BU-scoped permissions for role '{role_name}' from Casbin")
    
    # If no BU permissions found, log a warning but don't create any permissions
    # The role might not have BU permissions assigned, which is valid
    if not bu_permission_slugs:
        logger.warning(f"[create_default_bu_role_permissions] Role '{role_name}' has no BU-scoped permissions assigned. No BU permissions will be created. "
                     f"Admin should assign BU permissions to this role on the Roles page if it should be used in Business Units.")
        return
    
    # Use the actual permissions assigned to the role
    expanded_permissions = bu_permission_slugs
    
    # Add permissions to Casbin with BU context
    permissions_added = 0
    logger.info(f"[create_default_bu_role_permissions] Creating BU-scoped versions of {len(expanded_permissions)} permissions for role '{role_name}' in BU {business_unit_id}")
    for perm_slug in expanded_permissions:
        try:
            obj, act = parse_permission_slug(perm_slug)
            # Format: (role, org_domain, bu:{bu_id}:resource, action)
            bu_obj = f"bu:{business_unit_id}:{obj}"
            
            # Check if policy already exists
            # Navigate to base enforcer for policy operations
            base_enforcer = enforcer
            if hasattr(enforcer, '_enforcer'):
                base_enforcer = enforcer._enforcer
            if hasattr(base_enforcer, 'enforcer'):
                base_enforcer = base_enforcer.enforcer
            
            # Check if policy already exists
            existing = base_enforcer.get_filtered_policy(0, role_name, org_domain, bu_obj, act)
            
            if not existing:
                # Add policy to base enforcer
                base_enforcer.add_policy(role_name, org_domain, bu_obj, act)
                permissions_added += 1
                logger.debug(f"Added BU permission: {role_name} -> {bu_obj}:{act} for permission {perm_slug}")
            else:
                logger.debug(f"Permission already exists: {role_name} -> {bu_obj}:{act}")
        except Exception as e:
            logger.error(f"Failed to add permission {perm_slug} for role {role_name} in BU {business_unit_id}: {e}", exc_info=True)
    
    logger.info(f"[create_default_bu_role_permissions] Created {permissions_added} new BU-scoped permissions for role '{role_name}' in BU {business_unit_id}")
    
    if permissions_added > 0:
        logger.info(f"Created {permissions_added} BU-scoped permissions for role '{role_name}' in BU {business_unit_id}")
    else:
        logger.warning(f"No permissions were created for role '{role_name}' in BU {business_unit_id}. Expanded permissions: {expanded_permissions[:5]}...")


async def migrate_to_bu_scoped_policies(
    db: AsyncSession,
    enforcer: Enforcer
):
    """
    Migrate existing Casbin policies to support BU-scoped permissions.
    
    For each business unit:
    1. Get all members
    2. Add BU-scoped role assignment: (user_id, role_name, org_domain, bu_id)
    3. Create BU-scoped permission policies: (role, org_domain, bu:{bu_id}:resource, action)
    
    Note: This function assumes default roles have already been created and
    business_unit_members have been migrated to use role_id.
    """
    logger.info("Starting Casbin policy migration to BU-scoped format...")
    
    # Get all business units
    result = await db.execute(select(BusinessUnit))
    business_units = result.scalars().all()
    
    if not business_units:
        logger.info("No business units found, skipping policy migration")
        return
    
    logger.info(f"Found {len(business_units)} business units to migrate")
    
    total_members = 0
    total_policies = 0
    
    for bu in business_units:
        # Get organization domain
        org_domain = get_organization_domain(bu.organization)
        
        # Get all members of this BU
        members_result = await db.execute(
            select(BusinessUnitMember)
            .options(selectinload(BusinessUnitMember.role))
            .where(BusinessUnitMember.business_unit_id == bu.id)
        )
        members = members_result.scalars().all()
        
        if not members:
            logger.debug(f"No members in business unit {bu.name}, skipping")
            continue
        
        logger.info(f"Processing business unit {bu.name} ({bu.id}) with {len(members)} members")
        
        for member in members:
            if not member.role:
                logger.warning(f"Member {member.user_id} in BU {bu.id} has no role, skipping")
                continue
            
            role = member.role
            user_id = str(member.user_id)
            bu_id_str = str(bu.id)
            
            # Add BU-scoped role assignment: (user_id, role_name, org_domain, bu_id)
            # Note: Casbin grouping policies are (user, role, domain), so we'll store
            # BU context in the role name or use a different approach
            # For now, we'll use a composite role name: role_name@bu_id
            # OR we can extend the grouping policy format to include BU ID
            # Since Casbin model uses 3-param grouping, we'll use composite role names
            
            # Option 1: Use composite role name (simpler, works with current model)
            composite_role = f"{role.name}@bu:{bu_id_str}"
            
            # Check if grouping policy already exists
            existing = enforcer.get_filtered_grouping_policy(0, user_id)
            has_bu_role = any(
                len(p) >= 3 and p[1] == composite_role and p[2] == org_domain
                for p in existing
            )
            
            if not has_bu_role:
                enforcer.add_grouping_policy(user_id, composite_role, org_domain)
                total_members += 1
                logger.debug(f"Added BU role assignment: {user_id} -> {composite_role} in {org_domain}")
            
            # IMPORTANT: Add role hierarchy so composite role inherits from base role
            # This allows Casbin to match permissions stored for the base role
            existing_hierarchy = enforcer.get_filtered_grouping_policy(0, composite_role)
            has_role_hierarchy = any(
                len(p) >= 3 and p[1] == role.name and p[2] == org_domain
                for p in existing_hierarchy
            )
            
            if not has_role_hierarchy:
                enforcer.add_grouping_policy(composite_role, role.name, org_domain)
                logger.debug(f"Added role hierarchy: {composite_role} -> {role.name} in {org_domain}")
            
            # Create BU-scoped permission policies for this role
            # Only create once per role per BU (not per member)
            # Check if we've already created policies for this role in this BU
            bu_obj_sample = f"bu:{bu_id_str}:deployments"
            existing_policies = enforcer.get_filtered_policy(0, role.name, org_domain, bu_obj_sample)
            
            if not existing_policies:
                # Create permissions for this role in this BU
                await create_default_bu_role_permissions(role.name, bu.id, org_domain, enforcer)
                total_policies += 1
    
    # Save all policy changes
    enforcer.save_policy()
    
    logger.info(f"✅ Casbin policy migration completed:")
    logger.info(f"  - Processed {len(business_units)} business units")
    logger.info(f"  - Added {total_members} BU role assignments")
    logger.info(f"  - Created {total_policies} BU permission policy sets")

