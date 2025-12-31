"""API Dependencies - Modular dependency structure"""
from .auth import get_current_user, get_current_active_superuser, oauth2_scheme
from .permissions import is_allowed, is_allowed_bu, is_allowed_platform
from .business_unit import get_active_business_unit, require_business_unit
from .enforcer import OrgAwareEnforcer, get_org_aware_enforcer
from .helpers import (
    is_platform_admin,
    get_user_platform_roles,
    get_org_domain,
    get_bu_membership,
    get_user_bu_role,
    check_bu_permission
)

__all__ = [
    'get_current_user',
    'get_current_active_superuser', 
    'oauth2_scheme',
    'is_allowed',
    'is_allowed_bu',
    'is_allowed_platform',
    'get_active_business_unit',
    'require_business_unit',
    'OrgAwareEnforcer',
    'get_org_aware_enforcer',
    'is_platform_admin',
    'get_user_platform_roles',
    'get_org_domain',
    'get_bu_membership',
    'get_user_bu_role',
    'check_bu_permission',
]
