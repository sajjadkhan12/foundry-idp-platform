"""Notification service"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.models.notification import Notification, NotificationType


class NotificationService:
    """Service for notification operations"""
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        link: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Create a new notification with deduplication"""
        user_uuid = UUID(user_id)
        
        # Check for duplicate notification within the last 30 seconds
        # This prevents duplicate notifications from rapid API calls
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=30)
        duplicate_check = await db.execute(
            select(Notification).where(
                Notification.user_id == user_uuid,
                Notification.title == title,
                Notification.message == message,
                Notification.created_at >= cutoff_time
            ).order_by(Notification.created_at.desc()).limit(1)
        )
        existing_notification = duplicate_check.scalar_one_or_none()
        
        # If a duplicate exists within the last 30 seconds, return it instead of creating a new one
        if existing_notification:
            return {
                "id": existing_notification.id,
                "user_id": str(existing_notification.user_id),
                "title": existing_notification.title,
                "message": existing_notification.message,
                "type": existing_notification.type,
                "is_read": existing_notification.is_read,
                "link": existing_notification.link,
                "created_at": existing_notification.created_at.isoformat() if existing_notification.created_at else ""
            }
        
        # Create new notification if no duplicate found
        notification = Notification(
            user_id=user_uuid,
            title=title,
            message=message,
            type=notification_type,
            link=link,
            is_read=False
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        return {
            "id": notification.id,
            "user_id": str(notification.user_id),
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "link": notification.link,
            "created_at": notification.created_at.isoformat() if notification.created_at else ""
        }
    
    async def get_notification(
        self,
        notification_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get a notification by ID"""
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise ValueError("Notification not found")
        
        return {
            "id": notification.id,
            "user_id": str(notification.user_id),
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "link": notification.link,
            "created_at": notification.created_at.isoformat() if notification.created_at else ""
        }
    
    async def list_notifications(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """List notifications for a user"""
        # Validate UUID format
        try:
            user_uuid = UUID(user_id)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid user_id format: {user_id}. Expected UUID format.")
        
        query = select(Notification).where(Notification.user_id == user_uuid)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        # Get total count
        count_query = select(func.count()).select_from(Notification).where(Notification.user_id == user_uuid)
        if unread_only:
            count_query = count_query.where(Notification.is_read == False)
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Get paginated results
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        return {
            "notifications": [
                {
                    "id": n.id,
                    "user_id": str(n.user_id),
                    "title": n.title,
                    "message": n.message,
                    "type": n.type,
                    "is_read": n.is_read,
                    "link": n.link,
                    "created_at": n.created_at.isoformat() if n.created_at else ""
                }
                for n in notifications
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    async def update_notification(
        self,
        notification_id: str,
        is_read: Optional[bool] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Update a notification"""
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise ValueError("Notification not found")
        
        if is_read is not None:
            notification.is_read = is_read
        
        await db.commit()
        await db.refresh(notification)
        
        return {
            "id": notification.id,
            "user_id": str(notification.user_id),
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "link": notification.link,
            "created_at": notification.created_at.isoformat() if notification.created_at else ""
        }
    
    async def delete_notification(
        self,
        notification_id: str,
        db: AsyncSession
    ):
        """Delete a notification"""
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise ValueError("Notification not found")
        
        await db.delete(notification)
        await db.commit()
    
    async def mark_as_read(
        self,
        notification_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Mark a notification as read"""
        return await self.update_notification(notification_id, is_read=True, db=db)
    
    async def mark_all_as_read(
        self,
        user_id: str,
        db: AsyncSession
    ):
        """Mark all notifications as read for a user"""
        await db.execute(
            update(Notification)
            .where(Notification.user_id == UUID(user_id), Notification.is_read == False)
            .values(is_read=True)
        )
        await db.commit()
    
    async def get_unread_count(
        self,
        user_id: str,
        db: AsyncSession
    ) -> int:
        """Get unread notification count for a user"""
        result = await db.execute(
            select(func.count()).select_from(Notification).where(
                Notification.user_id == UUID(user_id),
                Notification.is_read == False
            )
        )
        return result.scalar_one() or 0


notification_service = NotificationService()
