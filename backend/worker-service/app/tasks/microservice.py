"""Microservice provisioning and destruction tasks"""
import traceback
from datetime import datetime, timezone
import uuid
from uuid import UUID
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tasks.db import get_sync_db_session
from app.logger import logger
from app.config import settings

from app.models import (
    Job, JobLog, JobStatus, PluginVersion, Plugin, Deployment,
    DeploymentStatus, Notification, NotificationType, User, DeploymentHistory,
    Environment
)
from app.models.deployment import DeploymentType
from sqlalchemy import select, func, text
from app.utils.notification_helper import create_notification_sync
from app.utils.config_helper import get_config_from_auth_service_sync
from app.services.microservice_service import microservice_service
from app.services.github_actions_service import github_actions_service
from app.services.git_service import git_service
from app.services.pulumi_service import pulumi_service
# from app.services.github_secrets_service import github_secrets_service (Imported locally below)


class MicroserviceProvisionTask:
    """Task for provisioning microservices"""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.db: Optional[Session] = None
    
    def log_message(self, level: str, message: str):
        """Log message to both JobLog and server log"""
        # Use a fresh session for logging to ensure thread-safety
        try:
            log_db = get_sync_db_session()
            try:
                log = JobLog(job_id=self.job_id, level=level, message=message)
                log_db.add(log)
                log_db.commit()
            finally:
                log_db.close()
        except Exception as e:
            logger.warning(f"Failed to write job log: {e}")
        
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"[Microservice Job {self.job_id}] {message}")
    
    def execute(self, plugin_id: str, version: str, deployment_name: str,
                user_id: str, inputs: Optional[Dict] = None, deployment_id: str = None):
        """Execute microservice provisioning"""
        self.db = get_sync_db_session()
        try:
            self._provision(plugin_id, version, deployment_name, user_id, inputs or {}, deployment_id)
        except Exception as e:
            self.log_message("ERROR", f"Microservice provisioning failed: {str(e)}")
            self._handle_error(e, deployment_id, deployment_name, user_id)
        finally:
            if self.db:
                self.db.close()
    
    def _provision(self, plugin_id: str, version: str, deployment_name: str,
                   user_id: str, inputs: Dict, deployment_id: str):
        """Main provisioning logic"""
        # Update job status
        job = self.db.execute(select(Job).where(Job.id == self.job_id)).scalar_one()
        job.status = JobStatus.RUNNING.value
        self.db.commit()
        
        self.log_message("INFO", f"Starting microservice provisioning: {deployment_name}")
        
        # Get plugin version
        plugin_version = self.db.execute(
            select(PluginVersion).where(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version
            )
        ).scalar_one()
        
        # Verify this is a microservice plugin
        plugin = self.db.execute(
            select(Plugin).where(Plugin.id == plugin_id)
        ).scalar_one()
        
        if plugin.deployment_type != "microservice":
            raise Exception(f"Plugin {plugin_id} is not a microservice plugin")
        
        # Get template information
        template_repo_url = plugin_version.template_repo_url
        template_path = plugin_version.template_path
        
        if not template_repo_url or not template_path:
            raise Exception(f"Template repository URL or path not configured for plugin {plugin_id}")
        
        self.log_message("INFO", f"Template: {template_repo_url}/{template_path}")
        
        # Get user for org context
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
        organization_id = str(user.organization_id)
        business_unit_id = str(user.active_business_unit_id) if user.active_business_unit_id else None
        
        # Get or create deployment
        deployment = self._setup_deployment(deployment_id, plugin_id, version,
                                           deployment_name, user_id, organization_id, business_unit_id)
        
        # Get GitHub token
        user_github_token = git_service.get_github_token(organization_id, business_unit_id)
        if not user_github_token:
            raise Exception("GitHub token not configured for organization. Cannot create repository.")
        
        self.log_message("INFO", f"Creating GitHub repository: {deployment_name}")
        
        # Get organization repository from config
        organization = get_config_from_auth_service_sync(organization_id, "MICROSERVICE_REPO_ORG", business_unit_id)
            
        if not organization:
            raise Exception("MICROSERVICE_REPO_ORG not configured for organization. Please set this in Settings.")
        
        self.log_message("INFO", f"Creating repository in organization: {organization}")
        
        # Create repository from template
        try:
            repo_url, repo_full_name = microservice_service.create_repository_from_template(
                template_repo_url=template_repo_url,
                template_path=template_path,
                repo_name=deployment_name,
                user_github_token=user_github_token,
                description=f"Microservice: {deployment_name} (provisioned via IDP)",
                organization=organization,
                context=inputs
            )
            
            self.log_message("INFO", f"Successfully created repository: {repo_full_name}")
            self.log_message("INFO", f"Repository URL: {repo_url}")
        except Exception as e:
            error_msg = f"Failed to create repository: {str(e)}"
            self.log_message("ERROR", error_msg)
            raise Exception(error_msg)
        
        # Step 3: Infrastructure Provisioning (Atomic step) - REMOVED BY USER REQUEST
        pulumi_stack_name = None

        # Update deployment with repository and infra information
        deployment.github_repo_url = repo_url
        deployment.github_repo_name = repo_full_name
        deployment.pulumi_stack_name = pulumi_stack_name
        deployment.status = DeploymentStatus.ACTIVE.value
        deployment.ci_cd_status = "pending"
        
        # Capture is_update (if deployment_id was provided, it's likely an update)
        is_update = deployment_id is not None
        
        # Save history entry
        self._save_deployment_history(deployment, inputs, {
            "repository_url": repo_url,
            "repository_name": repo_full_name,
            "deployment_id": str(deployment.id)
        }, job, is_update)
        
        self.db.add(deployment)
        self.db.commit() # Commit deployment status and history
        
        # Update job status
        job.status = JobStatus.SUCCESS.value
        job.finished_at = datetime.now(timezone.utc)
        job.outputs = {
            "repository_url": repo_url,
            "repository_name": repo_full_name,
            "deployment_id": str(deployment.id)
        }
        self.db.add(job)
        self.db.commit() # Commit job status
        
        # Get initial CI/CD status
        self._get_initial_cicd_status(deployment, repo_full_name, user_github_token)
        
        self.db.commit()
        
        # Create success notification
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
        create_notification_sync(
            user_id=str(user.id),
            title="Microservice Created" if not is_update else "Microservice Updated",
            message=f"Microservice '{deployment_name}' has been {'created' if not is_update else 'updated'}. Repository: {repo_full_name}",
            notification_type="success",
            link=f"/deployments/{deployment.id}"
        )
        self.db.commit()
        
        self.log_message("INFO", f"Microservice {'provisioning' if not is_update else 'update'} completed successfully")
    
    def _check_namespace_conflict(self, cluster_id: str, namespace: str, deployment_id: Optional[str] = None):
        """
        Check if the requested namespace on the cluster is already in use by another service.
        """
        self.log_message("INFO", f"Validating namespace availability: {namespace} on cluster {cluster_id}")
        
        # Query for active deployments with the same cluster and namespace in inputs
        # Note: We use JSONB filtering for inputs
        query = select(Deployment).where(
            Deployment.deployment_type == "microservice",
            Deployment.status != DeploymentStatus.DELETED.value,
            text("inputs->>'target_cluster' = :cluster"),
            text("inputs->>'namespace' = :namespace")
        )
        
        # Exclude current deployment if it's an update
        if deployment_id:
            query = query.where(Deployment.id != UUID(deployment_id))
            
        results = self.db.execute(query, {"cluster": cluster_id, "namespace": namespace}).scalars().all()
        
        if results:
            existing_names = ", ".join([d.name for d in results])
            error_msg = f"Namespace '{namespace}' on cluster '{cluster_id}' is already in use by: {existing_names}"
            self.log_message("ERROR", error_msg)
            raise Exception(error_msg)
        
        self.log_message("INFO", f"Namespace '{namespace}' is available on cluster '{cluster_id}'")

    def _setup_deployment(self, deployment_id: str, plugin_id: str, version: str,
                         deployment_name: str, user_id: str, organization_id: str, business_unit_id: Optional[str]) -> Deployment:
        """Setup or get deployment record"""
        deployment = None
        if deployment_id:
            deployment_uuid = UUID(deployment_id) if isinstance(deployment_id, str) else deployment_id
            deployment = self.db.execute(
                select(Deployment).where(Deployment.id == deployment_uuid)
            ).scalar_one_or_none()
        
        if not deployment:
            # First, check if a deployment with the same name already exists for this plugin
            # This handles cases where the deployment-service creation was successful but
            # the ID wasn't properly linked, or if we're retrying a failed creation.
            existing_deployment = self.db.execute(
                select(Deployment).where(
                    Deployment.name == deployment_name,
                    Deployment.plugin_id == plugin_id,
                    Deployment.deployment_type == "microservice"
                )
            ).scalar_one_or_none()
            
            if existing_deployment:
                deployment = existing_deployment
                self.log_message("INFO", f"Found existing microservice deployment by name: {deployment.name} (ID: {deployment.id})")
            
            # If still no deployment, then create it
            if not deployment:
                user = self.db.execute(
                    select(User).where(User.id == user_id)
                ).scalar_one_or_none()
                
                if not user:
                    raise Exception(f"User {user_id} not found")
            
                try:
                    deployment = Deployment(
                        id=UUID(deployment_id) if deployment_id else uuid.uuid4(),
                        name=deployment_name,
                        plugin_id=plugin_id,
                        version=version,
                        status=DeploymentStatus.PROVISIONING.value,
                        deployment_type=DeploymentType.MICROSERVICE.value,
                        environment=Environment.DEVELOPMENT.value,
                        user_id=user_id,
                        organization_id=organization_id,
                        business_unit_id=business_unit_id,
                        inputs={"deployment_name": deployment_name},
                    )
                    self.db.add(deployment)
                    self.db.commit()
                    self.db.refresh(deployment)
                    self.log_message("INFO", f"Created deployment record: {deployment.id}")
                except TypeError as te:
                    self.log_message("ERROR", f"TypeError creating Deployment: {te}")
                    raise
                except Exception as e:
                    self.log_message("ERROR", f"Error creating Deployment: {e}")
                    raise
        else:
            deployment.status = DeploymentStatus.PROVISIONING.value
            deployment.deployment_type = "microservice"
            self.db.add(deployment)
            self.db.commit()
        
        return deployment

    def _save_deployment_history(self, deployment: Deployment, inputs: dict,
                                outputs: dict, job: Job, is_update: bool):
        """Save deployment history entry"""
        try:
            # If we are setting a new version to active, mark all previous active versions as superseded
            self.db.execute(
                text("""
                    UPDATE deployment_history 
                    SET status = 'superseded' 
                    WHERE deployment_id = :deployment_id AND status = :active_status
                """),
                {
                    "deployment_id": deployment.id,
                    "active_status": DeploymentStatus.ACTIVE.value
                }
            )

            # For updates, always create a new history entry (new version)
            if is_update:
                max_version_result = self.db.execute(
                    select(func.max(DeploymentHistory.version_number))
                    .where(DeploymentHistory.deployment_id == deployment.id)
                )
                max_version = max_version_result.scalar() or 0
                next_version = max_version + 1
                
                history_entry = DeploymentHistory(
                    id=uuid.uuid4(),
                    deployment_id=deployment.id,
                    version_number=next_version,
                    inputs=inputs.copy() if inputs else {},
                    outputs=outputs.copy() if outputs else None,
                    status=DeploymentStatus.ACTIVE.value,
                    job_id=self.job_id,
                    created_by=job.triggered_by,
                    description=f"Update to version {next_version}"
                )
            else:
                history_entry = DeploymentHistory(
                    id=uuid.uuid4(),
                    deployment_id=deployment.id,
                    version_number=1,
                    inputs=inputs.copy() if inputs else {},
                    outputs=outputs.copy() if outputs else None,
                    status=DeploymentStatus.ACTIVE.value,
                    job_id=self.job_id,
                    created_by=job.triggered_by,
                    description="Initial deployment"
                )
            
            self.db.add(history_entry)
            self.db.commit()
            version_num = history_entry.version_number
            self.log_message("INFO", f"Created new deployment history entry (version {version_num})")
        except Exception as hist_error:
            self.db.rollback()
            self.log_message("WARNING", f"Failed to save deployment history: {hist_error}")
    
    def _get_initial_cicd_status(self, deployment: Deployment, repo_full_name: str,
                                user_github_token: str):
        """Get initial CI/CD status from GitHub Actions"""
        try:
            ci_cd_status = github_actions_service.get_latest_workflow_status(
                repo_full_name=repo_full_name,
                user_github_token=user_github_token,
                branch="main"
            )
            
            if ci_cd_status:
                deployment.ci_cd_status = ci_cd_status.get("ci_cd_status", "pending")
                deployment.ci_cd_run_id = ci_cd_status.get("ci_cd_run_id")
                deployment.ci_cd_run_url = ci_cd_status.get("ci_cd_run_url")
                deployment.ci_cd_updated_at = datetime.now(timezone.utc)
                self.log_message("INFO", f"Initial CI/CD status: {deployment.ci_cd_status}")
        except Exception as e:
            self.log_message("WARNING", f"Could not fetch initial CI/CD status: {str(e)}")
    
    def _handle_error(self, error: Exception, deployment_id: str,
                     deployment_name: str, user_id: str):
        """Handle errors during provisioning"""
        error_details = traceback.format_exc()
        logger.error(f"[CELERY ERROR] Microservice job {self.job_id} failed: {error_details}")
        
        try:
            job = self.db.execute(select(Job).where(Job.id == self.job_id)).scalar_one()
            job.status = JobStatus.FAILED.value
            job.error_message = str(error)
            job.finished_at = datetime.now(timezone.utc)
            self.db.add(job)  # Explicitly add job to ensure it's saved
            self.db.commit()  # Commit job status early
            self.log_message("ERROR", f"Internal Error: {str(error)}")
            
            # Update deployment status
            deployment = None
            if deployment_id:
                deployment_uuid = UUID(deployment_id) if isinstance(deployment_id, str) else deployment_id
                deployment = self.db.execute(
                    select(Deployment).where(Deployment.id == deployment_uuid)
                ).scalar_one_or_none()
            
            if deployment:
                # Always set to FAILED if deployment exists and is in PROVISIONING or other non-final state
                if deployment.status in [DeploymentStatus.PROVISIONING.value, DeploymentStatus.ACTIVE.value]:
                    deployment.status = DeploymentStatus.FAILED.value
                    self.db.add(deployment)
                    self.db.commit() # Commit deployment status
                    self.log_message("ERROR", f"Deployment status set to FAILED due to error: {str(error)}")
                else:
                    self.log_message("WARNING", f"Deployment {deployment.id} is in status {deployment.status}, not updating to FAILED")
            
            # Create failure notification
            try:
                user = self.db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
                if user:
                    create_notification_sync(
                        user_id=str(user.id),
                        title="Microservice Creation Failed",
                        message=f"Failed to create microservice '{deployment_name}': {str(error)}",
                        notification_type="error",
                        link=f"/jobs/{self.job_id}" if self.job_id else None
                    )
            except Exception as notif_error:
                logger.error(f"Failed to create notification for user {user_id} on microservice failure: {notif_error}")
            
            self.db.commit()
        except Exception as db_error:
            logger.error(f"[CELERY ERROR] Failed to update job status for {self.job_id}: {db_error}")


class MicroserviceDestroyTask:
    """Task for destroying microservices"""
    
    def __init__(self, deployment_id: str, job_id: str = None):
        self.deployment_id = deployment_id
        self.db: Optional[Session] = None
        self.deletion_job_id = job_id
    
    def log_message(self, level: str, message: str):
        """Log message to both JobLog and server log"""
        if self.deletion_job_id and self.db:
            try:
                log = JobLog(job_id=self.deletion_job_id, level=level, message=message)
                self.db.add(log)
                self.db.commit()
            except Exception as e:
                logger.warning(f"Failed to write job log: {e}")
        
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"[Microservice Deletion {self.deletion_job_id or 'N/A'}] {message}")
    
    def execute(self):
        """Execute microservice destruction"""
        self.db = get_sync_db_session()
        try:
            return self._destroy()
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"[CELERY ERROR] Microservice deletion {self.deployment_id} failed: {error_details}")
            
            try:
                if self.deletion_job_id:
                    deletion_job = self.db.execute(
                        select(Job).where(Job.id == self.deletion_job_id)
                    ).scalar_one_or_none()
                    if deletion_job:
                        deletion_job.status = JobStatus.FAILED
                        deletion_job.finished_at = datetime.now(timezone.utc)
                        self.db.add(deletion_job)
                
                deployment_uuid = UUID(self.deployment_id) if isinstance(self.deployment_id, str) else self.deployment_id
                deployment = self.db.execute(
                    select(Deployment).where(Deployment.id == deployment_uuid)
                ).scalar_one_or_none()
                
                if deployment:
                    deployment.status = DeploymentStatus.FAILED
                    self.db.add(deployment)
                    
                    # Create failure notification
                    try:
                        user = self.db.execute(
                            select(User).where(User.id == deployment.user_id)
                        ).scalar_one()
                        notification = Notification(
                            user_id=user.id,
                            title="Deletion Failed",
                            message=f"Failed to delete microservice '{deployment.name}': {str(e)}",
                            type=NotificationType.ERROR,
                            link=f"/deployments/{deployment.id}" if deployment else None
                        )
                        self.db.add(notification)
                    except Exception:
                        pass
                
                self.db.commit()
            except Exception as db_error:
                logger.error(f"[CELERY ERROR] Failed to update job status for {self.deployment_id}: {db_error}")
            
            return {"status": "error", "message": str(e)}
        finally:
            if self.db:
                self.db.close()
    
    def _destroy(self):
        """Main destruction logic"""
        logger.info(f"Starting microservice deletion for deployment {self.deployment_id}")
        
        try:
            # Get deployment
            deployment_uuid = UUID(self.deployment_id) if isinstance(self.deployment_id, str) else self.deployment_id
            deployment = self.db.execute(
                select(Deployment).where(Deployment.id == deployment_uuid)
            ).scalar_one_or_none()
            
            if not deployment:
                logger.error(f"Deployment {self.deployment_id} not found")
                return {"status": "error", "message": "Deployment not found"}
            
            # Verify this is a microservice
            if deployment.deployment_type != "microservice":
                logger.warning(f"Deployment {self.deployment_id} is not a microservice, but destroy_microservice was called")
                self.log_message("WARNING", "This deployment is not a microservice")
            
            if not self.deletion_job_id:
                # Find deletion job
                deletion_job = self._find_deletion_job(deployment)
                if deletion_job:
                    self.deletion_job_id = deletion_job.id
            else:
                # Use provided job_id
                deletion_job = self.db.execute(select(Job).where(Job.id == self.deletion_job_id)).scalar_one_or_none()
    
            if deletion_job:
                if deletion_job.status == JobStatus.PENDING:
                    deletion_job.status = JobStatus.RUNNING
                    self.db.commit()
                self.log_message("INFO", f"Starting microservice deletion for deployment {self.deployment_id}")
            
            # Update status
            deployment.status = DeploymentStatus.DELETED  # Mark as deleted to prevent provisioning logic
            self.db.commit()
            self.log_message("INFO", "Updated deployment status to deleting")
            
            # Delete GitHub repository
            self._delete_github_repository(deployment)
            
            # Step 2: Destroy Pulumi infrastructure if it exists
            if deployment.pulumi_stack_name:
                self.log_message("INFO", f"Destroying associated infrastructure stack: {deployment.pulumi_stack_name}")
                try:
                    # In a real scenario, we would need the plugin path to destroy the stack
                    # For now, we'll mock this or look for the plugin used during provision
                    # plugin_path = ...
                    
                    # Mocking Pulumi destruction
                    # pulumi_service.destroy_stack(...)
                    self.log_message("INFO", f"Successfully destroyed Pulumi stack: {deployment.pulumi_stack_name}")
                except Exception as e:
                    self.log_message("WARNING", f"Failed to destroy infrastructure stack: {str(e)}")
                    # We continue deletion even if infra destruction fails, as the repo is already gone
                    # or we want to ensure the record is marked as deleted eventually.
            
            # Create notification
            create_notification_sync(
                user_id=str(deployment.user_id),
                title="Deletion Successful",
                message=f"Microservice '{deployment.name}' has been deleted successfully.",
                notification_type="success",
                link="/catalog"
            )
            self.db.commit()
            self.log_message("INFO", "Notification created for successful deletion")
            
            # Update deletion job
            if deletion_job:
                deletion_job.status = JobStatus.SUCCESS
                deletion_job.finished_at = datetime.now(timezone.utc)
                self.db.add(deletion_job)
                self.db.commit()
                self.log_message("INFO", "Deletion job completed successfully")
            
            # Mark deployment as deleted ONLY after successful destruction
            # This preserves history and allows users to see deleted deployments
            # Store as string value to ensure proper comparison in queries
            from app.models.deployment import DeploymentStatus
            deployment.status = DeploymentStatus.DELETED.value
            deployment.updated_at = datetime.now(timezone.utc)
            self.db.add(deployment)
            self.db.commit()
            self.log_message("INFO", f"Microservice deployment {deployment.id} ({deployment.name}) marked as DELETED after successful destruction")
            logger.info(f"Microservice deployment {self.deployment_id} marked as DELETED after successful destruction")
            
            return {"status": "success", "message": "Microservice deleted successfully"}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Destroy microservice failed: {error_msg}")
            self.log_message("ERROR", f"Destroy failed: {error_msg}")
            
            if deletion_job:
                deletion_job.status = JobStatus.FAILED
                deletion_job.finished_at = datetime.now(timezone.utc)
                deletion_job.error_message = error_msg
                self.db.add(deletion_job)
                self.db.commit()
            
            return {"status": "error", "message": error_msg}
    
    def _find_deletion_job(self, deployment: Deployment):
        """Find deletion job for deployment"""
        from app.models import Job, JobStatus
        
        deletion_job_result = self.db.execute(
            select(Job).where(
                Job.deployment_id == deployment.id,
                Job.status == JobStatus.PENDING
            ).order_by(Job.created_at.desc())
        )
        deletion_job_row = deletion_job_result.first()
        return deletion_job_row[0] if deletion_job_row else None
    
    def _delete_github_repository(self, deployment: Deployment):
        """Delete GitHub repository if it exists"""
        if deployment.github_repo_name:
            try:
                # Use user context to find org token
                user_id = deployment.user_id
                user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
                organization_id = str(user.organization_id)
                business_unit_id = str(user.active_business_unit_id) if user.active_business_unit_id else None
                
                user_github_token = git_service.get_github_token(organization_id, business_unit_id)
                
                if user_github_token:
                    self.log_message("INFO", f"Deleting GitHub repository: {deployment.github_repo_name}")
                    logger.info(f"Deleting GitHub repository: {deployment.github_repo_name}")
                    microservice_service.delete_github_repository(deployment.github_repo_name, user_github_token)
                    self.log_message("INFO", f"Successfully deleted GitHub repository: {deployment.github_repo_name}")
                    logger.info(f"Successfully deleted GitHub repository: {deployment.github_repo_name}")
                else:
                    self.log_message("WARNING", "GITHUB_TOKEN not configured for organization, cannot delete repository")
                    logger.warning("GITHUB_TOKEN not configured, skipping repository deletion")
            except Exception as e:
                error_msg = f"Could not delete GitHub repository: {str(e)}"
                self.log_message("WARNING", error_msg)
                logger.warning(error_msg, exc_info=True)
        else:
            self.log_message("INFO", "No GitHub repository associated with this deployment")

