"""Credential management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.credential_service import credential_service


class CredentialServicer(auth_pb2_grpc.CredentialServiceServicer):
    """gRPC servicer for credential management operations"""
    
    async def CreateCredential(self, request, context):
        """Create or update credential"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Get organization_id from metadata or request
                organization_id = None
                if hasattr(request, 'organization_id') and request.organization_id:
                    organization_id = request.organization_id
                else:
                    # Try to get from metadata
                    metadata = dict(context.invocation_metadata())
                    if 'organization-id' in metadata:
                        organization_id = metadata['organization-id']
                
                if not organization_id:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("organization_id is required")
                    return auth_pb2.CredentialResponse()
                
                cred = await credential_service.create_credential(
                    request.name,
                    request.provider,
                    request.credentials,
                    organization_id,
                    db
                )
                return auth_pb2.CredentialResponse(
                    id=str(cred["id"]),
                    name=cred["name"],
                    provider=cred["provider"],
                    created_at=cred["created_at"],
                    updated_at=cred["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.CredentialResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.CredentialResponse()
    
    async def UpdateCredential(self, request, context):
        """Update credential"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Get organization_id from metadata or request
                organization_id = None
                if hasattr(request, 'organization_id') and request.organization_id:
                    organization_id = request.organization_id
                else:
                    metadata = dict(context.invocation_metadata())
                    if 'organization-id' in metadata:
                        organization_id = metadata['organization-id']
                
                if not organization_id:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("organization_id is required")
                    return auth_pb2.CredentialResponse()
                
                cred_id = int(request.credential_id)
                cred = await credential_service.update_credential(
                    cred_id,
                    request.name if request.name else None,
                    request.credentials if request.credentials else None,
                    organization_id,
                    db
                )
                return auth_pb2.CredentialResponse(
                    id=str(cred["id"]),
                    name=cred["name"],
                    provider=cred["provider"],
                    created_at=cred["created_at"],
                    updated_at=cred["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.CredentialResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.CredentialResponse()
    
    async def DeleteCredential(self, request, context):
        """Delete credential"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Get organization_id from metadata or request
                organization_id = None
                if hasattr(request, 'organization_id') and request.organization_id:
                    organization_id = request.organization_id
                else:
                    metadata = dict(context.invocation_metadata())
                    if 'organization-id' in metadata:
                        organization_id = metadata['organization-id']
                
                if not organization_id:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("organization_id is required")
                    return auth_pb2.Empty()
                
                cred_id = int(request.credential_id)
                await credential_service.delete_credential(
                    cred_id,
                    organization_id,
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
    
    async def GetCredential(self, request, context):
        """Get credential by ID"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Get organization_id from metadata or request
                organization_id = None
                if hasattr(request, 'organization_id') and request.organization_id:
                    organization_id = request.organization_id
                else:
                    metadata = dict(context.invocation_metadata())
                    if 'organization-id' in metadata:
                        organization_id = metadata['organization-id']
                
                if not organization_id:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("organization_id is required")
                    return auth_pb2.CredentialResponse()
                
                cred_id = int(request.credential_id)
                cred = await credential_service.get_credential(
                    cred_id,
                    organization_id,
                    db
                )
                return auth_pb2.CredentialResponse(
                    id=str(cred["id"]),
                    name=cred["name"],
                    provider=cred["provider"],
                    created_at=cred["created_at"],
                    updated_at=cred["updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.CredentialResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.CredentialResponse()
    
    async def ListCredentials(self, request, context):
        """List all credentials"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Get organization_id from metadata or request
                organization_id = None
                if hasattr(request, 'organization_id') and request.organization_id:
                    organization_id = request.organization_id
                else:
                    metadata = dict(context.invocation_metadata())
                    if 'organization-id' in metadata:
                        organization_id = metadata['organization-id']
                
                if not organization_id:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("organization_id is required")
                    return auth_pb2.ListCredentialsResponse()
                
                creds = await credential_service.list_credentials(organization_id, db)
                return auth_pb2.ListCredentialsResponse(
                    credentials=[
                        auth_pb2.CredentialResponse(
                            id=str(cred["id"]),
                            name=cred["name"],
                            provider=cred["provider"],
                            created_at=cred["created_at"],
                            updated_at=cred["updated_at"]
                        )
                        for cred in creds
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListCredentialsResponse()
