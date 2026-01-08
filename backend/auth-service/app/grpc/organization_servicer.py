"""Organization management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.organization_service import organization_service


class OrganizationServicer(auth_pb2_grpc.OrganizationServiceServicer):
    """gRPC servicer for organization management operations"""
    
    async def CreateOrganization(self, request, context):
        """Create organization"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                org = await organization_service.create_organization(
                    request.name,
                    request.slug,
                    request.description if request.description else None,
                    db
                )
                return auth_pb2.OrganizationResponse(
                    id=org["id"],
                    name=org["name"],
                    slug=org["slug"],
                    description=org["description"] or "",
                    is_active=org["is_active"],
                    created_at=org["created_at"],
                    updated_at=org["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.OrganizationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.OrganizationResponse()
    
    async def UpdateOrganization(self, request, context):
        """Update organization"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Note: In proto3, we can't distinguish between unset and False for bool
                # Workaround: if is_active is True, we know it was set
                # If is_active is False and other fields are being updated, assume it was intentional
                # Otherwise, don't update is_active
                is_active_value = None
                if request.is_active:
                    is_active_value = True
                elif request.is_active == False and (request.name or request.description):
                    # If False and other fields are set, assume it was intentional
                    is_active_value = False
                
                org = await organization_service.update_organization(
                    request.organization_id,
                    request.name if request.name else None,
                    request.description if request.description else None,
                    is_active_value,
                    db
                )
                return auth_pb2.OrganizationResponse(
                    id=org["id"],
                    name=org["name"],
                    slug=org["slug"],
                    description=org["description"] or "",
                    is_active=org["is_active"],
                    created_at=org["created_at"],
                    updated_at=org["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.OrganizationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.OrganizationResponse()
    
    async def DeleteOrganization(self, request, context):
        """Delete organization"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await organization_service.delete_organization(
                    request.organization_id,
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
    
    async def GetOrganization(self, request, context):
        """Get organization by ID"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                org = await organization_service.get_organization(
                    request.organization_id,
                    db
                )
                return auth_pb2.OrganizationResponse(
                    id=org["id"],
                    name=org["name"],
                    slug=org["slug"],
                    description=org["description"] or "",
                    is_active=org["is_active"],
                    created_at=org["created_at"],
                    updated_at=org["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.OrganizationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.OrganizationResponse()
    
    async def ListOrganizations(self, request, context):
        """List all organizations"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                orgs = await organization_service.list_organizations(
                    request.skip if request.skip > 0 else 0,
                    request.limit if request.limit > 0 else 100,
                    db
                )
                return auth_pb2.ListOrganizationsResponse(
                    organizations=[
                        auth_pb2.OrganizationResponse(
                            id=org["id"],
                            name=org["name"],
                            slug=org["slug"],
                            description=org["description"] or "",
                            is_active=org["is_active"],
                            created_at=org["created_at"],
                            updated_at=org["updated_at"]
                        )
                        for org in orgs
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListOrganizationsResponse()
    
    async def GetCurrentOrganization(self, request, context):
        """Get current user's organization"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                org = await organization_service.get_current_organization(
                    request.user_id,
                    db
                )
                return auth_pb2.OrganizationResponse(
                    id=org["id"],
                    name=org["name"],
                    slug=org["slug"],
                    description=org["description"] or "",
                    is_active=org["is_active"],
                    created_at=org["created_at"],
                    updated_at=org["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.OrganizationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.OrganizationResponse()
