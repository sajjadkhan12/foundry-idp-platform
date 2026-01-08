"""
Audit Client Library
Use this to log activities from other microservices to the audit service.

Usage:
    from audit_client import audit_client
    
    # Log an activity
    await audit_client.log_activity(
        user_id="user-uuid",
        user_email="user@example.com",
        action="deployment.create",
        resource_type="deployment",
        resource_id="deployment-uuid",
        resource_name="my-deployment",
        details={"key": "value"},
        ip_address="192.168.1.1",
        status="success",
        service_name="deployment-service"
    )
"""
import httpx
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://audit-service:8000")

class AuditClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or AUDIT_SERVICE_URL
        
    async def log_activity(
        self,
        action: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        business_unit_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        service_name: Optional[str] = None,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> bool:
        """Log an activity to the audit service"""
        try:
            payload = {
                "action": action,
                "status": status,
            }
            
            # Add optional fields if provided
            if user_id:
                payload["user_id"] = user_id
            if user_email:
                payload["user_email"] = user_email
            if user_name:
                payload["user_name"] = user_name
            if resource_type:
                payload["resource_type"] = resource_type
            if resource_id:
                payload["resource_id"] = str(resource_id)
            if resource_name:
                payload["resource_name"] = resource_name
            if details:
                payload["details"] = details
            if ip_address:
                payload["ip_address"] = ip_address
            if user_agent:
                payload["user_agent"] = user_agent
            if error_message:
                payload["error_message"] = error_message
            if business_unit_id:
                payload["business_unit_id"] = business_unit_id
            if organization_id:
                payload["organization_id"] = organization_id
            if service_name:
                payload["service_name"] = service_name
            if correlation_id:
                payload["correlation_id"] = correlation_id
            if duration_ms is not None:
                payload["duration_ms"] = duration_ms
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/audit-logs",
                    json=payload
                )
                
                if response.status_code == 201:
                    logger.debug(f"Audit log created: {action}")
                    return True
                else:
                    logger.warning(f"Failed to create audit log: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            # Don't fail the main operation if audit logging fails
            logger.error(f"Error logging to audit service: {e}")
            return False
    
    def log_activity_sync(
        self,
        action: str,
        **kwargs
    ) -> bool:
        """Synchronous version of log_activity for non-async contexts"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, create a task
                asyncio.create_task(self.log_activity(action, **kwargs))
                return True
            else:
                return loop.run_until_complete(self.log_activity(action, **kwargs))
        except Exception as e:
            logger.error(f"Error in sync audit log: {e}")
            return False

# Global client instance
audit_client = AuditClient()
