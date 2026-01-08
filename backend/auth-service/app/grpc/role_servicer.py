"""Role management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.role_service import role_service


class RoleServicer(auth_pb2_grpc.RoleServiceServicer):
    """gRPC servicer for role management operations"""
    
    async def CreateRole(self, request, context):
        """Create role"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                role = await role_service.create_role(
                    request.name,
                    request.description if request.description else None,
                    request.is_platform_role,
                    db,
                    permissions=list(request.permissions) if request.permissions else []
                )
                return auth_pb2.RoleResponse(
                    id=role["id"],
                    name=role["name"],
                    description=role["description"],
                    is_platform_role=role["is_platform_role"],
                    created_at=role["created_at"],
                    permissions=role.get("permissions", [])
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(str(e))
                return auth_pb2.RoleResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.RoleResponse()
    
    async def UpdateRole(self, request, context):
        """Update role"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                role = await role_service.update_role(
                    request.role_id,
                    request.name if request.name else None,
                    request.description if request.description else None,
                    request.is_platform_role if request.HasField("is_platform_role") else None,
                    db,
                    permissions=list(request.permissions) if request.permissions else None
                )
                return auth_pb2.RoleResponse(
                    id=role["id"],
                    name=role["name"],
                    description=role["description"],
                    is_platform_role=role["is_platform_role"],
                    created_at=role["created_at"],
                    permissions=role.get("permissions", [])
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.RoleResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.RoleResponse()
    
    async def DeleteRole(self, request, context):
        """Delete role"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await role_service.delete_role(request.role_id, db)
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def GetRole(self, request, context):
        """Get role"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                role = await role_service.get_role(request.role_id, db)
                return auth_pb2.RoleResponse(
                    id=role["id"],
                    name=role["name"],
                    description=role["description"],
                    is_platform_role=role["is_platform_role"],
                    created_at=role["created_at"],
                    permissions=role.get("permissions", [])
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.RoleResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.RoleResponse()
    
    async def ListRoles(self, request, context):
        """List roles"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # In proto3, bool fields don't support HasField, so we use the value directly
                roles = await role_service.list_roles(
                    request.platform_roles_only,
                    db
                )
                return auth_pb2.ListRolesResponse(
                    roles=[
                        auth_pb2.RoleResponse(
                            id=r["id"],
                            name=r["name"],
                            description=r["description"],
                            is_platform_role=r["is_platform_role"],
                            created_at=r["created_at"],
                            permissions=r.get("permissions", [])
                        )
                        for r in roles
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListRolesResponse()
    
    async def AssignRole(self, request, context):
        """Assign role"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await role_service.assign_role(
                    request.user_id,
                    request.role_name,
                    request.organization_id,
                    db
                )
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def RemoveRole(self, request, context):
        """Remove role"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await role_service.remove_role(
                    request.user_id,
                    request.role_name,
                    request.organization_id,
                    db
                )
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
