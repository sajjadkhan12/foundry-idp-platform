from fastapi import APIRouter, Depends
from typing import List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps.permissions import is_allowed
from app.api.deps.enforcer import OrgAwareEnforcer, get_org_aware_enforcer
from app.database import get_db
from app.schemas.rbac import PermissionResponse
from app.models.rbac import PermissionMetadata
from app.core.permission_registry import PERMISSIONS_BY_SLUG, get_permission, parse_permission_slug

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.get("/", response_model=List[PermissionResponse])
async def list_permissions(
    current_user = Depends(is_allowed("platform:permissions:list")),
    enforcer: OrgAwareEnforcer = Depends(get_org_aware_enforcer),
    db: AsyncSession = Depends(get_db)
):
    """
    List all permissions with enriched metadata.
    Returns all 95 unique permissions (no duplicates - each permission slug is unique).
    With the updated parse_permission_slug, scope is included in object name, making all permissions unique.
    """
    # Try to get metadata from database first, fallback to registry
    db_metadata = {}
    try:
        result = await db.execute(select(PermissionMetadata))
        db_metadata = {perm.slug: perm for perm in result.scalars().all()}
    except Exception:
        # Table doesn't exist yet - will use registry metadata only
        pass
    
    # Build permissions list - all permissions are now unique (no deduplication needed)
    all_permissions = []
    
    for perm_def in PERMISSIONS_BY_SLUG.values():
        slug = perm_def["slug"]
        
        # Get database metadata for this permission
        db_perm = db_metadata.get(slug)
        
        perm_response = PermissionResponse(
            id=db_perm.id if db_perm else None,
            slug=slug,
            name=perm_def.get("name"),
            description=perm_def.get("description"),
            category=perm_def.get("category"),
            resource=perm_def.get("resource"),
            action=perm_def.get("action"),
            environment=perm_def.get("environment"),
            icon=perm_def.get("icon"),
            created_at=db_perm.created_at if db_perm else None,
            equivalent_slugs=None  # No equivalent slugs - all permissions are unique now
        )
        all_permissions.append(perm_response)
    
    # Sort by category, then by name
    all_permissions.sort(key=lambda p: (p.category or "", p.name or p.slug))
    
    return all_permissions