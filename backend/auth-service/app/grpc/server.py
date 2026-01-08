"""gRPC server for auth microservice"""
import asyncio
import grpc
from concurrent import futures
import logging

from app.config import settings
from app.grpc.auth_servicer import AuthenticationServicer
from app.grpc.authorization_servicer import AuthorizationServicer
from app.grpc.user_servicer import UserServicer
from app.grpc.role_servicer import RoleServicer
from app.grpc.group_servicer import GroupServicer
from app.grpc.business_unit_servicer import BusinessUnitServicer
from app.grpc.organization_servicer import OrganizationServicer
from app.grpc.business_unit_group_servicer import BusinessUnitGroupServicer
from app.grpc.credential_servicer import CredentialServicer

# Import generated proto modules
from proto import auth_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def serve():
    """Start the gRPC server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register servicers
    auth_pb2_grpc.add_AuthenticationServiceServicer_to_server(
        AuthenticationServicer(), server
    )
    auth_pb2_grpc.add_AuthorizationServiceServicer_to_server(
        AuthorizationServicer(), server
    )
    auth_pb2_grpc.add_UserServiceServicer_to_server(
        UserServicer(), server
    )
    auth_pb2_grpc.add_RoleServiceServicer_to_server(
        RoleServicer(), server
    )
    auth_pb2_grpc.add_GroupServiceServicer_to_server(
        GroupServicer(), server
    )
    auth_pb2_grpc.add_BusinessUnitServiceServicer_to_server(
        BusinessUnitServicer(), server
    )
    auth_pb2_grpc.add_OrganizationServiceServicer_to_server(
        OrganizationServicer(), server
    )
    auth_pb2_grpc.add_BusinessUnitGroupServiceServicer_to_server(
        BusinessUnitGroupServicer(), server
    )
    auth_pb2_grpc.add_CredentialServiceServicer_to_server(
        CredentialServicer(), server
    )
    
    # Listen on port
    listen_addr = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server")
        await server.stop(5)


if __name__ == "__main__":
    asyncio.run(serve())
