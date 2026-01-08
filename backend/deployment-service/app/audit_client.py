"""
Audit Client for Deployment Service
Logs activities to the centralized audit service.
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
        self.service_name = "deployment-service"
        
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
        status: str = "success",
        error_message: Optional[str] = None,
        business_unit_id: Optional[str] = None
    ) -> bool:
        """Log an activity to the audit service"""
        try:
            payload = {
                "action": action,
                "status": status,
                "service_name": self.service_name,
            }
            
            if user_id:
                payload["user_id"] = str(user_id)
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
            if error_message:
                payload["error_message"] = error_message
            if business_unit_id:
                payload["business_unit_id"] = str(business_unit_id)
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/audit-logs",
                    json=payload
                )
                
                if response.status_code == 201:
                    logger.debug(f"Audit log created: {action}")
                    return True
                else:
                    logger.warning(f"Failed to create audit log: {response.status_code}")
                    return False
                    
        except Exception as e:
            # Don't fail the main operation if audit logging fails
            logger.warning(f"Error logging to audit service: {e}")
            return False

# Global client instance
audit_client = AuditClient()
