"""Business unit management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.business_unit_service import business_unit_service


class BusinessUnitServicer(auth_pb2_grpc.BusinessUnitServiceServicer):
    """gRPC servicer for business unit management operations"""
    
    async def CreateBusinessUnit(self, request, context):
        """Create business unit"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                bu = await business_unit_service.create_business_unit(
                    request.name,
                    request.slug,
                    request.description if request.description else None,
                    request.organization_id,
                    db
                )
                return auth_pb2.BusinessUnitResponse(
                    id=bu["id"],
                    name=bu["name"],
                    slug=bu["slug"],
                    description=bu["description"],
                    organization_id=bu["organization_id"],
                    is_active=bu["is_active"],
                    role=bu["role"] or "",
                    member_count=bu["member_count"],
                    can_manage_members=bu["can_manage_members"],
                    created_at=bu["created_at"],
                    updated_at=bu["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(str(e))
                return auth_pb2.BusinessUnitResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.BusinessUnitResponse()
    
    async def UpdateBusinessUnit(self, request, context):
        """Update business unit"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                bu = await business_unit_service.update_business_unit(
                    request.business_unit_id,
                    request.name if request.name else None,
                    request.description if request.description else None,
                    request.is_active if request.HasField("is_active") else None,
                    db
                )
                return auth_pb2.BusinessUnitResponse(
                    id=bu["id"],
                    name=bu["name"],
                    slug=bu["slug"],
                    description=bu["description"],
                    organization_id=bu["organization_id"],
                    is_active=bu["is_active"],
                    role=bu["role"] or "",
                    member_count=bu["member_count"],
                    can_manage_members=bu["can_manage_members"],
                    created_at=bu["created_at"],
                    updated_at=bu["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.BusinessUnitResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.BusinessUnitResponse()
    
    async def DeleteBusinessUnit(self, request, context):
        """Delete business unit"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await business_unit_service.delete_business_unit(request.business_unit_id, db)
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def GetBusinessUnit(self, request, context):
        """Get business unit"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                bu = await business_unit_service.get_business_unit(request.business_unit_id, db)
                return auth_pb2.BusinessUnitResponse(
                    id=bu["id"],
                    name=bu["name"],
                    slug=bu["slug"],
                    description=bu["description"],
                    organization_id=bu["organization_id"],
                    is_active=bu["is_active"],
                    role=bu["role"] or "",
                    member_count=bu["member_count"],
                    can_manage_members=bu["can_manage_members"],
                    created_at=bu["created_at"],
                    updated_at=bu["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.BusinessUnitResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.BusinessUnitResponse()
    
    async def ListBusinessUnits(self, request, context):
        """List business units"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                bus = await business_unit_service.list_business_units(
                    request.user_id if request.user_id else None,
                    request.organization_id if request.organization_id else None,
                    db
                )
                return auth_pb2.ListBusinessUnitsResponse(
                    business_units=[
                        auth_pb2.BusinessUnitResponse(
                            id=bu["id"],
                            name=bu["name"],
                            slug=bu["slug"],
                            description=bu["description"],
                            organization_id=bu["organization_id"],
                            is_active=bu["is_active"],
                            role=bu["role"] or "",
                            member_count=bu["member_count"],
                            can_manage_members=bu["can_manage_members"],
                            created_at=bu["created_at"],
                            updated_at=bu["updated_at"]
                        )
                        for bu in bus
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListBusinessUnitsResponse()
    
    async def AddBusinessUnitMember(self, request, context):
        """Add business unit member"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await business_unit_service.add_business_unit_member(
                    request.business_unit_id,
                    request.user_email,
                    list(request.role_ids) if request.role_ids else [],
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
    
    async def RemoveBusinessUnitMember(self, request, context):
        """Remove business unit member"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await business_unit_service.remove_business_unit_member(
                    request.business_unit_id,
                    request.user_id,
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
    
    async def ListBusinessUnitMembers(self, request, context):
        """List business unit members"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                members = await business_unit_service.list_business_unit_members(
                    request.business_unit_id,
                    db
                )
                return auth_pb2.ListBusinessUnitMembersResponse(
                    members=[
                        auth_pb2.BusinessUnitMemberResponse(
                            id=m["id"],
                            business_unit_id=m["business_unit_id"],
                            user_id=m["user_id"],
                            user_email=m["user_email"],
                            user_name=m["user_name"] or "",
                            role=m["role"],
                            role_id=m["role_id"] or "",
                            created_at=m["created_at"]
                        )
                        for m in members
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListBusinessUnitMembersResponse()
