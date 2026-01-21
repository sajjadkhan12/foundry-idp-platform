"""Helper to retrieve configurations from auth-service"""
import grpc
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Logger
logger = logging.getLogger(__name__)

async def get_config_from_auth_service(
    organization_id: str,
    config_key: str,
    business_unit_id: Optional[str] = None
) -> Optional[str]:
    """
    Get configuration value from auth-service via gRPC
    
    Args:
        organization_id: Organization ID
        config_key: Configuration key
        business_unit_id: Optional business unit ID
    
    Returns:
        Configuration value or None if not found
    """
    try:
        from proto import auth_pb2, auth_pb2_grpc
    except ImportError:
        logger.warning("Auth proto not available, cannot retrieve config from auth-service")
        return None
    
    try:
        # Create channel to auth-service
        # In docker-compose, hostname is auth-service, port 50051
        channel = grpc.aio.insecure_channel('auth-service:50051')
        stub = auth_pb2_grpc.ConfigurationServiceStub(channel)
        
        # Create request
        request = auth_pb2.GetConfigurationRequest(
            organization_id=organization_id,
            config_key=config_key,
            business_unit_id=business_unit_id or ""
        )
        
        # Call gRPC
        response = await stub.GetConfiguration(request)
        
        # Close channel
        await channel.close()
        
        if response.config_value:
            return response.config_value
        return None
        
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            logger.debug(f"Configuration {config_key} not found for org {organization_id}")
            return None
        logger.warning(f"Failed to get config from auth-service: {e.code()} - {e.details()}")
        return None
    except Exception as e:
        logger.warning(f"Error calling auth-service for config: {e}")
        return None


def get_config_from_auth_service_sync(
    organization_id: str,
    config_key: str,
    business_unit_id: Optional[str] = None
) -> Optional[str]:
    """
    Synchronous wrapper for get_config_from_auth_service
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        get_config_from_auth_service(organization_id, config_key, business_unit_id)
    )
