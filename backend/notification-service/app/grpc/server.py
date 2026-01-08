"""gRPC server for notification microservice"""
import asyncio
import grpc
from concurrent import futures
import logging

from app.config import settings
from app.grpc.notification_servicer import NotificationServicer

# Import generated proto modules
try:
    from proto import notification_pb2_grpc
except ImportError:
    notification_pb2_grpc = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def serve():
    """Start the gRPC server"""
    if not notification_pb2_grpc:
        logger.error("Proto files not generated. Run: python -m grpc_tools.protoc --proto_path=proto --python_out=proto --grpc_python_out=proto proto/notification.proto")
        return
    
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register servicer
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(
        NotificationServicer(), server
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
