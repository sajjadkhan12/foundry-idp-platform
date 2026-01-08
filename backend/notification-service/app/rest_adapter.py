"""
REST to gRPC adapter for notification microservice
This provides REST API endpoints for all notification service functionality
"""
import logging
# Configure logging to reduce verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import grpc

from app.config import settings
from app.grpc.notification_servicer import NotificationServicer

# Import generated proto modules
try:
    from proto import notification_pb2, notification_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    notification_pb2 = None
    notification_pb2_grpc = None

app = FastAPI(title="Notification Service REST API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CreateNotificationRequest(BaseModel):
    user_id: str
    title: str
    message: str
    type: Optional[str] = "info"
    link: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    link: Optional[str] = None
    created_at: str


class UpdateNotificationRequest(BaseModel):
    is_read: Optional[bool] = None


# Create servicer instance
notification_servicer = NotificationServicer()


class MockContext:
    """Mock gRPC context for REST adapter"""
    def __init__(self):
        self.code = None
        self.details = None
    
    def set_code(self, code):
        self.code = code
    
    def set_details(self, details):
        self.details = details


async def _get_user_id_from_token(token: Optional[str]) -> Optional[str]:
    """Extract user ID from token by calling auth-service"""
    if not token:
        return None
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://auth-service:8000/api/v1/auth/validate",
                json={"token": token},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("user_id")
    except Exception as e:
        print(f"Error validating token: {e}")
    return None


def _get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract token from Authorization header"""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency to verify token and return user ID.
    Raises HTTPException(401) if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
    user_id = await _get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    return user_id


# ==================== Notification Endpoints ====================

@app.post("/api/v1/notifications", response_model=NotificationResponse, status_code=201)
async def create_notification(
    request: CreateNotificationRequest,
    current_user_id: str = Depends(verify_token)
):
    """Create a notification"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = notification_pb2.CreateNotificationRequest(
        user_id=request.user_id,
        title=request.title,
        message=request.message,
        type=request.type or "info",
        link=request.link or ""
    )
    
    response = await notification_servicer.CreateNotification(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create notification")
    
    return {
        "id": response.id,
        "user_id": response.user_id,
        "title": response.title,
        "message": response.message,
        "type": response.type,
        "is_read": response.is_read,
        "link": response.link if response.link else None,
        "created_at": response.created_at
    }


@app.get("/api/v1/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Get a notification by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = notification_pb2.GetNotificationRequest(notification_id=notification_id)
    
    response = await notification_servicer.GetNotification(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Notification not found")
    
    return {
        "id": response.id,
        "user_id": response.user_id,
        "title": response.title,
        "message": response.message,
        "type": response.type,
        "is_read": response.is_read,
        "link": response.link if response.link else None,
        "created_at": response.created_at
    }


@app.get("/api/v1/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    user_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user_id: str = Depends(verify_token)
):
    """List notifications"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Extract user_id from token if not provided
    # Extract user_id from token if not provided (use authenticated user's ID)
    if not user_id:
        user_id = current_user_id
    
    # If no user_id, return empty list instead of error (graceful degradation)
    if not user_id:
        return []
    
    context = MockContext()
    grpc_request = notification_pb2.ListNotificationsRequest(
        user_id=user_id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    
    response = await notification_servicer.ListNotifications(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list notifications")
    
    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "link": n.link if n.link else None,
            "created_at": n.created_at
        }
        for n in response.notifications
    ]


@app.put("/api/v1/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Mark a notification as read"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = notification_pb2.MarkAsReadRequest(notification_id=notification_id)
    
    response = await notification_servicer.MarkAsRead(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Notification not found")
    
    return {
        "id": response.id,
        "user_id": response.user_id,
        "title": response.title,
        "message": response.message,
        "type": response.type,
        "is_read": response.is_read,
        "link": response.link if response.link else None,
        "created_at": response.created_at
    }


@app.put("/api/v1/notifications/read-all")
async def mark_all_as_read(
    user_id: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """Mark all notifications as read"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user_id from query or from authorization token
    actual_user_id = user_id
    if not actual_user_id:
        token = _get_token_from_header(authorization)
        if token:
            actual_user_id = await _get_user_id_from_token(token)
    
    if not actual_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    context = MockContext()
    grpc_request = notification_pb2.MarkAllAsReadRequest(user_id=actual_user_id)
    
    await notification_servicer.MarkAllAsRead(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to mark all as read")
    
    return {"message": "All notifications marked as read"}


@app.delete("/api/v1/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user_id: str = Depends(verify_token)
):
    """Delete a notification"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = notification_pb2.DeleteNotificationRequest(notification_id=notification_id)
    
    await notification_servicer.DeleteNotification(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Notification not found")
    
    return {"message": "Notification deleted"}


@app.get("/api/v1/notifications/unread/count")
async def get_unread_count(
    user_id: Optional[str] = Query(None),
    current_user_id: str = Depends(verify_token)
):
    """Get unread notification count"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Extract user_id from token if not provided
    actual_user_id = user_id
    if not actual_user_id:
        token = _get_token_from_header(authorization)
        if token:
            actual_user_id = await _get_user_id_from_token(token)
    
    # If no user_id, return 0 count (graceful degradation)
    if not actual_user_id:
        return {"count": 0}
    
    context = MockContext()
    grpc_request = notification_pb2.GetUnreadCountRequest(user_id=actual_user_id)
    
    response = await notification_servicer.GetUnreadCount(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to get unread count")
    
    return {"count": response.count}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notification-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
