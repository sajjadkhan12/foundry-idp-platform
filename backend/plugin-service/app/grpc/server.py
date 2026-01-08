"""gRPC server for plugin microservice"""
import asyncio
import grpc
from concurrent import futures
import logging

from app.config import settings
from app.grpc.plugin_servicer import PluginServicer

try:
    from proto import plugin_pb2_grpc
except ImportError:
    plugin_pb2_grpc = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def serve():
    """Start the gRPC server"""
    if not plugin_pb2_grpc:
        logger.error("Proto files not generated. Run: python -m grpc_tools.protoc --proto_path=proto --python_out=proto --grpc_python_out=proto proto/plugin.proto")
        return
    
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register servicer
    plugin_pb2_grpc.add_PluginServiceServicer_to_server(
        PluginServicer(), server
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
