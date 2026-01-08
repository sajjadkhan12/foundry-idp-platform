"""Notification gRPC servicer"""
import grpc
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notification_service import notification_service

try:
    from proto import notification_pb2, notification_pb2_grpc
except ImportError:
    # Fallback for development
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from proto import notification_pb2, notification_pb2_grpc


class NotificationServicer(notification_pb2_grpc.NotificationServiceServicer):
    """gRPC servicer for notification operations"""
    
    async def CreateNotification(self, request, context):
        """Create a notification"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                notification = await notification_service.create_notification(
                    request.user_id,
                    request.title,
                    request.message,
                    request.type,
                    request.link if request.link else None,
                    db
                )
                return notification_pb2.NotificationResponse(
                    id=notification["id"],
                    user_id=notification["user_id"],
                    title=notification["title"],
                    message=notification["message"],
                    type=notification["type"],
                    is_read=notification["is_read"],
                    link=notification.get("link", ""),
                    created_at=notification.get("created_at", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return notification_pb2.NotificationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.NotificationResponse()
    
    async def GetNotification(self, request, context):
        """Get a notification by ID"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                notification = await notification_service.get_notification(request.notification_id, db)
                return notification_pb2.NotificationResponse(
                    id=notification["id"],
                    user_id=notification["user_id"],
                    title=notification["title"],
                    message=notification["message"],
                    type=notification["type"],
                    is_read=notification["is_read"],
                    link=notification.get("link", ""),
                    created_at=notification.get("created_at", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return notification_pb2.NotificationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.NotificationResponse()
    
    async def ListNotifications(self, request, context):
        """List notifications"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await notification_service.list_notifications(
                    request.user_id,
                    request.skip,
                    request.limit,
                    request.unread_only,
                    db
                )
                return notification_pb2.ListNotificationsResponse(
                    notifications=[
                        notification_pb2.NotificationResponse(
                            id=n["id"],
                            user_id=n["user_id"],
                            title=n["title"],
                            message=n["message"],
                            type=n["type"],
                            is_read=n["is_read"],
                            link=n.get("link", ""),
                            created_at=n.get("created_at", "")
                        )
                        for n in result["notifications"]
                    ],
                    total=result["total"],
                    skip=result["skip"],
                    limit=result["limit"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return notification_pb2.ListNotificationsResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.ListNotificationsResponse()
    
    async def UpdateNotification(self, request, context):
        """Update a notification"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                notification = await notification_service.update_notification(
                    request.notification_id,
                    request.is_read if request.HasField("is_read") else None,
                    db
                )
                return notification_pb2.NotificationResponse(
                    id=notification["id"],
                    user_id=notification["user_id"],
                    title=notification["title"],
                    message=notification["message"],
                    type=notification["type"],
                    is_read=notification["is_read"],
                    link=notification.get("link", ""),
                    created_at=notification.get("created_at", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return notification_pb2.NotificationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.NotificationResponse()
    
    async def DeleteNotification(self, request, context):
        """Delete a notification"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await notification_service.delete_notification(request.notification_id, db)
                return notification_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return notification_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.Empty()
    
    async def MarkAsRead(self, request, context):
        """Mark a notification as read"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                notification = await notification_service.mark_as_read(request.notification_id, db)
                return notification_pb2.NotificationResponse(
                    id=notification["id"],
                    user_id=notification["user_id"],
                    title=notification["title"],
                    message=notification["message"],
                    type=notification["type"],
                    is_read=notification["is_read"],
                    link=notification.get("link", ""),
                    created_at=notification.get("created_at", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return notification_pb2.NotificationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.NotificationResponse()
    
    async def MarkAllAsRead(self, request, context):
        """Mark all notifications as read"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await notification_service.mark_all_as_read(request.user_id, db)
                return notification_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.Empty()
    
    async def GetUnreadCount(self, request, context):
        """Get unread notification count"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                count = await notification_service.get_unread_count(request.user_id, db)
                return notification_pb2.UnreadCountResponse(count=count)
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return notification_pb2.UnreadCountResponse(count=0)
