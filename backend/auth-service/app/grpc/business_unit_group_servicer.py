"""Business Unit Group management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.business_unit_group_service import business_unit_group_service


class BusinessUnitGroupServicer(auth_pb2_grpc.BusinessUnitGroupServiceServicer):
    """gRPC servicer for business unit group management operations"""
    
    async def CreateBusinessUnitGroup(self, request, context):
        """Create business unit group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                if not request.role_id:
                    raise ValueError("role_id is required")
                group = await business_unit_group_service.create_business_unit_group(
                    request.business_unit_id,
                    request.name,
                    request.description if request.description else None,
                    request.role_id,
                    db
                )
                return auth_pb2.BusinessUnitGroupResponse(
                    id=group["id"],
                    business_unit_id=group["business_unit_id"],
                    name=group["name"],
                    description=group["description"] or "",
                    created_at=group["created_at"],
                    updated_at=group["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.BusinessUnitGroupResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.BusinessUnitGroupResponse()
    
    async def UpdateBusinessUnitGroup(self, request, context):
        """Update business unit group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                group = await business_unit_group_service.update_business_unit_group(
                    request.business_unit_id,
                    request.group_id,
                    request.name if request.name else None,
                    request.description if request.description else None,
                    db
                )
                return auth_pb2.BusinessUnitGroupResponse(
                    id=group["id"],
                    business_unit_id=group["business_unit_id"],
                    name=group["name"],
                    description=group["description"] or "",
                    created_at=group["created_at"],
                    updated_at=group["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.BusinessUnitGroupResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.BusinessUnitGroupResponse()
    
    async def DeleteBusinessUnitGroup(self, request, context):
        """Delete business unit group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await business_unit_group_service.delete_business_unit_group(
                    request.business_unit_id,
                    request.group_id,
                    db
                )
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def GetBusinessUnitGroup(self, request, context):
        """Get business unit group by ID"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                group = await business_unit_group_service.get_business_unit_group(
                    request.business_unit_id,
                    request.group_id,
                    db
                )
                return auth_pb2.BusinessUnitGroupResponse(
                    id=group["id"],
                    business_unit_id=group["business_unit_id"],
                    name=group["name"],
                    description=group["description"] or "",
                    created_at=group["created_at"],
                    updated_at=group["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.BusinessUnitGroupResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.BusinessUnitGroupResponse()
    
    async def ListBusinessUnitGroups(self, request, context):
        """List all groups in a business unit"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                groups = await business_unit_group_service.list_business_unit_groups(
                    request.business_unit_id,
                    db
                )
                return auth_pb2.ListBusinessUnitGroupsResponse(
                    groups=[
                        auth_pb2.BusinessUnitGroupResponse(
                            id=group["id"],
                            business_unit_id=group["business_unit_id"],
                            name=group["name"],
                            description=group["description"] or "",
                            created_at=group["created_at"],
                            updated_at=group["updated_at"]
                        )
                        for group in groups
                    ]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.ListBusinessUnitGroupsResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListBusinessUnitGroupsResponse()
    
    async def AddBusinessUnitGroupMember(self, request, context):
        """Add member to business unit group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await business_unit_group_service.add_business_unit_group_member(
                    request.business_unit_id,
                    request.group_id,
                    request.user_id,
                    db
                )
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def RemoveBusinessUnitGroupMember(self, request, context):
        """Remove member from business unit group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await business_unit_group_service.remove_business_unit_group_member(
                    request.business_unit_id,
                    request.group_id,
                    request.user_id,
                    db
                )
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def ListBusinessUnitGroupMembers(self, request, context):
        """List all members of a business unit group"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                members = await business_unit_group_service.list_business_unit_group_members(
                    request.business_unit_id,
                    request.group_id,
                    db
                )
                return auth_pb2.ListBusinessUnitGroupMembersResponse(
                    members=[
                        auth_pb2.BusinessUnitGroupMemberResponse(
                            id=member["id"],
                            business_unit_id=member["business_unit_id"],
                            group_id=member["group_id"],
                            user_id=member["user_id"],
                            user_email=member["user_email"],
                            user_name=member["user_name"],
                            created_at=member["created_at"]
                        )
                        for member in members
                    ]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.ListBusinessUnitGroupMembersResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListBusinessUnitGroupMembersResponse()
