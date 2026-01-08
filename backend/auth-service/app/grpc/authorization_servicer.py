"""Authorization gRPC servicer"""
import grpc
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.authorization_service import authorization_service
try:
    from proto import auth_pb2, auth_pb2_grpc
except ImportError:
    # Fallback for development
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from proto import auth_pb2, auth_pb2_grpc


class AuthorizationServicer(auth_pb2_grpc.AuthorizationServiceServicer):
    """gRPC servicer for authorization operations"""
    
    async def CheckPermission(
        self,
        request: auth_pb2.PermissionCheckRequest,
        context: grpc.ServicerContext
    ) -> auth_pb2.PermissionCheckResponse:
        """Check if user has permission"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                allowed = await authorization_service.check_permission(
                    request.user_id,
                    request.permission_slug,
                    request.business_unit_id if request.business_unit_id else None,
                    request.organization_id if request.organization_id else None,
                    db
                )
                return auth_pb2.PermissionCheckResponse(
                    allowed=allowed,
                    message="Permission granted" if allowed else "Permission denied"
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.PermissionCheckResponse(allowed=False, message=str(e))
    
    async def GetUserRoles(
        self,
        request: auth_pb2.GetUserRolesRequest,
        context: grpc.ServicerContext
    ) -> auth_pb2.GetUserRolesResponse:
        """Get user roles"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                roles = await authorization_service.get_user_roles(
                    request.user_id,
                    request.organization_id if request.organization_id else None,
                    db
                )
                return auth_pb2.GetUserRolesResponse(roles=roles)
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.GetUserRolesResponse(roles=[])
    
    async def GetUserPermissions(
        self,
        request: auth_pb2.GetUserPermissionsRequest,
        context: grpc.ServicerContext
    ) -> auth_pb2.GetUserPermissionsResponse:
        """Get user permissions"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                permissions = await authorization_service.get_user_permissions(
                    request.user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    request.organization_id if request.organization_id else None,
                    db
                )
                return auth_pb2.GetUserPermissionsResponse(permissions=permissions)
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.GetUserPermissionsResponse(permissions=[])
    
    async def IsPlatformAdmin(
        self,
        request: auth_pb2.IsPlatformAdminRequest,
        context: grpc.ServicerContext
    ) -> auth_pb2.IsPlatformAdminResponse:
        """Check if user is platform admin"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                is_admin = await authorization_service.is_platform_admin(
                    request.user_id,
                    request.organization_id if request.organization_id else None,
                    db
                )
                return auth_pb2.IsPlatformAdminResponse(is_admin=is_admin)
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.IsPlatformAdminResponse(is_admin=False)
