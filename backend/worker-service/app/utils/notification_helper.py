"""Helper function for creating notifications via gRPC"""
import grpc
import os
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "notification-service:50052")

try:
    # Try to import notification proto files
    import sys
    from pathlib import Path
    # Add proto directory to path
    proto_path = Path(__file__).parent.parent.parent / "proto"
    if proto_path.exists():
        sys.path.insert(0, str(proto_path.parent))
    
    from proto.notification import notification_pb2, notification_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    notification_pb2 = None
    notification_pb2_grpc = None
    logger.warning("Notification proto files not available. Notifications will be logged only.")


def create_notification_sync(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
    link: Optional[str] = None
) -> Optional[dict]:
    """
    Create a notification via notification microservice gRPC (synchronous wrapper).
    Returns the created notification dict or None if creation failed.
    """
    if not PROTO_AVAILABLE:
        logger.warning(f"Notification proto not available. Would create notification: {title} - {message}")
        return None
    
    try:
        # Run async function in sync context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_create_notification_async, user_id, title, message, notification_type, link)
                return future.result(timeout=5)
        else:
            return loop.run_until_complete(_create_notification_async(user_id, title, message, notification_type, link))
    except Exception as e:
        logger.error(f"Failed to create notification via gRPC: {e}", exc_info=True)
        return None


async def _create_notification_async(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
    link: Optional[str] = None
) -> Optional[dict]:
    """Async helper to create notification"""
    if not PROTO_AVAILABLE:
        return None
    
    try:
        channel = grpc.aio.insecure_channel(NOTIFICATION_SERVICE_URL)
        stub = notification_pb2_grpc.NotificationServiceStub(channel)
        
        request = notification_pb2.CreateNotificationRequest(
            user_id=str(user_id),
            title=title,
            message=message,
            type=notification_type,
            link=link or ""
        )
        
        response = await stub.CreateNotification(request)
        await channel.close()
        
        return {
            "id": response.id,
            "user_id": response.user_id,
            "title": response.title,
            "message": response.message,
            "type": response.type,
            "is_read": response.is_read,
            "link": response.link,
            "created_at": response.created_at
        }
    except grpc.RpcError as e:
        logger.error(f"gRPC error creating notification: {e.details()}")
        return None
    except Exception as e:
        logger.error(f"Failed to create notification via gRPC: {e}", exc_info=True)
        return None
