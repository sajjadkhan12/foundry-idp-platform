"""Group management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.group_service import group_service


class GroupServicer(auth_pb2_grpc.GroupServiceServicer):
    """gRPC servicer for group management operations"""
    
    async def CreateGroup(self, request, context):
        """Create group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                group = await group_service.create_group(
                    request.name,
                    request.description if request.description else None,
                    db
                )
                return auth_pb2.GroupResponse(
                    id=group["id"],
                    name=group["name"],
                    description=group["description"],
                    created_at=group["created_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(str(e))
                return auth_pb2.GroupResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.GroupResponse()
    
    async def UpdateGroup(self, request, context):
        """Update group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                group = await group_service.update_group(
                    request.group_id,
                    request.name if request.name else None,
                    request.description if request.description else None,
                    db
                )
                return auth_pb2.GroupResponse(
                    id=group["id"],
                    name=group["name"],
                    description=group["description"],
                    created_at=group["created_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.GroupResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.GroupResponse()
    
    async def DeleteGroup(self, request, context):
        """Delete group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await group_service.delete_group(request.group_id, db)
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def GetGroup(self, request, context):
        """Get group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                group = await group_service.get_group(request.group_id, db)
                return auth_pb2.GroupResponse(
                    id=group["id"],
                    name=group["name"],
                    description=group["description"],
                    created_at=group["created_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.GroupResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.GroupResponse()
    
    async def ListGroups(self, request, context):
        """List groups"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                groups = await group_service.list_groups(db)
                return auth_pb2.ListGroupsResponse(
                    groups=[
                        auth_pb2.GroupResponse(
                            id=g["id"],
                            name=g["name"],
                            description=g["description"],
                            created_at=g["created_at"]
                        )
                        for g in groups
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListGroupsResponse()
    
    async def AddGroupMember(self, request, context):
        """Add group member"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Get organization_id from user - simplified for now
                from app.models.rbac import User
                from sqlalchemy.future import select
                from app.core.organization import get_user_organization, get_organization_domain
                import uuid
                
                user_result = await db.execute(select(User).where(User.id == uuid.UUID(request.user_id)))
                user = user_result.scalar_one_or_none()
                if not user:
                    raise ValueError("User not found")
                
                from app.core.organization import get_user_organization
                org = await get_user_organization(user, db)
                org_domain = get_organization_domain(org)
                
                await group_service.add_group_member(
                    request.group_id,
                    request.user_id,
                    org_domain,
                    db
                )
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def RemoveGroupMember(self, request, context):
        """Remove group member"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                from app.models.rbac import User
                from sqlalchemy.future import select
                from app.core.organization import get_user_organization, get_organization_domain
                import uuid
                
                user_result = await db.execute(select(User).where(User.id == uuid.UUID(request.user_id)))
                user = user_result.scalar_one_or_none()
                if not user:
                    raise ValueError("User not found")
                
                org = await get_user_organization(user, db)
                org_domain = get_organization_domain(org)
                
                await group_service.remove_group_member(
                    request.group_id,
                    request.user_id,
                    org_domain,
                    db
                )
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
