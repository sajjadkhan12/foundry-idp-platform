"""gRPC server for deployment microservice"""
import asyncio
import grpc
from concurrent import futures
import logging

from app.config import settings
from app.grpc.deployment_servicer import DeploymentServicer

# Import generated proto modules
from proto import deployment_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def serve():
    """Start the gRPC server"""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register servicer
    deployment_pb2_grpc.add_DeploymentServiceServicer_to_server(
        DeploymentServicer(), server
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
