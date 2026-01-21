"""Worker service for executing provisioning tasks"""
import json
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database import get_sync_db_session
from app.config import settings
from app.workers import celery_app
from app.services.github_actions_service import github_actions_service
from app.models.deployment import Deployment
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WorkerService:
    """Service for executing worker tasks via Celery"""
    
    async def provision_infrastructure(
        self,
        job_id: str,
        plugin_id: str,
        version: str,
        inputs: Dict[str, Any],
        credential_name: Optional[str],
        deployment_id: Optional[str]
    ) -> Dict[str, Any]:
        """Execute infrastructure provisioning task via Celery"""
        try:
            # Queue task to Celery
            from app.workers import provision_infrastructure as provision_task
            task = provision_task.delay(
                job_id=job_id,
                plugin_id=plugin_id,
                version=version,
                inputs=inputs,
                credential_name=credential_name,
                deployment_id=deployment_id
            )
            
            logger.info(f"Queued infrastructure provisioning task {task.id} for job {job_id}")
            
            return {
                "success": True,
                "message": "Task queued successfully",
                "task_id": task.id,
                "error": ""
            }
        except Exception as e:
            logger.error(f"Failed to queue infrastructure provisioning: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to queue task",
                "task_id": "",
                "error": str(e)
            }
    
    async def destroy_infrastructure(self, deployment_id: str, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute infrastructure destruction task via Celery"""
        try:
            from app.workers import destroy_infrastructure as destroy_task
            task = destroy_task.delay(deployment_id=deployment_id, job_id=job_id)
            
            logger.info(f"Queued infrastructure destruction task {task.id} for deployment {deployment_id}")
            
            return {
                "success": True,
                "message": "Task queued successfully",
                "task_id": task.id,
                "error": ""
            }
        except Exception as e:
            logger.error(f"Failed to queue infrastructure destruction: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to queue task",
                "task_id": "",
                "error": str(e)
            }
    
    async def provision_microservice(
        self,
        job_id: str,
        plugin_id: str,
        version: str,
        deployment_name: str,
        user_id: str,
        deployment_id: Optional[str],
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute microservice provisioning task via Celery"""
        try:
            from app.workers import provision_microservice as provision_task
            task = provision_task.delay(
                job_id=job_id,
                plugin_id=plugin_id,
                version=version,
                deployment_name=deployment_name,
                user_id=user_id,
                deployment_id=deployment_id,
                inputs=inputs
            )
            
            logger.info(f"Queued microservice provisioning task {task.id} for job {job_id}")
            
            return {
                "success": True,
                "message": "Task queued successfully",
                "task_id": task.id,
                "error": ""
            }
        except Exception as e:
            logger.error(f"Failed to queue microservice provisioning: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to queue task",
                "task_id": "",
                "error": str(e)
            }
    
    async def destroy_microservice(self, deployment_id: str, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute microservice destruction task via Celery"""
        try:
            from app.workers import destroy_microservice as destroy_task
            task = destroy_task.delay(deployment_id=deployment_id, job_id=job_id)
            
            logger.info(f"Queued microservice destruction task {task.id} for deployment {deployment_id}")
            
            return {
                "success": True,
                "message": "Task queued successfully",
                "task_id": task.id,
                "error": ""
            }
        except Exception as e:
            logger.error(f"Failed to queue microservice destruction: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to queue task",
                "task_id": "",
                "error": str(e)
            }
    
    async def cleanup_stuck_deployments(self) -> Dict[str, Any]:
        """Execute cleanup stuck deployments task via Celery"""
        try:
            from app.workers import cleanup_stuck_deployments as cleanup_task
            task = cleanup_task.delay()
            
            logger.info(f"Queued cleanup stuck deployments task {task.id}")
            
            return {
                "success": True,
                "message": "Task queued successfully",
                "task_id": task.id,
                "error": ""
            }
        except Exception as e:
            logger.error(f"Failed to queue cleanup stuck deployments: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to queue task",
                "task_id": "",
                "error": str(e)
            }
    
    async def cleanup_expired_refresh_tokens(self) -> Dict[str, Any]:
        """Execute cleanup expired refresh tokens task via Celery"""
        try:
            from app.workers import cleanup_expired_refresh_tokens as cleanup_task
            task = cleanup_task.delay()
            
            logger.info(f"Queued cleanup expired refresh tokens task {task.id}")
            
            return {
                "success": True,
                "message": "Task queued successfully",
                "task_id": task.id,
                "error": ""
            }
        except Exception as e:
            logger.error(f"Failed to queue cleanup expired refresh tokens: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to queue task",
                "task_id": "",
                "error": str(e)
            }
    
    async def poll_github_actions_status(self) -> Dict[str, Any]:
        """Execute poll GitHub Actions status task via Celery"""
        try:
            from app.workers import poll_github_actions_status as poll_task
            task = poll_task.delay()
            
            logger.info(f"Queued poll GitHub Actions status task {task.id}")
            
            return {
                "success": True,
                "message": "Task queued successfully",
                "task_id": task.id,
                "error": ""
            }
        except Exception as e:
            logger.error(f"Failed to queue poll GitHub Actions status: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to queue task",
                "task_id": "",
                "error": str(e)
            }
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get Celery task status"""
        try:
            from celery.result import AsyncResult
            task_result = AsyncResult(task_id, app=celery_app)
            
            if task_result.state == 'PENDING':
                return {
                    "status": "pending",
                    "message": "Task is pending",
                    "error": "",
                    "outputs": ""
                }
            elif task_result.state == 'PROGRESS':
                return {
                    "status": "running",
                    "message": "Task is running",
                    "error": "",
                    "outputs": task_result.info.get("outputs", "") if isinstance(task_result.info, dict) else ""
                }
            elif task_result.state == 'SUCCESS':
                return {
                    "status": "success",
                    "message": "Task completed successfully",
                    "error": "",
                    "outputs": task_result.result if task_result.result else ""
                }
            elif task_result.state == 'FAILURE':
                return {
                    "status": "failed",
                    "message": "Task failed",
                    "error": str(task_result.info) if task_result.info else "Unknown error",
                    "outputs": ""
                }
            else:
                return {
                    "status": task_result.state.lower(),
                    "message": f"Task is in {task_result.state} state",
                    "error": "",
                    "outputs": ""
                }
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}", exc_info=True)
            return {
                "status": "error",
                "message": "Failed to get task status",
                "error": str(e),
                "outputs": ""
            }
    
    async def process_github_webhook(
        self,
        event_type: str,
        payload_json: str,
        signature: Optional[str],
        payload_body: bytes
    ) -> Dict[str, Any]:
        """
        Process GitHub webhook event and update deployment CI/CD status.
        
        Args:
            event_type: GitHub webhook event type (e.g., "workflow_run")
            payload_json: JSON string of webhook payload
            signature: X-Hub-Signature-256 header value
            payload_body: Raw payload body for signature verification
            
        Returns:
            Dictionary with success, message, deployment_updated, and deployment_id
        """
        try:
            # Verify webhook signature if provided
            if signature:
                if not github_actions_service.verify_webhook_signature(payload_body, signature):
                    logger.warning("Invalid webhook signature")
                    return {
                        "success": False,
                        "message": "Invalid webhook signature",
                        "deployment_updated": False,
                        "deployment_id": ""
                    }
            
            # Parse payload
            try:
                payload = json.loads(payload_json)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "message": "Invalid JSON payload",
                    "deployment_updated": False,
                    "deployment_id": ""
                }
            
            # Only process workflow_run events
            if event_type != "workflow_run":
                return {
                    "success": True,
                    "message": "Event type not processed",
                    "deployment_updated": False,
                    "deployment_id": ""
                }
            
            # Parse webhook event
            webhook_data = github_actions_service.parse_webhook_event(event_type, payload)
            
            if not webhook_data:
                logger.warning(f"Could not parse webhook event: {event_type}")
                return {
                    "success": True,
                    "message": "Event not parsed",
                    "deployment_updated": False,
                    "deployment_id": ""
                }
            
            # Get repository full name
            repo_full_name = webhook_data.get("repository")
            if not repo_full_name:
                logger.warning("No repository information in webhook payload")
                return {
                    "success": True,
                    "message": "No repository info",
                    "deployment_updated": False,
                    "deployment_id": ""
                }
            
            # Find deployment by repository name (using sync DB session)
            db = get_sync_db_session()
            try:
                deployment = db.execute(
                    select(Deployment).where(
                        Deployment.github_repo_name == repo_full_name,
                        Deployment.deployment_type == "microservice"
                    )
                ).scalar_one_or_none()
                
                if not deployment:
                    logger.info(f"No deployment found for repository: {repo_full_name}")
                    return {
                        "success": True,
                        "message": "Deployment not found",
                        "deployment_updated": False,
                        "deployment_id": ""
                    }
                
                # Convert webhook data to CI/CD status
                ci_cd_status_data = github_actions_service.get_workflow_status_from_webhook(webhook_data)
                
                # Update deployment
                deployment.ci_cd_status = ci_cd_status_data.get("ci_cd_status")
                deployment.ci_cd_run_id = ci_cd_status_data.get("ci_cd_run_id")
                deployment.ci_cd_run_url = ci_cd_status_data.get("ci_cd_run_url")
                deployment.ci_cd_updated_at = datetime.now(timezone.utc)
                
                db.add(deployment)
                db.commit()
                
                logger.info(
                    f"Updated CI/CD status for deployment {deployment.id}: "
                    f"{deployment.ci_cd_status} (run_id: {deployment.ci_cd_run_id})"
                )
                
                return {
                    "success": True,
                    "message": "Webhook processed successfully",
                    "deployment_updated": True,
                    "deployment_id": str(deployment.id)
                }
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing GitHub webhook: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "deployment_updated": False,
                "deployment_id": ""
            }


# Singleton instance
worker_service = WorkerService()
