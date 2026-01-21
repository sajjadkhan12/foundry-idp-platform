"""
Shared dependencies for auth-service
"""
import logging
import grpc
from typing import Optional
from fastapi import Header, HTTPException, Depends
from proto import auth_pb2, auth_pb2_grpc

# Configure logging
logger = logging.getLogger(__name__)

# Import servicers
from app.grpc.auth_servicer import AuthenticationServicer
from app.grpc.authorization_servicer import AuthorizationServicer
from app.grpc.user_servicer import UserServicer
from app.grpc.role_servicer import RoleServicer
from app.grpc.group_servicer import GroupServicer
from app.grpc.business_unit_servicer import BusinessUnitServicer
from app.grpc.organization_servicer import OrganizationServicer
from app.grpc.business_unit_group_servicer import BusinessUnitGroupServicer
from app.grpc.credential_servicer import CredentialServicer
from app.grpc.configuration_servicer import ConfigurationServicer

# Check proto availability
PROTO_AVAILABLE = True
try:
    from proto import auth_pb2
except ImportError:
    PROTO_AVAILABLE = False


# Create servicer instances
auth_servicer = AuthenticationServicer()
authz_servicer = AuthorizationServicer()
user_servicer = UserServicer()
role_servicer = RoleServicer()
group_servicer = GroupServicer()
bu_servicer = BusinessUnitServicer()
org_servicer = OrganizationServicer()
bu_group_servicer = BusinessUnitGroupServicer()
credential_servicer = CredentialServicer()
config_servicer = ConfigurationServicer()


class MockContext:
    """Mock gRPC context for internal calls"""
    def __init__(self):
        self._code = None
        self._details = ""
    
    @property
    def code(self):
        return self._code
        
    @property
    def details(self):
        return self._details
    
    def abort(self, code, details):
        self._code = code
        self._details = details
        # For internal usage, we might not want to verify raise exception immediately 
        # but let the caller check code
    
    def set_code(self, code):
        self._code = code
        
    def set_details(self, details):
        self._details = details


def _get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract token from Authorization header"""
    if authorization:
        if authorization.startswith("Bearer "):
            return authorization[7:]
        elif authorization.startswith("bearer "):
            return authorization[7:]
    return None


async def _get_user_id_from_token(token: Optional[str]) -> Optional[str]:
    """Extract user ID from token"""
    if not token or not PROTO_AVAILABLE:
        return None
    try:
        context = MockContext()
        grpc_request = auth_pb2.ValidateTokenRequest(token=token)
        response = await auth_servicer.ValidateToken(grpc_request, context)
        if not context.code:
            return response.user_id
        else:
            logger.warning(f"ValidateToken gRPC failed: {context.details}")
    except Exception as e:
        logger.error(f"Error in _get_user_id_from_token: {e}", exc_info=True)
    return None


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency to verify token and return user ID.
    Raises HTTPException(401) if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
    user_id = await _get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    return user_id
