"""Infrastructure provisioning and destruction tasks"""
from pathlib import Path
import tempfile
import shutil
import traceback
import asyncio
import re
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, Dict, Tuple, Callable

from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from app.tasks.db import get_sync_db_session
from app.tasks.utils import categorize_error
from app.logger import logger
from app.config import settings

from app.models import (
    Job, JobLog, JobStatus, PluginVersion, CloudCredential, Deployment,
    DeploymentStatus, User, Plugin, DeploymentHistory
)
from app.utils.notification_helper import create_notification_sync
from app.services.storage import storage_service
from app.services.pulumi_service import pulumi_service
from app.services.crypto import crypto_service
from app.services.git_service import git_service


class InfrastructureProvisionTask:
    """Task for provisioning infrastructure using Pulumi"""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.db: Optional[Session] = None
        self.temp_dir: Optional[Path] = None
    
    def log_message(self, level: str, message: str):
        """Log message to both JobLog and server log"""
        # Use a fresh session for logging to ensure thread-safety
        # especially for Pulumi callbacks called from separate threads
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
        log_func(f"[Job {self.job_id}] {message}")
    
    def execute(self, plugin_id: str, version: str, inputs: dict,
                credential_name: str = None, deployment_id: str = None):
        """Execute infrastructure provisioning"""
        self.db = get_sync_db_session()
        try:
            self._provision(plugin_id, version, inputs, credential_name, deployment_id)
        except Exception as e:
            self._handle_error(e, deployment_id)
        finally:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            if self.db:
                # Ensure any pending changes are committed before closing
                try:
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                finally:
                    self.db.close()
    
    def _provision(self, plugin_id: str, version: str, inputs: dict,
                   credential_name: str, deployment_id: str):
        """Main provisioning logic"""
        # Update job status
        job_result = self.db.execute(select(Job).where(Job.id == self.job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            error_msg = f"Job {self.job_id} not found in database"
            self.log_message("ERROR", error_msg)
            raise ValueError(error_msg)
        
        job.status = JobStatus.RUNNING
        self.db.add(job)  # Explicitly add job to ensure status is saved
        self.db.commit()
        
        self.log_message("INFO", "Starting provisioning job")
        
        # Get plugin version
        plugin_version = self._get_plugin_version(plugin_id, version)
        
        # Determine stack name and resource name
        # For updates/rollbacks, we need to preserve the existing stack_name and resource name
        # to avoid creating new resources
        temp_stack_name = f"{plugin_id}-{self.job_id[:8]}"
        temp_resource_name = inputs.get("bucket_name") or inputs.get("name") or f"{plugin_id}-{self.job_id[:8]}"
        
        # Setup deployment - this will return existing deployment if deployment_id is provided
        deployment, is_update, user_id = self._setup_deployment(
            job, plugin_id, version, inputs, deployment_id, plugin_version, temp_stack_name, temp_resource_name
        )
        
        # For updates/rollbacks, preserve existing stack_name
        if is_update and deployment:
            # Use existing stack_name (critical for Pulumi to update the same stack)
            stack_name = deployment.stack_name or temp_stack_name
            self.log_message("INFO", f"Update/rollback detected - using existing stack: {stack_name}")
            
            # Determine resource name from new inputs (user may want to change it)
            # If user provided a new resource name in inputs, use it; otherwise preserve existing
            existing_inputs = deployment.inputs or {}
            resource_name_key = "bucket_name" if "bucket_name" in inputs or "bucket_name" in existing_inputs else "name"
            
            # Log what we received for debugging
            self.log_message("INFO", f"Update inputs received: {list(inputs.keys()) if inputs else 'empty'}")
            self.log_message("INFO", f"Existing deployment inputs: {list(existing_inputs.keys()) if existing_inputs else 'empty'}")
            self.log_message("INFO", f"Resource name key: {resource_name_key}")
            
            # Check if user provided a new resource name in the update request
            if resource_name_key in inputs:
                # User explicitly provided a resource name - use it (allows renaming)
                resource_name = inputs[resource_name_key]
                existing_resource_name = existing_inputs.get(resource_name_key)
                if existing_resource_name and resource_name != existing_resource_name:
                    self.log_message("INFO", f"Resource name change detected: '{existing_resource_name}' -> '{resource_name}' (key: {resource_name_key})")
                else:
                    self.log_message("INFO", f"Using resource name '{resource_name}' from update request (key: {resource_name_key})")
            elif resource_name_key in existing_inputs:
                # No new resource name provided - preserve existing to avoid creating new resources
                existing_resource_name = existing_inputs[resource_name_key]
                resource_name = existing_resource_name
                # Update inputs to use existing resource name - this ensures Pulumi updates the same resource
                inputs = inputs.copy()
                inputs[resource_name_key] = existing_resource_name
                self.log_message("INFO", f"Preserving existing resource name '{resource_name}' for update (key: {resource_name_key})")
            else:
                # Fallback to deployment name if no resource name in inputs
                resource_name = deployment.name or temp_resource_name
                self.log_message("INFO", f"Using deployment name '{resource_name}' as resource name")
        else:
            # New deployment - use generated names
            stack_name = temp_stack_name
            resource_name = temp_resource_name
        
        # Ensure stack_name is valid
        if not stack_name or stack_name.strip() == "":
            stack_name = f"{plugin_id}-{self.job_id[:8]}"
            self.log_message("WARNING", f"stack_name was empty/None, using generated name: {stack_name}")
        
        # Setup plugin source (GitOps or ZIP)
        extract_path = self._setup_plugin_source(
            plugin_version, deployment, inputs, stack_name, resource_name, plugin_id, version
        )
        
        # ESC is required for credential management
        esc_env = pulumi_service.get_esc_environment(plugin_version.manifest)
        if not esc_env:
            cloud_provider = plugin_version.manifest.get("cloud_provider", "unknown").lower()
            error_msg = f"ESC environment not configured for {cloud_provider}. Please set PULUMI_ESC_ENVIRONMENT_{cloud_provider.upper()} in configuration."
            self.log_message("ERROR", error_msg)
            if deployment:
                try:
                    deployment.status = DeploymentStatus.FAILED
                    self.db.add(deployment)
                    self.db.commit()
                except Exception as deploy_error:
                    logger.warning(f"Failed to update deployment status: {deploy_error}")
            raise Exception(error_msg)
        
        self.log_message("INFO", f"ESC environment configured: {esc_env} - using automatic credential management")
        
        # Define callback for Pulumi output
        def on_output(msg):
            # Strip Pulumi's [Pulumi] prefix if present to avoid double prefixing
            clean_msg = msg[9:] if msg.startswith("[Pulumi] ") else msg
            self.log_message("INFO", clean_msg)
        
        # Run Pulumi
        self.log_message("INFO", f"Executing Pulumi program with ESC environment: {esc_env}")
        result = asyncio.run(pulumi_service.run_pulumi(
            plugin_path=extract_path,
            stack_name=stack_name,
            config=inputs,
            credentials=None,  # ESC handles credentials automatically
            manifest=plugin_version.manifest,
            on_output=on_output
        ))
        
        # Handle result
        self._handle_provision_result(result, job, deployment, inputs, is_update, resource_name, stack_name)
    
    def _get_plugin_version(self, plugin_id: str, version: str):
        """Get plugin version from database"""
        return self.db.execute(
            select(PluginVersion).where(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version
            )
        ).scalar_one()
    
    def _setup_deployment(self, job, plugin_id: str, version: str, inputs: dict,
                         deployment_id: str, plugin_version, stack_name: str,
                         resource_name: str) -> Tuple[Optional[Deployment], bool, Optional[str]]:
        """Setup or get deployment record"""
        deployment = None
        is_update = False
        user_id = None
        
        if deployment_id:
            deployment_uuid = UUID(deployment_id) if isinstance(deployment_id, str) else deployment_id
            deployment = self.db.execute(
                select(Deployment).where(Deployment.id == deployment_uuid)
            ).scalar_one_or_none()
            
            if deployment:
                if deployment.stack_name:
                    stack_name = deployment.stack_name
                user_id = deployment.user_id
                
                # Don't proceed if deployment is being deleted or already deleted
                if deployment.status == DeploymentStatus.DELETED:
                    self.log_message("ERROR", f"Deployment {deployment_id} is already deleted, cannot provision")
                    raise Exception(f"Deployment {deployment_id} is already deleted and cannot be provisioned")
                if deployment.status == DeploymentStatus.DELETING:
                    self.log_message("ERROR", f"Deployment {deployment_id} is being deleted, cannot provision")
                    raise Exception(f"Deployment {deployment_id} is being deleted and cannot be provisioned")
                
                # Use stack_name as the source of truth for whether this is an update
                # If we have a stack_name, we are updating an existing stack
                if deployment.stack_name:
                    is_update = True
                    self.log_message("INFO", f"Detected update job for deployment with existing stack: {deployment.name} (Stack: {deployment.stack_name})")
                elif deployment.status == DeploymentStatus.ACTIVE:
                    is_update = True
                    self.log_message("INFO", f"Detected update job for active deployment: {deployment.name}")
                
                # Backfill metadata if missing or unknown
                manifest_cp = plugin_version.manifest.get("cloud_provider", "unknown")
                input_region = inputs.get("location") or inputs.get("region") or "unknown"
                
                meta_updated = False
                if not deployment.cloud_provider or deployment.cloud_provider == "unknown":
                    deployment.cloud_provider = manifest_cp
                    meta_updated = True
                if not deployment.region or deployment.region == "unknown":
                    deployment.region = input_region
                    meta_updated = True
                
                if meta_updated:
                    self.db.add(deployment)
                    self.db.commit()
                    self.log_message("INFO", f"Backfilled metadata for deployment {deployment.id}: provider={deployment.cloud_provider}, region={deployment.region}")
            else:
                self.log_message("WARNING", f"Deployment {deployment_id} not found")
        
        # Create deployment if it doesn't exist
        if not deployment:
            # First, check if a deployment with the same name already exists for this plugin
            # This handles cases where the deployment-service creation was successful but
            # the ID wasn't properly linked, or if we're retrying a failed creation.
            existing_deployment = self.db.execute(
                select(Deployment).where(
                    Deployment.name == resource_name,
                    Deployment.plugin_id == plugin_id
                )
            ).scalar_one_or_none()
            
            if existing_deployment:
                deployment = existing_deployment
                self.log_message("INFO", f"Found existing deployment by name: {deployment.name} (ID: {deployment.id})")
                
                # Update job with the found deployment_id if it's missing
                if not job.deployment_id:
                    job.deployment_id = str(deployment.id)
                    self.db.add(job)
                    self.db.commit()
            
            # If still no deployment, then create it
            if not deployment:
                user = self.db.execute(
                    select(User).where(User.email == job.triggered_by)
                ).scalar_one_or_none()
                
                if user:
                    user_id = user.id
                deployment = Deployment(
                    name=resource_name,
                    plugin_id=plugin_id,
                    version=version,
                    status=DeploymentStatus.PROVISIONING,
                    user_id=user_id,
                    inputs=inputs,
                    stack_name=stack_name,
                    cloud_provider=plugin_version.manifest.get("cloud_provider", "unknown"),
                    region=inputs.get("location", "unknown")
                )
                self.db.add(deployment)
                self.db.commit()
                self.db.refresh(deployment)
                self.log_message("INFO", f"Created deployment record: {deployment.name} (ID: {deployment.id})")
            else:
                self.log_message("WARNING", f"User not found for email: {job.triggered_by}")
        
        # Fallback: get user from job if not found
        if not user_id:
            user = self.db.execute(
                select(User).where(User.email == job.triggered_by)
            ).scalar_one_or_none()
            if user:
                user_id = user.id
        
        return deployment, is_update, user_id
    
    def _setup_plugin_source(self, plugin_version, deployment, inputs: dict,
                            stack_name: str, resource_name: str, plugin_id: str,
                            version: str) -> Path:
        """Setup GitOps or ZIP extraction"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        if plugin_version.git_repo_url and plugin_version.git_branch:
            # GitOps flow
            self.log_message("INFO", f"Using GitOps: {plugin_version.git_repo_url} branch {plugin_version.git_branch}")
            try:
                # Check if deployment already has a git branch
                if deployment and deployment.git_branch:
                    deployment_branch = deployment.git_branch
                    self.log_message("INFO", f"Using existing deployment branch: {deployment_branch}")
                    repo_path = git_service.clone_repository(
                        plugin_version.git_repo_url,
                        deployment_branch,
                        self.temp_dir / "repo"
                    )
                    git_service.inject_user_values(repo_path, inputs, plugin_version.manifest, stack_name)
                    git_service.commit_changes(
                        repo_path,
                        f"Update deployment {deployment.name if deployment else resource_name}",
                        "IDP System",
                        "idp@system"
                    )
                else:
                    # First deployment - create new branch
                    repo_path = git_service.clone_repository(
                        plugin_version.git_repo_url,
                        plugin_version.git_branch,
                        self.temp_dir / "repo"
                    )
                    
                    # Create deployment branch name
                    deployment_name = deployment.name if deployment else resource_name
                    deployment_branch = re.sub(r'[^a-z0-9\-]', '-', deployment_name.lower())
                    deployment_branch = re.sub(r'-+', '-', deployment_branch)
                    deployment_branch = deployment_branch.strip('-')
                    
                    if not deployment_branch or len(deployment_branch) == 0:
                        deployment_branch = f"deploy-{deployment.id if deployment else self.job_id[:8]}"
                    if len(deployment_branch) > 255:
                        deployment_branch = deployment_branch[:255]
                    
                    self.log_message("INFO", f"Creating new deployment branch '{deployment_branch}' from template branch '{plugin_version.git_branch}'")
                    git_service.create_deployment_branch(repo_path, plugin_version.git_branch, deployment_branch)
                    git_service.inject_user_values(repo_path, inputs, plugin_version.manifest, stack_name)
                    git_service.commit_changes(
                        repo_path,
                        f"Deploy {deployment_name} - Initial deployment with user values",
                        "IDP System",
                        "idp@system"
                    )
                    
                    # Push branch to GitHub
                    try:
                        git_service.push_branch(repo_path, deployment_branch)
                        self.log_message("INFO", f"Pushed deployment branch '{deployment_branch}' to GitHub")
                    except Exception as push_error:
                        self.log_message("WARNING", f"Failed to push branch to GitHub (will use local): {push_error}")
                    
                    # Update deployment with git branch
                    if deployment:
                        deployment.git_branch = deployment_branch
                        self.db.commit()
                        self.log_message("INFO", f"Updated deployment record with git branch: {deployment_branch}")
                
                self.log_message("INFO", f"GitOps setup complete: branch {deployment_branch}")
                return repo_path
                
            except Exception as e:
                error_msg = f"GitOps setup failed: {str(e)}"
                self.log_message("ERROR", error_msg)
                logger.error(error_msg, exc_info=True)
                self.log_message("INFO", "Falling back to ZIP extraction")
                return storage_service.extract_plugin(plugin_id, version, self.temp_dir)
        else:
            # Legacy ZIP flow
            extract_path = storage_service.extract_plugin(plugin_id, version, self.temp_dir)
            self.log_message("INFO", f"Extracted plugin ZIP to {extract_path}")
            return extract_path
    
    
    def _handle_provision_result(self, result: Dict, job: Job, deployment: Optional[Deployment],
                                inputs: dict, is_update: bool, resource_name: str, stack_name: str):
        """Handle provisioning result"""
        # Re-fetch job and deployment to ensure we have latest state
        job = self.db.execute(select(Job).where(Job.id == self.job_id)).scalar_one()
        if deployment:
            deployment = self.db.execute(select(Deployment).where(Deployment.id == deployment.id)).scalar_one()
        
        # Check if deployment is being deleted - don't update status if so
        if deployment and deployment.status == DeploymentStatus.DELETING:
            self.log_message("WARNING", f"Deployment {deployment.id} is being deleted, skipping status update from provisioning job")
            # Still update job status but don't touch deployment
            if result["status"] == "success":
                job.status = JobStatus.SUCCESS
                job.outputs = result["outputs"]
                job.finished_at = datetime.now(timezone.utc)
            else:
                job.status = JobStatus.FAILED
                job.error_message = result.get('error', 'Unknown error')
                job.finished_at = datetime.now(timezone.utc)
            self.db.add(job)
            self.db.commit()
            return
        
        if result["status"] == "success":
            job.status = JobStatus.SUCCESS
            job.outputs = result["outputs"]
            job.finished_at = datetime.now(timezone.utc)
            self.db.add(job)  # Explicitly add job to ensure status is saved
            
            if deployment:
                if is_update:
                    # Capture previous inputs to detect real changes
                    previous_inputs = deployment.inputs.copy() if deployment.inputs else {}
                    
                    deployment.status = DeploymentStatus.ACTIVE.value
                    deployment.update_status = "update_succeeded"
                    deployment.last_update_error = None
                    deployment.inputs = inputs
                    deployment.outputs = result["outputs"]
                    self.log_message("INFO", "Deployment update completed successfully")
                    
                    # Only create a new history version if inputs actually changed
                    if inputs != previous_inputs:
                        self._save_deployment_history(deployment, inputs, result["outputs"], job, is_update=True)
                    else:
                        self.log_message("INFO", "Inputs unchanged; skipping new history version")
                else:
                    deployment.status = DeploymentStatus.ACTIVE
                    deployment.stack_name = stack_name
                    deployment.outputs = result["outputs"]
                    self.log_message("INFO", "Provisioning completed successfully")
                    
                    # Save initial history entry
                    self._save_deployment_history(deployment, inputs, result["outputs"], job, is_update=False)
                
                self.db.add(deployment)
            
            # Create success notification
            self._create_notification(deployment, resource_name, is_update, success=True)
            # Commit all changes
            self.db.commit()
            self.log_message("INFO", f"Job {self.job_id} completed successfully - changes committed")
        else:
            # Provisioning failed
            error_msg = result.get('error', 'Unknown error')
            error_state = categorize_error(error_msg)
            
            # Update job status - ensure it's explicitly added to session
            job.error_state = error_state
            job.error_message = error_msg
            job.status = JobStatus.FAILED
            job.finished_at = datetime.now(timezone.utc)
            self.db.add(job)  # Explicitly add job to ensure it's saved
            
            if is_update and deployment:
                deployment.update_status = "update_failed"
                deployment.last_update_error = error_msg
                self.db.add(deployment)
                
                # Create a history entry for the failed update attempt
                try:
                    max_version_result = self.db.execute(
                        select(func.max(DeploymentHistory.version_number))
                        .where(DeploymentHistory.deployment_id == deployment.id)
                    )
                    max_version = max_version_result.scalar() or 0
                    next_version = max_version + 1
                    
                    failed_history_entry = DeploymentHistory(
                        deployment_id=deployment.id,
                        version_number=next_version,
                        inputs=inputs.copy(),
                        outputs=None,  # No outputs for failed update
                        status=DeploymentStatus.FAILED.value,
                        job_id=self.job_id,
                        created_by=job.triggered_by,
                        description=f"Failed update attempt to version {next_version}"
                    )
                    self.db.add(failed_history_entry)
                    self.log_message("INFO", f"Created failed update history entry (version {next_version})")
                except Exception as hist_err:
                    self.log_message("WARNING", f"Failed to create failed update history entry: {hist_err}")
                
                self.db.commit()
                
                self.log_message("ERROR", f"Deployment update failed: {error_msg}")
                self.log_message("INFO", "Deployment remains active with previous configuration")
                
                self._create_notification(deployment, resource_name, is_update=True, success=False, error_state=error_state)
                logger.error(f"[UPDATE FAILED] Deployment {deployment.id} update failed. Deployment remains active. Error: {error_state} - {error_msg}")
            else:
                # For new deployments, always set status to FAILED
                if deployment:
                    deployment.status = DeploymentStatus.FAILED
                    self.db.add(deployment)
                    self.log_message("ERROR", f"Deployment status set to FAILED: {error_msg}")
                else:
                    self.log_message("WARNING", f"No deployment found to update status for job {self.job_id}")
                
                self.log_message("ERROR", f"Provisioning failed: {error_msg}")
                self.log_message("ERROR", f"Error category: {error_state}")
                
                self._create_notification(deployment, resource_name, is_update=False, success=False, error_state=error_state)
                self.db.commit()
                logger.error(f"[FAILED] Job {self.job_id} failed. Error: {error_state} - {error_msg}")
    
    def _save_deployment_history(self, deployment: Deployment, inputs: dict,
                                outputs: dict, job: Job, is_update: bool):
        """Save deployment history entry"""
        try:
            # If this is an update and inputs are identical to the latest history entry, skip creating a new version
            if is_update:
                latest_entry = self.db.execute(
                    select(DeploymentHistory)
                    .where(DeploymentHistory.deployment_id == deployment.id)
                    .order_by(DeploymentHistory.version_number.desc())
                    .limit(1)
                ).scalar_one_or_none()
                if latest_entry and latest_entry.inputs == inputs:
                    self.log_message("INFO", "Inputs unchanged vs latest history; skipping new history version")
                    return
            
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
            # Don't check for existing history - each update should create version 2, 3, etc.
            if is_update:
                max_version_result = self.db.execute(
                    select(func.max(DeploymentHistory.version_number))
                    .where(DeploymentHistory.deployment_id == deployment.id)
                )
                max_version = max_version_result.scalar() or 0
                next_version = max_version + 1
                
                history_entry = DeploymentHistory(
                    deployment_id=deployment.id,
                    version_number=next_version,
                    inputs=inputs.copy(),
                    outputs=outputs.copy() if outputs else None,
                    status=DeploymentStatus.ACTIVE,
                    job_id=self.job_id,
                    created_by=job.triggered_by,
                    description=f"Update to version {next_version}"
                )
            else:
                history_entry = DeploymentHistory(
                    deployment_id=deployment.id,
                    version_number=1,
                    inputs=inputs.copy(),
                    outputs=outputs.copy() if outputs else None,
                    status=DeploymentStatus.ACTIVE,
                    job_id=self.job_id,
                    created_by=job.triggered_by,
                    description="Initial deployment"
                )
            
            self.db.add(history_entry)
            version_num = history_entry.version_number
            self.log_message("INFO", f"Created new deployment history entry (version {version_num})")
        except Exception as hist_error:
            self.log_message("WARNING", f"Failed to save deployment history: {hist_error}")
    
    def _create_notification(self, deployment: Optional[Deployment], resource_name: str,
                           is_update: bool, success: bool, error_state: str = None):
        """Create notification for user"""
        job = self.db.execute(select(Job).where(Job.id == self.job_id)).scalar_one()
        user_email = job.triggered_by
        user = self.db.execute(select(User).where(User.email == user_email)).scalar_one_or_none()
        
        if not user:
            return
        
        if success:
            if is_update:
                create_notification_sync(
                    user_id=str(user.id),
                    title="Deployment Updated",
                    message=f"Resource '{resource_name}' has been updated successfully.",
                    notification_type="success",
                    link=f"/deployments/{deployment.id}" if deployment else f"/jobs/{self.job_id}"
                )
            else:
                create_notification_sync(
                    user_id=str(user.id),
                    title="Provisioning Successful",
                    message=f"Resource '{resource_name}' has been provisioned successfully.",
                    notification_type="success",
                    link=f"/deployments/{deployment.id}" if deployment else f"/jobs/{self.job_id}"
                )
        else:
            if is_update:
                create_notification_sync(
                    user_id=str(user.id),
                    title="Deployment Update Failed",
                    message=f"Update for '{resource_name}' failed. Deployment remains active with previous configuration. Error: {error_state}",
                    notification_type="error",
                    link=f"/deployments/{deployment.id}" if deployment else f"/jobs/{self.job_id}"
                )
            else:
                create_notification_sync(
                    user_id=str(user.id),
                    title="Provisioning Failed",
                    message=f"Job '{resource_name}' failed. Error: {error_state}. Please review and retry manually if needed.",
                    notification_type="error",
                    link=f"/jobs/{self.job_id}"
                )
    
    def _handle_error(self, error: Exception, deployment_id: str):
        """Handle errors during provisioning"""
        error_details = traceback.format_exc()
        error_msg = str(error)
        logger.error(f"[CELERY ERROR] Job {self.job_id} failed: {error_details}")
        
        try:
            # Get a fresh database session for error handling
            if not self.db:
                self.db = get_sync_db_session()
            job = self.db.execute(select(Job).where(Job.id == self.job_id)).scalar_one_or_none()
            if not job:
                logger.error(f"Job {self.job_id} not found in database during error handling")
                return
            error_state = categorize_error(error_msg)
            job.error_state = error_state
            job.error_message = error_msg
            job.status = JobStatus.FAILED
            job.finished_at = datetime.now(timezone.utc)
            self.db.add(job)  # Explicitly add job to ensure it's saved
            
            self.log_message("ERROR", f"Internal Error: {error_msg}")
            self.log_message("ERROR", f"Exception occurred: {error_msg}")
            self.log_message("ERROR", f"Error category: {error_state}")
            
            # Get deployment
            deployment = None
            if deployment_id:
                deployment_uuid = UUID(deployment_id) if isinstance(deployment_id, str) else deployment_id
                deployment = self.db.execute(
                    select(Deployment).where(Deployment.id == deployment_uuid)
                ).scalar_one_or_none()
            elif job.deployment_id:
                deployment = self.db.execute(
                    select(Deployment).where(Deployment.id == job.deployment_id)
                ).scalar_one_or_none()
            
            # Check if this is an update (only if deployment is ACTIVE)
            is_update_exception = deployment and deployment.status == DeploymentStatus.ACTIVE
            
            if is_update_exception:
                deployment.update_status = "update_failed"
                deployment.last_update_error = error_msg
                self.db.add(deployment)
                self.db.commit()
                
                self.log_message("ERROR", f"Deployment update failed with exception: {error_msg}")
                self.log_message("INFO", "Deployment remains active with previous configuration")
                
                self._create_notification(deployment, deployment.name if deployment else "resource", is_update=True, success=False, error_state=error_state)
            elif deployment:
                # For new deployments or deployments in PROVISIONING status, set to FAILED
                if deployment.status in [DeploymentStatus.PROVISIONING, DeploymentStatus.ACTIVE]:
                    deployment.status = DeploymentStatus.FAILED
                    self.db.add(deployment)
                    self.log_message("ERROR", f"Deployment status set to FAILED due to error: {error_msg}")
                else:
                    # Deployment might already be in a different state, but still log the error
                    self.log_message("WARNING", f"Deployment {deployment.id} is in status {deployment.status}, not updating to FAILED")
                
                self._create_notification(deployment, deployment.name if deployment else "resource", is_update=False, success=False, error_state=error_state)
                self.db.commit()
            else:
                # No deployment found, but still commit the job status
                self.log_message("WARNING", f"No deployment found for job {self.job_id}, job status set to FAILED")
                self.db.commit()
            
            logger.error(f"[FAILED] Job {self.job_id} failed with exception. Error: {error_state} - {error_msg}")
        except Exception as db_error:
            logger.error(f"[CELERY ERROR] Failed to update job status for {self.job_id}: {db_error}", exc_info=True)


class InfrastructureDestroyTask:
    """Task for destroying infrastructure"""
    
    def __init__(self, deployment_id: str):
        self.deployment_id = deployment_id
        self.db: Optional[Session] = None
        self.deletion_job_id: Optional[str] = None
        self.temp_dir: Optional[Path] = None
    
    def log_message(self, level: str, message: str):
        """Log message to both JobLog and server log"""
        # Use a fresh session for logging to ensure thread-safety
        try:
            log_db = get_sync_db_session()
            try:
                log = JobLog(job_id=self.deletion_job_id, level=level, message=message)
                log_db.add(log)
                log_db.commit()
            finally:
                log_db.close()
        except Exception as e:
            logger.warning(f"Failed to write job log: {e}")
        
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"[Deletion Job {self.deletion_job_id or 'N/A'}] {message}")
    
    def execute(self):
        """Execute infrastructure destruction"""
        self.db = get_sync_db_session()
        try:
            # Define callback for Pulumi output
            def on_output(msg):
                # We don't have a job_id here for log_message, so we log to server logs
                # and potentially update deployment status if we had a way to log specifically
                # for destroy tasks. For now, server logs it is.
                logger.info(f"[Pulumi Destroy] {msg}")
            
            return self._destroy(on_output=on_output)
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"[CELERY ERROR] Destroy task failed for deployment {self.deployment_id}: {error_details}")
            
            try:
                deployment_uuid = UUID(self.deployment_id) if isinstance(self.deployment_id, str) else self.deployment_id
                deployment = self.db.execute(
                    select(Deployment).where(Deployment.id == deployment_uuid)
                ).scalar_one_or_none()
                
                if deployment:
                    deployment.status = DeploymentStatus.FAILED
                    self.db.commit()
            except Exception as db_error:
                logger.error(f"[CELERY ERROR] Failed to update deployment status: {db_error}")
            
            return {"status": "error", "message": str(e)}
        finally:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            if self.db:
                self.db.close()
    
    def _destroy(self, on_output: Optional[Callable[[str], None]] = None):
        """Main destruction logic"""
        logger.info(f"[destroy_infrastructure] Starting infrastructure destruction for deployment {self.deployment_id}")
        
        # Get deployment
        deployment_uuid = UUID(self.deployment_id) if isinstance(self.deployment_id, str) else self.deployment_id
        deployment = self.db.execute(
            select(Deployment).where(Deployment.id == deployment_uuid)
        ).scalar_one_or_none()
        
        if not deployment:
            logger.error(f"Deployment {self.deployment_id} not found")
            return {"status": "error", "message": "Deployment not found"}
        
        # Find deletion job
        deletion_job = self._find_deletion_job(deployment)
        if deletion_job:
            self.deletion_job_id = deletion_job.id
            if deletion_job.status == JobStatus.PENDING:
                deletion_job.status = JobStatus.RUNNING
                self.db.commit()
            self.log_message("INFO", f"Starting infrastructure destruction for deployment {self.deployment_id}")
        
        # Note: We do NOT mark as DELETED here - only after successful destruction
        # This allows the deployment to remain visible with its current status until destruction completes
        # Refresh deployment to get latest state
        self.db.refresh(deployment)
        
        # Get plugin version
        plugin_version = self.db.execute(
            select(PluginVersion).where(
                PluginVersion.plugin_id == deployment.plugin_id,
                PluginVersion.version == deployment.version
            )
        ).scalar_one()
        
        # Setup plugin source
        extract_path = self._setup_plugin_source(deployment, plugin_version)
        
        # Run Pulumi destroy
        if not deployment.stack_name:
            self.log_message("WARNING", "No stack_name found - this may be a microservice deployment or deployment was never provisioned")
            result = {
                "status": "success",
                "summary": {},
                "message": "No stack to destroy (microservice deployment or never provisioned)"
            }
        else:
            # ESC is required for credential management when destroying a stack
            # Create minimal manifest for ESC lookup
            manifest = {"cloud_provider": deployment.cloud_provider.lower()} if deployment.cloud_provider else None
            esc_env = pulumi_service.get_esc_environment(manifest)
            if not esc_env:
                cloud_provider = deployment.cloud_provider or "unknown"
                error_msg = f"ESC environment not configured for {cloud_provider}. Please set PULUMI_ESC_ENVIRONMENT_{cloud_provider.upper()} in configuration."
                self.log_message("ERROR", error_msg)
                raise Exception(error_msg)
            
            self.log_message("INFO", f"ESC environment configured: {esc_env} - using automatic credential management for destroy")
            self.log_message("INFO", f"Executing Pulumi destroy for stack: {deployment.stack_name}")
            # Run Pulumi destroy
            result = asyncio.run(pulumi_service.destroy_stack(
                plugin_path=extract_path,
                stack_name=deployment.stack_name,
                credentials=None,
                cloud_provider=deployment.cloud_provider,
                on_output=on_output
            ))
        
        self.log_message("INFO", f"Pulumi destroy completed with status: {result.get('status', 'unknown')}")
        
        # Handle result
        error_msg = result.get('error', '')
        is_stack_not_found = 'no stack named' in str(error_msg).lower() or 'not found' in str(error_msg).lower()
        
        if result["status"] == "success" or is_stack_not_found:
            if is_stack_not_found:
                self.log_message("WARNING", "Stack not found in Pulumi, deleting deployment record anyway")
            
            # Create notification
            self._create_success_notification(deployment)
            
            # Update deletion job
            if deletion_job:
                deletion_job.status = JobStatus.SUCCESS
                deletion_job.finished_at = datetime.now(timezone.utc)
                self.db.add(deletion_job)
                self.db.commit()
                self.log_message("INFO", "Deletion job completed successfully")
            
            # Delete GitOps branch
            self._delete_gitops_branch(deployment, plugin_version)
            
            # Mark deployment as deleted ONLY after successful destruction
            # This preserves history and allows users to see deleted deployments
            # Store as string value to ensure proper comparison in queries
            # Refresh deployment first to ensure we have the latest state
            self.db.refresh(deployment)
            deployment.status = DeploymentStatus.DELETED.value
            deployment.updated_at = datetime.now(timezone.utc)
            self.db.add(deployment)
            self.db.commit()
            # Verify the status was saved correctly
            self.db.refresh(deployment)
            actual_status = str(deployment.status).lower()
            if actual_status != "deleted":
                logger.error(f"CRITICAL: Deployment {deployment.id} status was not saved as 'deleted'. Actual status: {actual_status}")
                # Try again with explicit string
                deployment.status = "deleted"
                self.db.add(deployment)
                self.db.commit()
                self.db.refresh(deployment)
                logger.info(f"Retried setting deployment status. New status: {deployment.status}")
            logger.info(f"Deployment {deployment.id} ({deployment.name}) marked as DELETED after successful infrastructure destruction. Status verified: {deployment.status}")
            return {"status": "success", "message": "Infrastructure destroyed, branch deleted, and deployment marked as deleted"}
        else:
            # Destroy failed
            logger.error(f"Destroy failed: {error_msg}")
            self.log_message("ERROR", f"Destroy failed: {error_msg}")
            deployment.status = DeploymentStatus.FAILED
            
            if deletion_job:
                deletion_job.status = JobStatus.FAILED
                deletion_job.finished_at = datetime.now(timezone.utc)
                self.db.add(deletion_job)
                self.db.commit()
            
            # Create failure notification
            create_notification_sync(
                user_id=str(deployment.user_id),
                title="Deletion Failed",
                message=f"Failed to delete '{deployment.name}': {error_msg}",
                notification_type="error",
                link=f"/deployments/{deployment.id}"
            )
            return {"status": "error", "message": error_msg}
    
    def _find_deletion_job(self, deployment: Deployment):
        """Find deletion job for deployment"""
        from app.models import Job, JobStatus
        
        # Use enum value (string) for comparison to avoid SQL enum issues
        deletion_job_result = self.db.execute(
            select(Job).where(
                Job.deployment_id == deployment.id,
                Job.status == JobStatus.PENDING.value  # Use .value to get "pending" string
            ).order_by(Job.created_at.desc())
        )
        deletion_job_row = deletion_job_result.first()
        deletion_job = deletion_job_row[0] if deletion_job_row else None
        
        if not deletion_job:
            deletion_job_result = self.db.execute(
                select(Job).where(Job.deployment_id == deployment.id)
                .order_by(Job.created_at.desc())
            )
            deletion_job_row = deletion_job_result.first()
            deletion_job = deletion_job_row[0] if deletion_job_row else None
        
        if not deletion_job:
            logger.warning(f"Deletion job not found for deployment {self.deployment_id}, continuing without job tracking")
            self.log_message("WARNING", f"Deletion job not found for deployment {self.deployment_id}")
        
        return deletion_job
    
    def _setup_plugin_source(self, deployment: Deployment, plugin_version) -> Path:
        """Setup plugin source for destruction"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pulumi_destroy_"))
        
        if deployment.git_branch and plugin_version.git_repo_url:
            try:
                repo_path = git_service.clone_repository(
                    plugin_version.git_repo_url,
                    deployment.git_branch,
                    self.temp_dir / "repo"
                )
                self.log_message("INFO", f"Cloned deployment branch {deployment.git_branch}")
                return repo_path
            except Exception as e:
                error_msg = f"GitOps clone failed: {str(e)}"
                self.log_message("ERROR", error_msg)
                logger.error(error_msg, exc_info=True)
                self.log_message("INFO", "Falling back to ZIP extraction")
                return storage_service.extract_plugin(deployment.plugin_id, deployment.version, self.temp_dir)
        elif plugin_version.git_repo_url and plugin_version.git_branch:
            try:
                repo_path = git_service.clone_repository(
                    plugin_version.git_repo_url,
                    plugin_version.git_branch,
                    self.temp_dir / "repo"
                )
                self.log_message("INFO", f"Cloned template branch {plugin_version.git_branch}")
                return repo_path
            except Exception as e:
                error_msg = f"GitOps clone failed: {str(e)}"
                self.log_message("ERROR", error_msg)
                logger.error(error_msg, exc_info=True)
                self.log_message("INFO", "Falling back to ZIP extraction")
                return storage_service.extract_plugin(deployment.plugin_id, deployment.version, self.temp_dir)
        else:
            self.log_message("INFO", "Extracting plugin ZIP to temporary directory")
            extract_path = storage_service.extract_plugin(deployment.plugin_id, deployment.version, self.temp_dir)
            self.log_message("INFO", "Plugin extracted successfully")
            return extract_path
    
    def _create_success_notification(self, deployment: Deployment):
        """Create success notification"""
        create_notification_sync(
            user_id=str(deployment.user_id),
            title="Deletion Successful",
            message=f"Resource '{deployment.name}' has been deleted successfully.",
            notification_type="success",
            link="/catalog"
        )
        self.db.commit()
        self.log_message("INFO", "Notification created for successful deletion")
    
    def _unlink_jobs(self, deployment: Deployment):
        """Unlink jobs from deployment"""
        from app.models import Job
        jobs = self.db.execute(
            select(Job).where(Job.deployment_id == deployment.id)
        ).scalars().all()
        
        for job in jobs:
            job.deployment_id = None
            self.db.add(job)
        self.db.commit()
        self.log_message("INFO", "Unlinked jobs from deployment to preserve history")
    
    def _delete_gitops_branch(self, deployment: Deployment, plugin_version):
        """Delete GitOps branch from GitHub"""
        if deployment.git_branch and plugin_version.git_repo_url:
            try:
                github_token = settings.GITHUB_TOKEN if hasattr(settings, 'GITHUB_TOKEN') else ""
                if not github_token:
                    self.log_message("WARNING", "GITHUB_TOKEN not configured, cannot delete branch via API")
                    logger.warning("GITHUB_TOKEN not configured, skipping branch deletion")
                else:
                    self.log_message("INFO", f"Deleting deployment branch '{deployment.git_branch}' from GitHub repository '{plugin_version.git_repo_url}' (after infrastructure removal)")
                    logger.info(f"Attempting to delete branch '{deployment.git_branch}' from {plugin_version.git_repo_url} (after infrastructure removal)")
                    git_service.delete_branch(plugin_version.git_repo_url, deployment.git_branch, github_token)
                    self.log_message("INFO", f"Successfully deleted deployment branch '{deployment.git_branch}' from GitHub")
                    logger.info(f"Successfully deleted branch '{deployment.git_branch}' from GitHub")
            except Exception as branch_error:
                error_msg = f"Failed to delete branch '{deployment.git_branch}': {str(branch_error)}"
                self.log_message("WARNING", error_msg)
                logger.warning(error_msg, exc_info=True)

