"""Plugin service for upload and provisioning"""
import json
import uuid
import tempfile
import shutil
import zipfile
import re
import httpx
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

from app.models.plugin import Plugin, PluginVersion
from app.models.job import Job, JobLog, JobStatus
from app.models.access import PluginAccess, PluginAccessRequest, AccessRequestStatus
from app.services.plugin_validator import plugin_validator
from app.services.storage_service import storage_service
from app.services.git_service import git_service
from app.services.tag_validator import validate_tags
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def to_uuid(value: Optional[str]) -> Optional[uuid.UUID]:
    """Convert string to UUID object, returns None if invalid or empty"""
    if not value:
        return None
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return None


async def get_admins_and_bu_owners(business_unit_id: Optional[str]) -> List[str]:
    """Get list of admin and BU owner user IDs to notify for plugin access requests"""
    user_ids = []
    
    try:
        async with httpx.AsyncClient() as client:
            # Get all users from auth service
            response = await client.get(
                "http://auth-service:8000/api/v1/users",
                timeout=5.0
            )
            
            if response.status_code == 200:
                users = response.json()
                
                # Check each user for admin permissions
                for user in users:
                    try:
                        # Check if user is admin (has platform:plugins:upload or is system admin)
                        perm_response = await client.post(
                            "http://auth-service:8000/api/v1/permissions/check",
                            json={
                                "user_id": user["id"],
                                "permission": "platform:plugins:upload",
                                "resource": "platform",
                                "action": "upload"
                            },
                            timeout=5.0
                        )
                        
                        if perm_response.status_code == 200 and perm_response.json().get("allowed", False):
                            if user["id"] not in user_ids:
                                user_ids.append(user["id"])
                                logger.info(f"Added admin to notify list: {user.get('email', user['id'])}")
                    except Exception as e:
                        logger.warning(f"Error checking admin permissions for user {user.get('id')}: {e}")
                        continue
            
            # Get BU owners if business_unit_id is provided
            if business_unit_id:
                try:
                    bu_response = await client.get(
                        f"http://auth-service:8000/api/v1/business-units/{business_unit_id}/members",
                        timeout=5.0
                    )
                    
                    if bu_response.status_code == 200:
                        members = bu_response.json()
                        
                        for member in members:
                            # Check if member has permission to manage BU members (indicates owner/manager)
                            perm_response = await client.post(
                                "http://auth-service:8000/api/v1/permissions/check",
                                json={
                                    "user_id": member["user_id"],
                                    "permission": "business_unit:business_units:manage_members",
                                    "resource": "business_unit",
                                    "action": "manage_members",
                                    "business_unit_id": business_unit_id
                                },
                                timeout=5.0
                            )
                            
                            if perm_response.status_code == 200 and perm_response.json().get("allowed", False):
                                if member["user_id"] not in user_ids:
                                    user_ids.append(member["user_id"])
                                    logger.info(f"Added BU owner to notify list: {member.get('user_id')}")
                except Exception as e:
                    logger.warning(f"Error getting BU owners for business_unit {business_unit_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error getting admins and BU owners: {e}")
    
    logger.info(f"Total users to notify: {len(user_ids)}")
    return user_ids


async def send_notification(user_id: str, title: str, message: str, notification_type: str = "info", link: str = ""):
    """Send notification to user via notification-service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://notification-service:8000/api/v1/notifications",
                json={
                    "user_id": user_id,
                    "title": title,
                    "message": message,
                    "type": notification_type,
                    "link": link
                },
                timeout=5.0
            )
            if response.status_code == 201:
                logger.info(f"Notification sent to user {user_id}: {title}")
            else:
                error_detail = response.text if hasattr(response, 'text') else str(response.status_code)
                logger.warning(f"Failed to send notification: {response.status_code} - {error_detail}")
                # Log response body for debugging
                try:
                    error_body = response.json() if hasattr(response, 'json') else None
                    if error_body:
                        logger.warning(f"Notification service error details: {error_body}")
                except:
                    pass
    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)


class PluginService:
    """Service for plugin operations"""
    
    async def upload_plugin(
        self,
        file_content: bytes,
        filename: str,
        git_repo_url: Optional[str],
        git_branch: Optional[str],
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Upload a plugin ZIP file"""
        # Validate file
        if not filename or not filename.endswith('.zip'):
            raise ValueError("Only ZIP files are accepted")
        
        # Save to temporary file for validation
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(file_content)
            tmp_path = Path(tmp_file.name)
        
        try:
            # Validate plugin ZIP
            is_valid, error_msg, manifest = plugin_validator.validate_zip(tmp_path)
            if not is_valid:
                raise ValueError(f"Invalid plugin: {error_msg}")
            
            plugin_id = manifest['id']
            version = manifest['version']
            
            # Check if plugin exists
            result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
            plugin = result.scalar_one_or_none()
            
            if not plugin:
                # Create new plugin
                plugin = Plugin(
                    id=plugin_id,
                    name=manifest.get('name', plugin_id),
                    description=manifest.get('description'),
                    author=manifest.get('author')
                )
                db.add(plugin)
            
            # Check if version exists
            result = await db.execute(
                select(PluginVersion).where(
                    PluginVersion.plugin_id == plugin_id,
                    PluginVersion.version == version
                )
            )
            existing_version = result.scalar_one_or_none()
            if existing_version:
                raise ValueError(f"Plugin '{plugin_id}' version '{version}' already exists")
            
            # Determine Git repository URL
            config_repo_url = settings.GITHUB_REPOSITORY.strip() if settings.GITHUB_REPOSITORY else None
            final_git_repo_url = git_repo_url or config_repo_url
            final_git_branch = git_branch
            
            # Save to storage
            storage_path = storage_service.save_plugin(plugin_id, version, file_content)
            
            # Extract and push to GitHub if GitOps is enabled
            if final_git_repo_url and tmp_path.exists():
                extract_dir = Path(storage_path).parent / "extracted"
                extract_dir.mkdir(parents=True, exist_ok=True)
                
                temp_extract = Path(storage_path).parent / "temp_extract"
                temp_extract.mkdir(parents=True, exist_ok=True)
                
                with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                    members = [m for m in zip_ref.infolist() if not (m.filename.startswith('__MACOSX') or m.filename.endswith('.DS_Store'))]
                    zip_ref.extractall(temp_extract, members)
                
                # Flatten structure if single root directory
                root_items = list(temp_extract.iterdir())
                if len(root_items) == 1 and root_items[0].is_dir() and root_items[0].name == plugin_id:
                    for item in root_items[0].iterdir():
                        dest = extract_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest)
                    shutil.rmtree(temp_extract, ignore_errors=True)
                else:
                    for item in root_items:
                        dest = extract_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest)
                    shutil.rmtree(temp_extract, ignore_errors=True)
                
                # Generate branch name if not provided
                if not final_git_branch:
                    raw_name = manifest.get('name') or plugin_id
                    base_name = raw_name.lower().replace(" ", "-").replace("_", "-")
                    base_name = re.sub(r'[^a-z0-9\-]', '-', base_name)
                    base_name = re.sub(r'-+', '-', base_name).strip('-')
                    if not base_name:
                        base_name = plugin_id.lower()
                    final_git_branch = f"plugin-{base_name}"
                
                # Push to GitHub
                try:
                    git_service.initialize_and_push_plugin(
                        repo_url=final_git_repo_url,
                        branch=final_git_branch,
                        source_dir=extract_dir,
                        commit_message=f"Upload plugin {plugin_id} version {version}"
                    )
                except Exception as e:
                    logger.error(f"Failed to push plugin to GitHub: {e}", exc_info=True)
                    if git_repo_url:  # If explicitly provided, fail
                        raise ValueError(f"Failed to push plugin to GitHub: {str(e)}")
                    # Otherwise, continue without GitOps
                    final_git_repo_url = None
                    final_git_branch = None
            
            # Create plugin version record
            plugin_version = PluginVersion(
                plugin_id=plugin_id,
                version=version,
                manifest=manifest,
                storage_path=storage_path,
                git_repo_url=final_git_repo_url,
                git_branch=final_git_branch
            )
            db.add(plugin_version)
            await db.commit()
            await db.refresh(plugin_version)
            
            return {
                "id": plugin_version.id,
                "plugin_id": plugin_version.plugin_id,
                "version": plugin_version.version,
                "manifest": json.dumps(plugin_version.manifest),
                "storage_path": plugin_version.storage_path,
                "git_repo_url": plugin_version.git_repo_url or "",
                "git_branch": plugin_version.git_branch or "",
                "template_repo_url": plugin_version.template_repo_url or "",
                "template_path": plugin_version.template_path or "",
                "created_at": plugin_version.created_at.isoformat() if plugin_version.created_at else ""
            }
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
    
    async def upload_microservice_template(
        self,
        plugin_id: str,
        name: str,
        version: str,
        description: str,
        template_repo_url: str,
        template_path: str,
        author: Optional[str],
        user_id: str,
        db: AsyncSession,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a microservice template"""
        # Validate inputs
        if not template_repo_url.strip():
            raise ValueError("Template repository URL is required")
        if not template_path.strip():
            raise ValueError("Template path is required")
        
        # Check if plugin exists
        result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = result.scalar_one_or_none()
        
        if not plugin:
            plugin = Plugin(
                id=plugin_id,
                name=name,
                description=description,
                author=author or user_id,
                deployment_type="microservice",
                is_locked=False
            )
            db.add(plugin)
        else:
            plugin.name = name
            plugin.description = description
            plugin.deployment_type = "microservice"
            if author:
                plugin.author = author
        
        await db.flush()
        
        # Check if version exists
        result = await db.execute(
            select(PluginVersion).where(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version
            )
        )
        existing_version = result.scalar_one_or_none()
        if existing_version:
            raise ValueError(f"Plugin '{plugin_id}' version '{version}' already exists")
        
        # Create manifest
        manifest = {
            "id": plugin_id,
            "name": name,
            "version": version,
            "description": description,
            "deployment_type": "microservice",
            "cloud_provider": "kubernetes",
            "language": "python",
            "framework": "fastapi"
        }
        
        # Add custom inputs if provided
        if inputs:
            manifest["inputs"] = inputs
        
        # Create plugin version
        plugin_version = PluginVersion(
            plugin_id=plugin_id,
            version=version,
            manifest=manifest,
            storage_path="",
            template_repo_url=template_repo_url.strip(),
            template_path=template_path.strip(),
            git_repo_url=template_repo_url.strip(),
            git_branch="main"
        )
        db.add(plugin_version)
        await db.commit()
        await db.refresh(plugin_version)
        
        return {
            "id": plugin_version.id,
            "plugin_id": plugin_version.plugin_id,
            "version": plugin_version.version,
            "manifest": json.dumps(plugin_version.manifest),
            "storage_path": plugin_version.storage_path,
            "git_repo_url": plugin_version.git_repo_url or "",
            "git_branch": plugin_version.git_branch or "",
            "template_repo_url": plugin_version.template_repo_url or "",
            "template_path": plugin_version.template_path or "",
            "created_at": plugin_version.created_at.isoformat() if plugin_version.created_at else ""
        }
    
    async def provision_plugin(
        self,
        plugin_id: str,
        version: str,
        inputs: Dict[str, Any],
        environment: str,
        tags: Dict[str, str],
        deployment_name: Optional[str],
        cost_center: Optional[str],
        project_code: Optional[str],
        user_id: str,
        user_email: str,
        business_unit_id: Optional[str],
        organization_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Create a provisioning job"""
        logger.info(f"Provisioning job starting for {plugin_id}:{version}, user: {user_email}")
        try:
            # Validate tags
            is_valid, error_msg = validate_tags(tags, environment)
            if not is_valid:
                raise ValueError(f"Tag validation failed: {error_msg}")
            
            # Validate plugin version exists
            result = await db.execute(
                select(PluginVersion).where(
                    PluginVersion.plugin_id == plugin_id,
                    PluginVersion.version == version
                )
            )
            plugin_version = result.scalar_one_or_none()
            if not plugin_version:
                raise ValueError(f"Plugin {plugin_id} version {version} not found")
        
            # Get plugin
            result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
            plugin = result.scalar_one_or_none()
            if not plugin:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            deployment_type = plugin.deployment_type or "infrastructure"
            cloud_provider = plugin_version.manifest.get("cloud_provider", "unknown")
            
            # Create job
            job_inputs = inputs.copy() if inputs else {}
            if business_unit_id:
                job_inputs["_business_unit_id"] = business_unit_id
            
            # Create job using raw SQL to properly cast enum
            job_id = str(uuid.uuid4())
            from sqlalchemy import text
            
            # Insert job with proper enum cast - use bindparam for proper parameter binding
            await db.execute(
                text("""
                    INSERT INTO jobs (id, plugin_version_id, deployment_id, status, triggered_by, inputs, retry_count, created_at)
                    VALUES (:id, :plugin_version_id, :deployment_id, CAST(:status AS jobstatus), :triggered_by, CAST(:inputs AS jsonb), 0, NOW())
                """),
                {
                    "id": job_id,
                    "plugin_version_id": plugin_version.id,
                    "deployment_id": None,
                    "status": JobStatus.PENDING.value,
                    "triggered_by": user_email,
                    "inputs": json.dumps(job_inputs)
                }
            )
            
            # Add initial log
            log_entry = JobLog(
                job_id=job_id,
                level="INFO",
                message=f"Job created for {plugin_id}:{version}"
            )
            db.add(log_entry)
            
            await db.commit()
        
            # Fetch the job to return
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one()
            
            # Create deployment via deployment-service
            deployment_id = None
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    # Determine deployment name
                    if deployment_type == "microservice":
                        deployment_name = inputs.get("deployment_name") or inputs.get("name") or f"{plugin_id}-{job_id[:8]}"
                    else:
                        deployment_name = inputs.get("bucket_name") or inputs.get("name") or f"{plugin_id}-{job_id[:8]}"
                    
                    logger.info(f"Attempting to create deployment: {deployment_name}, type: {deployment_type}, cloud_provider: {cloud_provider}")
                    
                    # Prepare inputs with metadata for deployment-service
                    deployment_inputs = inputs.copy()
                    deployment_inputs["_cloud_provider"] = cloud_provider
                    deployment_inputs["_region"] = inputs.get("location") or inputs.get("region") or "unknown"
                    
                    # Create deployment
                    deployment_response = await client.post(
                        "http://deployment-service:8000/api/v1/deployments",
                        json={
                            "name": deployment_name,
                            "deployment_type": deployment_type,
                            "plugin_id": plugin_id,
                            "version": version,
                            "environment": environment,
                            "user_id": user_id,
                            "business_unit_id": business_unit_id or "",
                            "inputs": deployment_inputs,
                            "cost_center": cost_center or "",
                            "project_code": project_code or ""
                        },
                        timeout=10.0
                    )
                    
                    if deployment_response.status_code == 201:
                        deployment_data = deployment_response.json()
                        deployment_id = deployment_data.get("id")
                        
                        if deployment_id:
                            logger.info(f"Created deployment {deployment_id} for job {job_id}")
                            # Add tags to deployment
                            tags_to_add = tags.copy() if tags else {}
                            if business_unit_id:
                                try:
                                    from app.models.business_unit import BusinessUnit
                                    bu_result = await db.execute(
                                        select(BusinessUnit).where(BusinessUnit.id == business_unit_id)
                                    )
                                    business_unit = bu_result.scalar_one_or_none()
                                    if business_unit:
                                        tags_to_add["business_unit"] = business_unit.name
                                except Exception:
                                    pass
                            
                            for key, value in tags_to_add.items():
                                try:
                                    await client.post(
                                        f"http://deployment-service:8000/api/v1/deployments/{deployment_id}/tags",
                                        json={"key": key, "value": value},
                                        timeout=5.0
                                    )
                                except Exception:
                                    pass
                            
                            # Update job to link to deployment
                            await db.execute(
                                text("UPDATE jobs SET deployment_id = :deployment_id WHERE id = :job_id"),
                                {"deployment_id": deployment_id, "job_id": job_id}
                            )
                            await db.commit()
                            
                            # Update job object directly to avoid async refresh issues
                            job.deployment_id = deployment_id
                        else:
                            logger.error(f"Deployment created but ID missing in response: {deployment_data}")
                            raise ValueError("Deployment creation succeeded but returned no ID")
                    else:
                        logger.error(f"Failed to create deployment: {deployment_response.status_code} {deployment_response.text}")
                        # Fail the provisioning if deployment creation fails
                        raise ValueError(f"Failed to create deployment record: {deployment_response.text}")
            except ValueError:
                # Re-raise ValueErrors (like the one above)
                raise
            except Exception as e:
                logger.error(f"Failed to create deployment for job {job_id}: {e}", exc_info=True)
                # Fail the provisioning if deployment creation fails dramatically
                raise ValueError(f"Failed to create deployment due to connection error: {str(e)}")
            
            # Trigger worker-service to process the job
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    if deployment_type == "microservice":
                        # Call microservice provisioning endpoint
                        worker_response = await client.post(
                            "http://worker-service:8000/api/v1/provision/microservice",
                            json={
                                "job_id": job.id,
                                "plugin_id": plugin_id,
                                "version": version,
                                "deployment_name": inputs.get("deployment_name") or inputs.get("name") or f"{plugin_id}-{job.id[:8]}",
                                "user_id": user_id,
                                "deployment_id": deployment_id or job.deployment_id or "",
                                "inputs": inputs
                            },
                            timeout=30.0
                        )
                    else:
                        # Call infrastructure provisioning endpoint
                        # Get credential name from plugin manifest or use default
                        credential_name = None
                        if cloud_provider:
                            credential_name = f"{cloud_provider.lower()}_default"
                        
                        worker_response = await client.post(
                            "http://worker-service:8000/api/v1/provision/infrastructure",
                            json={
                                "job_id": str(job.id),  # Ensure it's a string
                                "plugin_id": plugin_id,
                                "version": version,
                                "inputs": inputs,
                                "credential_name": credential_name or None,
                                "deployment_id": (deployment_id or job.deployment_id or "") if (deployment_id or job.deployment_id) else None
                            },
                            timeout=30.0
                        )
                    
                    if worker_response.status_code == 202:
                        response_data = worker_response.json()
                        task_id = response_data.get("task_id")
                        logger.info(f"Successfully triggered worker-service for job {job.id}. Celery Task ID: {task_id}")
                        # Add log to JobLog
                        log_entry = JobLog(
                            job_id=job.id,
                            level="INFO",
                            message=f"Provisioning task dispatched to worker. Task ID: {task_id}"
                        )
                        db.add(log_entry)
                        await db.commit()
                    else:
                        error_detail = worker_response.text
                        logger.error(f"Worker service returned error {worker_response.status_code} for job {job.id}: {error_detail}")
                        # Add error log to JobLog
                        log_entry = JobLog(
                            job_id=job.id,
                            level="ERROR",
                            message=f"Failed to dispatch task to worker. Status: {worker_response.status_code}"
                        )
                        db.add(log_entry)
                        await db.commit()
            except Exception as e:
                logger.error(f"Failed to trigger worker-service: {e}", exc_info=True)
                # Don't fail the job creation if worker trigger fails - job will be picked up later
            
            return {
                "job_id": job.id,
                "deployment_id": job.deployment_id or "",
                "status": job.status if isinstance(job.status, str) else job.status.value,
                "message": "Job created successfully"
            }
        except Exception as e:
            import traceback
            logger.error(f"CRITICAL ERROR in provision_plugin: {str(e)}")
            traceback.print_exc()
            raise
    
    async def get_job(self, job_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get a job by ID"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError("Job not found")
        
        return {
            "id": job.id,
            "plugin_version_id": job.plugin_version_id,
            "deployment_id": job.deployment_id or "",
            "status": job.status if isinstance(job.status, str) else job.status.value,
            "triggered_by": job.triggered_by,
            "inputs": json.dumps(job.inputs),
            "outputs": json.dumps(job.outputs) if job.outputs else "",
            "retry_count": job.retry_count,
            "error_state": job.error_state or "",
            "error_message": job.error_message or "",
            "created_at": job.created_at.isoformat() if job.created_at else "",
            "finished_at": job.finished_at.isoformat() if job.finished_at else ""
        }
    
    async def list_jobs(
        self,
        user_id: str,
        business_unit_id: Optional[str],
        skip: int,
        limit: int,
        status: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """List jobs with filters"""
        # Build query
        query = select(Job)
        
        # Filter by business unit if provided
        if business_unit_id:
            bu_id_str = str(business_unit_id)
            query = query.where(
                cast(Job.inputs, JSONB)['_business_unit_id'].astext == bu_id_str
            )
        
        # Filter by status if provided
        if status:
            query = query.where(Job.status == JobStatus(status))
        
        # Get total count
        count_query = select(func.count()).select_from(Job)
        if business_unit_id:
            bu_id_str = str(business_unit_id)
            count_query = count_query.where(
                cast(Job.inputs, JSONB)['_business_unit_id'].astext == bu_id_str
            )
        if status:
            count_query = count_query.where(Job.status == JobStatus(status))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Get paginated results
        query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return {
            "jobs": [
                {
                    "id": j.id,
                    "plugin_version_id": j.plugin_version_id,
                    "deployment_id": j.deployment_id or "",
                    "status": j.status if isinstance(j.status, str) else j.status.value,
                    "triggered_by": j.triggered_by,
                    "inputs": json.dumps(j.inputs),
                    "outputs": json.dumps(j.outputs) if j.outputs else "",
                    "retry_count": j.retry_count,
                    "error_state": j.error_state or "",
                    "error_message": j.error_message or "",
                    "created_at": j.created_at.isoformat() if j.created_at else "",
                    "finished_at": j.finished_at.isoformat() if j.finished_at else ""
                }
                for j in jobs
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    async def get_job_logs(
        self,
        job_id: str,
        skip: int,
        limit: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get job logs"""
        # Verify job exists
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise ValueError("Job not found")
        
        # Get logs
        count_query = select(func.count()).select_from(JobLog).where(JobLog.job_id == job_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        query = select(JobLog).where(JobLog.job_id == job_id).order_by(JobLog.timestamp).offset(skip).limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "job_id": log.job_id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else "",
                    "level": log.level,
                    "message": log.message
                }
                for log in logs
            ],
            "total": total
        }
    
    async def cancel_job(self, job_id: str, user_id: str, db: AsyncSession):
        """Cancel a job"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError("Job not found")
        
        # Check status - handle both string and enum
        status_str = job.status if isinstance(job.status, str) else job.status.value
        if status_str in [JobStatus.SUCCESS.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
            raise ValueError(f"Cannot cancel job with status: {status_str}")
        
        job.status = JobStatus.CANCELLED.value
        job.finished_at = datetime.now(timezone.utc)
        
        log_entry = JobLog(
            job_id=job.id,
            level="INFO",
            message=f"Job cancelled by user {user_id}"
        )
        db.add(log_entry)
        
        await db.commit()
    
    async def delete_job(self, job_id: str, user_id: str, db: AsyncSession):
        """Delete a job"""
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError("Job not found")
        
        # Delete logs first
        await db.execute(select(JobLog).where(JobLog.job_id == job_id))
        logs_result = await db.execute(select(JobLog).where(JobLog.job_id == job_id))
        logs = logs_result.scalars().all()
        for log in logs:
            await db.delete(log)
        
        # Delete job
        await db.delete(job)
        await db.commit()
    
    # ==================== Plugin CRUD Methods ====================
    
    async def list_plugins(
        self,
        user_id: str,
        business_unit_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """List all plugins with access information"""
        # Get all plugins
        result = await db.execute(select(Plugin))
        plugins = result.scalars().all()
        
        # Get all versions for all plugins
        plugin_ids = [p.id for p in plugins]
        versions_result = await db.execute(
            select(PluginVersion).where(PluginVersion.plugin_id.in_(plugin_ids))
        )
        all_versions = versions_result.scalars().all()
        
        # Group versions by plugin_id
        versions_by_plugin = {}
        for version in all_versions:
            if version.plugin_id not in versions_by_plugin:
                versions_by_plugin[version.plugin_id] = []
            versions_by_plugin[version.plugin_id].append(version)
        
        # TODO: Check if user is admin (would need auth-service call or shared logic)
        # For now, assume we'll get is_admin flag from caller
        is_admin = False  # This should be passed as parameter or checked via auth-service
        
        # Get user access for non-admins
        user_access = set()
        pending_requests = set()
        
        if not is_admin:
            user_uuid = to_uuid(user_id)
            bu_uuid = to_uuid(business_unit_id) if business_unit_id else None
            
            if user_uuid:
                # Build conditions for access checks
                # Match monolith behavior: check ONLY the specific business_unit_id (not NULL)
                # This ensures access is scoped to the current business unit
                if bu_uuid:
                    # Check PluginAccess for current business unit only
                    access_result = await db.execute(
                        select(PluginAccess).where(
                            PluginAccess.user_id == user_uuid,
                            PluginAccess.business_unit_id == bu_uuid
                        )
                    )
                    user_access = {access.plugin_id for access in access_result.scalars().all()}
                    
                    # Check approved access requests for current business unit only
                    request_result = await db.execute(
                        select(PluginAccessRequest).where(
                            PluginAccessRequest.user_id == user_uuid,
                            PluginAccessRequest.business_unit_id == bu_uuid,
                            PluginAccessRequest.status == "approved"
                        )
                    )
                    user_access.update({req.plugin_id for req in request_result.scalars().all()})
                    
                    # Check pending requests for current business unit only
                    pending_result = await db.execute(
                        select(PluginAccessRequest).where(
                            PluginAccessRequest.user_id == user_uuid,
                            PluginAccessRequest.business_unit_id == bu_uuid,
                            PluginAccessRequest.status == "pending"
                        )
                    )
                    pending_requests = {req.plugin_id for req in pending_result.scalars().all()}
                else:
                    # No business unit - check for NULL business_unit_id only (backward compatibility)
                    access_result = await db.execute(
                        select(PluginAccess).where(
                            PluginAccess.user_id == user_uuid,
                            PluginAccess.business_unit_id.is_(None)
                        )
                    )
                    user_access = {access.plugin_id for access in access_result.scalars().all()}
                    
                    # Check approved access requests with NULL business_unit_id
                    request_result = await db.execute(
                        select(PluginAccessRequest).where(
                            PluginAccessRequest.user_id == user_uuid,
                            PluginAccessRequest.business_unit_id.is_(None),
                            PluginAccessRequest.status == "approved"
                        )
                    )
                    user_access.update({req.plugin_id for req in request_result.scalars().all()})
                    
                    # Check pending requests with NULL business_unit_id
                    pending_result = await db.execute(
                        select(PluginAccessRequest).where(
                            PluginAccessRequest.user_id == user_uuid,
                            PluginAccessRequest.business_unit_id.is_(None),
                            PluginAccessRequest.status == "pending"
                        )
                    )
                    pending_requests = {req.plugin_id for req in pending_result.scalars().all()}
        
        # Build response
        plugin_list = []
        for plugin in plugins:
            has_access = True
            has_pending = False
            
            if plugin.is_locked:
                has_access = is_admin or (plugin.id in user_access)
                has_pending = plugin.id in pending_requests
            
            # Get versions for this plugin
            plugin_versions = versions_by_plugin.get(plugin.id, [])
            
            # Get latest version
            latest_version = None
            if plugin_versions:
                sorted_versions = sorted(plugin_versions, key=lambda v: v.version, reverse=True)
                latest_version = sorted_versions[0]
            
            plugin_data = {
                "id": plugin.id,
                "name": plugin.name,
                "description": plugin.description,
                "author": plugin.author,
                "is_locked": plugin.is_locked,
                "deployment_type": plugin.deployment_type,
                "has_access": has_access,
                "has_pending_request": has_pending,
                "created_at": plugin.created_at.isoformat() if plugin.created_at else "",
                "updated_at": plugin.updated_at.isoformat() if plugin.updated_at else "",
                "versions": [{
                    "id": v.id,
                    "plugin_id": v.plugin_id,
                    "version": v.version,
                    "manifest": json.dumps(v.manifest) if v.manifest else "{}",
                    "storage_path": v.storage_path or "",
                    "git_repo_url": v.git_repo_url or "",
                    "git_branch": v.git_branch or "",
                    "template_repo_url": v.template_repo_url or "",
                    "template_path": v.template_path or "",
                    "created_at": v.created_at.isoformat() if v.created_at else ""
                } for v in plugin_versions]
            }
            
            if latest_version and latest_version.manifest:
                manifest = latest_version.manifest
                plugin_data["latest_version"] = latest_version.version
                plugin_data["category"] = manifest.get('category', 'service')
                plugin_data["cloud_provider"] = manifest.get('cloud_provider', 'other')
            else:
                plugin_data["latest_version"] = "0.0.0"
                plugin_data["category"] = "service"
                plugin_data["cloud_provider"] = "other"
            
            plugin_list.append(plugin_data)
        
        return {"plugins": plugin_list}
    
    async def get_plugin(
        self,
        plugin_id: str,
        user_id: str,
        business_unit_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get plugin details"""
        result = await db.execute(
            select(Plugin).where(Plugin.id == plugin_id)
        )
        plugin = result.scalar_one_or_none()
        
        if not plugin:
            raise ValueError("Plugin not found")
        
        # Get versions for this plugin
        versions_result = await db.execute(
            select(PluginVersion).where(PluginVersion.plugin_id == plugin_id)
        )
        plugin_versions = versions_result.scalars().all()
        
        # TODO: Check if user is admin
        is_admin = False
        
        # Check access
        has_access = True
        has_pending = False
        
        if plugin.is_locked:
            has_access = is_admin
            if not is_admin:
                user_uuid = to_uuid(user_id)
                # Convert business_unit_id to UUID, handling empty strings
                bu_uuid = None
                if business_unit_id and business_unit_id.strip():
                    bu_uuid = to_uuid(business_unit_id)
                
                logger.info(f"DEBUG get_plugin: user_id={user_id}, business_unit_id={business_unit_id}, bu_uuid={bu_uuid}")
                
                if user_uuid:
                    # Build conditions for access checks
                    if bu_uuid:
                        bu_condition = or_(
                            PluginAccess.business_unit_id == bu_uuid,
                            PluginAccess.business_unit_id.is_(None)
                        )
                        bu_request_condition = or_(
                            PluginAccessRequest.business_unit_id == bu_uuid,
                            PluginAccessRequest.business_unit_id.is_(None)
                        )
                        logger.info(f"DEBUG: Using BU condition with bu_uuid={bu_uuid}")
                    else:
                        bu_condition = PluginAccess.business_unit_id.is_(None)
                        bu_request_condition = PluginAccessRequest.business_unit_id.is_(None)
                        logger.info(f"DEBUG: Using NULL condition (no BU)")
                    
                    # Check PluginAccess
                    access_result = await db.execute(
                        select(PluginAccess).where(
                            PluginAccess.plugin_id == plugin_id,
                            PluginAccess.user_id == user_uuid,
                            bu_condition
                        )
                    )
                    has_access = access_result.scalar_one_or_none() is not None
                    
                    # Check approved request
                    if not has_access:
                        request_result = await db.execute(
                            select(PluginAccessRequest).where(
                                PluginAccessRequest.plugin_id == plugin_id,
                                PluginAccessRequest.user_id == user_uuid,
                                bu_request_condition,
                                PluginAccessRequest.status == "approved"
                            )
                        )
                        has_access = request_result.scalar_one_or_none() is not None
                    
                    # Check pending request
                    pending_result = await db.execute(
                        select(PluginAccessRequest).where(
                            PluginAccessRequest.plugin_id == plugin_id,
                            PluginAccessRequest.user_id == user_uuid,
                            bu_request_condition,
                            PluginAccessRequest.status == "pending"
                        )
                    )
                    has_pending = pending_result.scalar_one_or_none() is not None
        
        # Get latest version
        latest_version = None
        if plugin_versions:
            sorted_versions = sorted(plugin_versions, key=lambda v: v.version, reverse=True)
            latest_version = sorted_versions[0]
        
        # Check if user is admin (for git info visibility)
        # TODO: This should be passed as parameter or checked via auth-service
        # For now, we'll check via auth-service
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                perm_response = await client.post(
                    f"http://auth-service:8000/api/v1/permissions/check-service",
                    json={
                        "user_id": user_id,
                        "permission": "platform:plugins:upload",
                        "resource": "platform"
                    },
                    timeout=5.0
                )
                if perm_response.status_code == 200:
                    perm_data = perm_response.json()
                    is_admin = perm_data.get("has_permission", False)
                else:
                    is_admin = False
        except Exception as e:
            logger.warning(f"Could not check admin permissions: {e}")
            is_admin = False
        
        result = {
            "id": plugin.id,
            "name": plugin.name,
            "description": plugin.description,
            "author": plugin.author,
            "is_locked": plugin.is_locked,
            "deployment_type": plugin.deployment_type,
            "has_access": has_access,
            "has_pending_request": has_pending,
            "created_at": plugin.created_at.isoformat() if plugin.created_at else "",
            "updated_at": plugin.updated_at.isoformat() if plugin.updated_at else "",
            "latest_version": latest_version.version if latest_version else "0.0.0",
            "versions": [{
                "id": v.id,
                "plugin_id": v.plugin_id,
                "version": v.version,
                "manifest": json.dumps(v.manifest) if v.manifest else "{}",
                "storage_path": v.storage_path,
                "git_repo_url": v.git_repo_url or "",
                "git_branch": v.git_branch or "",
                "template_repo_url": v.template_repo_url or "",
                "template_path": v.template_path or "",
                "created_at": v.created_at.isoformat() if v.created_at else ""
            } for v in plugin_versions]
        }
        
        # Add git info at top level for admins (from latest version)
        if is_admin and latest_version:
            result["git_repo_url"] = latest_version.git_repo_url
            result["git_branch"] = latest_version.git_branch
        else:
            result["git_repo_url"] = None
            result["git_branch"] = None
        
        return result
    
    async def delete_plugin(
        self,
        plugin_id: str,
        user_id: str,
        db: AsyncSession
    ):
        """Delete a plugin"""
        # TODO: Check permissions (user must be admin)
        
        result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = result.scalar_one_or_none()
        
        if not plugin:
            raise ValueError("Plugin not found")
        
        # Get all plugin versions for this plugin
        versions_result = await db.execute(
            select(PluginVersion).where(PluginVersion.plugin_id == plugin_id)
        )
        plugin_versions = versions_result.scalars().all()
        version_ids = [v.id for v in plugin_versions]
        
        # Collect Git branches to delete (before we delete plugin versions)
        branches_to_delete = set()
        for version in plugin_versions:
            if version.git_repo_url and version.git_branch:
                branches_to_delete.add((version.git_repo_url, version.git_branch))
        
        # Step 1: Delete all jobs that reference these plugin versions using raw SQL
        # This MUST happen before deleting plugin_versions to avoid FK constraint violation
        if version_ids:
            # Use IN clause with tuple for PostgreSQL
            placeholders = ",".join([f":id{i}" for i in range(len(version_ids))])
            params = {f"id{i}": vid for i, vid in enumerate(version_ids)}
            result = await db.execute(
                text(f"DELETE FROM jobs WHERE plugin_version_id IN ({placeholders})"),
                params
            )
            await db.flush()  # Flush to ensure deletions are visible
            await db.commit()  # Commit jobs deletion immediately
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} jobs referencing plugin versions: {version_ids}")
        
        # Step 2: Also delete job_logs for safety (they should cascade, but let's be explicit)
        # Job logs have ON DELETE CASCADE, but let's make sure
        
        # Step 3: Delete plugin access requests
        access_requests_result = await db.execute(
            select(PluginAccessRequest).where(PluginAccessRequest.plugin_id == plugin_id)
        )
        access_requests = access_requests_result.scalars().all()
        for req in access_requests:
            await db.delete(req)
        if access_requests:
            await db.commit()  # Commit access requests deletion
        
        # Step 4: Delete plugin access grants
        access_grants_result = await db.execute(
            select(PluginAccess).where(PluginAccess.plugin_id == plugin_id)
        )
        access_grants = access_grants_result.scalars().all()
        for grant in access_grants:
            await db.delete(grant)
        if access_grants:
            await db.commit()  # Commit access grants deletion
        
        # Step 5: Delete plugin versions (now safe since jobs are deleted)
        # Use raw SQL to ensure immediate deletion
        if version_ids:
            placeholders = ",".join([f":id{i}" for i in range(len(version_ids))])
            params = {f"id{i}": vid for i, vid in enumerate(version_ids)}
            result = await db.execute(
                text(f"DELETE FROM plugin_versions WHERE id IN ({placeholders})"),
                params
            )
            await db.flush()
            await db.commit()  # Commit plugin versions deletion before deleting plugin
            deleted_versions = result.rowcount
            logger.info(f"Deleted {deleted_versions} plugin versions")
        
        # Verify no plugin versions remain (safety check)
        remaining_versions = await db.execute(
            select(PluginVersion).where(PluginVersion.plugin_id == plugin_id)
        )
        if remaining_versions.scalar_one_or_none():
            raise ValueError(f"Failed to delete all plugin versions for {plugin_id}")
        
        # Step 6: Delete Git branches associated with plugin versions
        # Delete each branch (don't fail plugin deletion if branch deletion fails)
        for repo_url, branch in branches_to_delete:
            try:
                success = git_service.delete_branch(repo_url, branch)
                if success:
                    logger.info(f"Deleted Git branch {branch} from {repo_url}")
                else:
                    logger.warning(f"Failed to delete Git branch {branch} from {repo_url}, continuing...")
            except Exception as e:
                logger.warning(f"Error deleting Git branch {branch} from {repo_url}: {e}, continuing...")
        
        # Step 7: Delete plugin storage files (delete entire plugin directory with all versions)
        try:
            plugin_storage_dir = Path(storage_service.base_path) / plugin_id
            if plugin_storage_dir.exists():
                shutil.rmtree(plugin_storage_dir)
                logger.info(f"Deleted plugin storage directory: {plugin_storage_dir}")
        except Exception as e:
            logger.warning(f"Failed to delete plugin storage for {plugin_id}: {e}")
        
        # Step 8: Finally, delete the plugin itself
        # Since all plugin_versions are deleted, CASCADE will have nothing to do
        await db.delete(plugin)
        await db.flush()
        await db.commit()
        
        logger.info(f"Successfully deleted plugin {plugin_id} and all related data")
    
    async def lock_plugin(
        self,
        plugin_id: str,
        user_id: str,
        db: AsyncSession
    ):
        """Lock a plugin"""
        # TODO: Check permissions
        
        result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = result.scalar_one_or_none()
        
        if not plugin:
            raise ValueError("Plugin not found")
        
        plugin.is_locked = True
        plugin.updated_at = datetime.now(timezone.utc)
        await db.commit()
        
        # Send notification (fire and forget)
        await send_notification(
            user_id=user_id,
            title="Plugin Locked",
            message=f"Plugin '{plugin.name}' has been locked. Users will need to request access to use it.",
            notification_type="warning",
            link=f"/services"
        )
    
    async def unlock_plugin(
        self,
        plugin_id: str,
        user_id: str,
        db: AsyncSession
    ):
        """Unlock a plugin"""
        # TODO: Check permissions
        
        result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = result.scalar_one_or_none()
        
        if not plugin:
            raise ValueError("Plugin not found")
        
        plugin.is_locked = False
        plugin.updated_at = datetime.now(timezone.utc)
        await db.commit()
        
        # Send notification (fire and forget)
        await send_notification(
            user_id=user_id,
            title="Plugin Unlocked",
            message=f"Plugin '{plugin.name}' has been unlocked. All users can now access it.",
            notification_type="success",
            link=f"/services"
        )
    
    # ==================== Plugin Version Methods ====================
    
    async def list_plugin_versions(
        self,
        plugin_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """List all versions of a plugin"""
        result = await db.execute(
            select(PluginVersion).where(PluginVersion.plugin_id == plugin_id)
            .order_by(PluginVersion.created_at.desc())
        )
        versions = result.scalars().all()
        
        return {
            "versions": [{
                "id": v.id,
                "plugin_id": v.plugin_id,
                "version": v.version,
                "manifest": json.dumps(v.manifest) if v.manifest else "{}",
                "storage_path": v.storage_path,
                "git_repo_url": v.git_repo_url or "",
                "git_branch": v.git_branch or "",
                "template_repo_url": v.template_repo_url or "",
                "template_path": v.template_path or "",
                "created_at": v.created_at.isoformat() if v.created_at else ""
            } for v in versions]
        }
    
    async def get_plugin_version(
        self,
        plugin_id: str,
        version: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get a specific plugin version"""
        result = await db.execute(
            select(PluginVersion).where(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version
            )
        )
        version_obj = result.scalar_one_or_none()
        
        if not version_obj:
            raise ValueError(f"Plugin version {plugin_id}:{version} not found")
        
        return {
            "id": version_obj.id,
            "plugin_id": version_obj.plugin_id,
            "version": version_obj.version,
            "manifest": json.dumps(version_obj.manifest) if version_obj.manifest else "{}",
            "storage_path": version_obj.storage_path,
            "git_repo_url": version_obj.git_repo_url or "",
            "git_branch": version_obj.git_branch or "",
            "template_repo_url": version_obj.template_repo_url or "",
            "template_path": version_obj.template_path or "",
            "created_at": version_obj.created_at.isoformat() if version_obj.created_at else ""
        }
    
    # ==================== Plugin Access Methods ====================
    
    async def request_plugin_access(
        self,
        plugin_id: str,
        user_id: str,
        business_unit_id: Optional[str],
        note: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Request access to a locked plugin"""
        # Verify plugin exists and is locked
        result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = result.scalar_one_or_none()
        
        if not plugin:
            raise ValueError("Plugin not found")
        
        if not plugin.is_locked:
            raise ValueError("Plugin is not locked, access request not needed")
        
        user_uuid = to_uuid(user_id)
        bu_uuid = to_uuid(business_unit_id)
        
        if not user_uuid:
            raise ValueError("Invalid user ID")
        
        # Build condition for business unit filtering (NULL OR matching BU)
        if bu_uuid:
            bu_request_condition = or_(
                PluginAccessRequest.business_unit_id == bu_uuid,
                PluginAccessRequest.business_unit_id.is_(None)
            )
        else:
            bu_request_condition = PluginAccessRequest.business_unit_id.is_(None)
        
        # Check if user already has approved access
        access_result = await db.execute(
            select(PluginAccessRequest).where(
                PluginAccessRequest.plugin_id == plugin_id,
                PluginAccessRequest.user_id == user_uuid,
                bu_request_condition,
                PluginAccessRequest.status == "approved"
            )
        )
        if access_result.scalar_one_or_none():
            raise ValueError("You already have access to this plugin")
        
        # Check if there's already a pending request (same BU context)
        pending_result = await db.execute(
            select(PluginAccessRequest).where(
                PluginAccessRequest.plugin_id == plugin_id,
                PluginAccessRequest.user_id == user_uuid,
                bu_request_condition,
                PluginAccessRequest.status == "pending"
            )
        )
        if pending_result.scalar_one_or_none():
            raise ValueError("You already have a pending access request for this plugin")
        
        # Create access request
        access_request = PluginAccessRequest(
            id=uuid.uuid4(),
            plugin_id=plugin_id,
            user_id=user_uuid,
            business_unit_id=bu_uuid,
            status="pending",
            note=note
        )
        db.add(access_request)
        await db.commit()
        await db.refresh(access_request)
        
        # Send notification to the user
        await send_notification(
            user_id=user_id,
            title="Access Request Submitted",
            message=f"Your access request for plugin '{plugin.name}' has been submitted and is pending approval.",
            notification_type="info",
            link="/plugin-requests"
        )
        
        # Send notifications to admins and BU owners
        notify_user_ids = await get_admins_and_bu_owners(business_unit_id)
        
        # Get user email for the notification message
        user_email = "A user"
        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{user_id}",
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    user_email = user_data.get("email", user_data.get("username", "A user"))
        except Exception as e:
            logger.warning(f"Could not fetch user email for notification: {e}")
        
        note_text = f"\n\nReason: {note}" if note else ""
        for notify_user_id in notify_user_ids:
            await send_notification(
                user_id=notify_user_id,
                title="Plugin Access Request",
                message=f"{user_email} requested access to locked plugin: {plugin.name}{note_text}",
                notification_type="info",
                link="/admin/plugin-requests"
            )
        
        return {
            "id": str(access_request.id),
            "plugin_id": access_request.plugin_id,
            "user_id": str(access_request.user_id),
            "business_unit_id": str(access_request.business_unit_id) if access_request.business_unit_id else "",
            "status": access_request.status,
            "note": access_request.note or "",
            "requested_at": access_request.requested_at.isoformat() if access_request.requested_at else "",
            "reviewed_at": access_request.reviewed_at.isoformat() if access_request.reviewed_at else "",
            "reviewed_by": str(access_request.reviewed_by) if access_request.reviewed_by else ""
        }
    
    async def grant_plugin_access(
        self,
        plugin_id: str,
        user_id: str,
        granted_by_user_id: str,
        business_unit_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Grant access to a plugin"""
        # Verify plugin exists
        result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = result.scalar_one_or_none()
        
        if not plugin:
            raise ValueError("Plugin not found")
        
        user_uuid = to_uuid(user_id)
        granted_by_uuid = to_uuid(granted_by_user_id)
        
        if not user_uuid:
            raise ValueError("Invalid user ID")
        if not granted_by_uuid:
            raise ValueError("Invalid granted by user ID")
        
        # Find pending request first - get business_unit_id from the request if not provided
        request_result = await db.execute(
            select(PluginAccessRequest).where(
                PluginAccessRequest.plugin_id == plugin_id,
                PluginAccessRequest.user_id == user_uuid,
                PluginAccessRequest.status == "pending"
            ).order_by(PluginAccessRequest.requested_at.desc())
        )
        access_request = request_result.scalar_one_or_none()
        
        if not access_request:
            raise ValueError("Pending access request not found")
        
        # Use business_unit_id from the request if not provided
        bu_uuid = to_uuid(business_unit_id) if business_unit_id else access_request.business_unit_id
        
        # Update the pending request to approved
        access_request.status = "approved"
        access_request.reviewed_at = datetime.now(timezone.utc)
        access_request.reviewed_by = granted_by_uuid
        
        # Create or update PluginAccess grant
        access_result = await db.execute(
            select(PluginAccess).where(
                PluginAccess.plugin_id == plugin_id,
                PluginAccess.user_id == user_uuid,
                PluginAccess.business_unit_id == bu_uuid
            )
        )
        plugin_access = access_result.scalar_one_or_none()
        
        if not plugin_access:
            plugin_access = PluginAccess(
                plugin_id=plugin_id,
                user_id=user_uuid,
                business_unit_id=bu_uuid,
                granted_by=granted_by_uuid
            )
            db.add(plugin_access)
        
        await db.commit()
        await db.refresh(access_request)
        await db.refresh(plugin_access)
        
        # Send notification to the user
        await send_notification(
            user_id=user_id,
            title="Access Request Approved",
            message=f"Your access request for plugin '{plugin.name}' has been approved! You can now use this plugin.",
            notification_type="success",
            link=f"/provision/{plugin_id}"
        )
        
        return {
            "id": plugin_access.id,
            "plugin_id": plugin_access.plugin_id,
            "user_id": str(plugin_access.user_id),
            "business_unit_id": str(plugin_access.business_unit_id) if plugin_access.business_unit_id else "",
            "granted_by": str(plugin_access.granted_by),
            "granted_at": plugin_access.granted_at.isoformat() if plugin_access.granted_at else ""
        }
    
    async def reject_plugin_access(
        self,
        plugin_id: str,
        user_id: str,
        rejected_by_user_id: str,
        db: AsyncSession
    ):
        """Reject an access request"""
        # Get plugin info for notification
        plugin_result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = plugin_result.scalar_one_or_none()
        
        user_uuid = to_uuid(user_id)
        rejected_by_uuid = to_uuid(rejected_by_user_id)
        
        if not user_uuid:
            raise ValueError("Invalid user ID")
        
        result = await db.execute(
            select(PluginAccessRequest).where(
                PluginAccessRequest.plugin_id == plugin_id,
                PluginAccessRequest.user_id == user_uuid,
                PluginAccessRequest.status == "pending"
            )
        )
        access_request = result.scalar_one_or_none()
        
        if not access_request:
            raise ValueError("Pending access request not found")
        
        access_request.status = "rejected"
        access_request.reviewed_at = datetime.now(timezone.utc)
        access_request.reviewed_by = rejected_by_uuid
        
        await db.commit()
        
        # Send notification to the user
        plugin_name = plugin.name if plugin else plugin_id
        await send_notification(
            user_id=user_id,
            title="Access Request Rejected",
            message=f"Your access request for plugin '{plugin_name}' has been rejected.",
            notification_type="error",
            link="/plugin-requests"
        )
    
    async def revoke_plugin_access(
        self,
        plugin_id: str,
        user_id: str,
        revoked_by_user_id: str,
        db: AsyncSession
    ):
        """Revoke plugin access"""
        # Get plugin info for notification
        plugin_result = await db.execute(select(Plugin).where(Plugin.id == plugin_id))
        plugin = plugin_result.scalar_one_or_none()
        
        if not plugin:
            raise ValueError("Plugin not found")
        
        user_uuid = to_uuid(user_id)
        
        if not user_uuid:
            raise ValueError("Invalid user ID")
        
        # Find approved access request to get business_unit_id
        request_result = await db.execute(
            select(PluginAccessRequest).where(
                PluginAccessRequest.plugin_id == plugin_id,
                PluginAccessRequest.user_id == user_uuid,
                PluginAccessRequest.status == "approved"
            ).order_by(PluginAccessRequest.requested_at.desc())
        )
        access_request = request_result.scalar_one_or_none()
        
        if not access_request:
            raise ValueError("No approved access request found to revoke")
        
        # Get business_unit_id from the request
        bu_uuid = access_request.business_unit_id
        revoked_by_uuid = to_uuid(revoked_by_user_id)
        
        # Update access request to REVOKED
        access_request.status = "revoked"
        access_request.reviewed_at = datetime.now(timezone.utc)
        access_request.reviewed_by = revoked_by_uuid
        
        # Delete PluginAccess grant for this specific business unit
        access_result = await db.execute(
            select(PluginAccess).where(
                PluginAccess.plugin_id == plugin_id,
                PluginAccess.user_id == user_uuid,
                PluginAccess.business_unit_id == bu_uuid
            )
        )
        plugin_access = access_result.scalar_one_or_none()
        
        if plugin_access:
            await db.delete(plugin_access)
        else:
            # If no PluginAccess found, still commit the request status change
            logger.warning(f"PluginAccess not found for plugin_id={plugin_id}, user_id={user_id}, business_unit_id={bu_uuid}")
        
        await db.commit()
        
        # Send notification to the user
        plugin_name = plugin.name if plugin else plugin_id
        try:
            await send_notification(
                user_id=user_id,
                title="Access Revoked",
                message=f"Your access to plugin '{plugin_name}' has been revoked. You can request access again if needed.",
                notification_type="warning",
                link="/services"
            )
            logger.info(f"Revocation notification sent to user {user_id} for plugin {plugin_id}")
        except Exception as e:
            logger.error(f"Failed to send revocation notification to user {user_id}: {e}")
            # Don't fail the revoke operation if notification fails
    
    async def restore_plugin_access(
        self,
        plugin_id: str,
        user_id: str,
        restored_by_user_id: str,
        db: AsyncSession
    ):
        """Restore revoked plugin access"""
        user_uuid = to_uuid(user_id)
        restored_by_uuid = to_uuid(restored_by_user_id)
        
        if not user_uuid:
            raise ValueError("Invalid user ID")
        
        # Find revoked request
        result = await db.execute(
            select(PluginAccessRequest).where(
                PluginAccessRequest.plugin_id == plugin_id,
                PluginAccessRequest.user_id == user_uuid,
                PluginAccessRequest.status == "revoked"
            )
        )
        access_request = result.scalar_one_or_none()
        
        if not access_request:
            raise ValueError("Revoked access request not found")
        
        # Restore to APPROVED
        access_request.status = "approved"
        access_request.reviewed_at = datetime.now(timezone.utc)
        access_request.reviewed_by = restored_by_uuid
        
        # Recreate PluginAccess grant
        access_result = await db.execute(
            select(PluginAccess).where(
                PluginAccess.plugin_id == plugin_id,
                PluginAccess.user_id == user_uuid,
                PluginAccess.business_unit_id == access_request.business_unit_id
            )
        )
        plugin_access = access_result.scalar_one_or_none()
        
        if not plugin_access:
            plugin_access = PluginAccess(
                plugin_id=plugin_id,
                user_id=user_uuid,
                business_unit_id=access_request.business_unit_id,
                granted_by=restored_by_uuid
            )
            db.add(plugin_access)
        
        await db.commit()
    
    async def list_access_requests(
        self,
        plugin_id: Optional[str],
        status: Optional[str],
        search: Optional[str],
        user_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """List access requests (filtered by user role)"""
        
        # Check if user is admin
        is_admin = False
        bu_ids_owned = []
        
        if user_id:
            try:
                async with httpx.AsyncClient() as client:
                    # Check if user is admin
                    # Use HTTP port (8000) for REST API, not gRPC port (50051)
                    auth_url = os.environ.get("AUTH_SERVICE_HTTP_URL", "http://auth-service:8000")
                    if ":" in auth_url and not auth_url.startswith("http"):
                        auth_url = f"http://{auth_url}"
                    
                    response = await client.post(
                        f"{auth_url}/api/v1/permissions/check-service",
                        json={
                            "user_id": user_id,
                            "permission": "platform:plugins:upload",
                            "resource": "platform",
                            "resource_id": ""
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        is_admin = data.get("has_permission", False)
                    
                    # If not admin, check for BU ownership
                    if not is_admin:
                        # Get user's business units where they can manage members
                        bu_response = await client.get(
                            f"{auth_url}/api/v1/business-units?user_id={user_id}"
                        )
                        if bu_response.status_code == 200:
                            business_units = bu_response.json()
                            for bu in business_units:
                                # Check if user can manage members in this BU
                                if bu.get("can_manage_members", False):
                                    bu_id = bu.get("id")
                                    if bu_id:
                                        bu_ids_owned.append(bu_id)
                                        logger.info(f"User {user_id} can manage BU: {bu_id}")
            except Exception as e:
                logger.error(f"Error checking user permissions: {e}")
        
        # Build query
        query = select(PluginAccessRequest)
        
        if plugin_id:
            query = query.where(PluginAccessRequest.plugin_id == plugin_id)
        
        if status:
            # Use lowercase string comparison
            query = query.where(PluginAccessRequest.status == status.lower())
        
        # Filter by business unit if user is a BU owner (not admin)
        if not is_admin and bu_ids_owned:
            # Convert string UUIDs to UUID objects
            bu_uuids = [to_uuid(bu_id) for bu_id in bu_ids_owned if to_uuid(bu_id)]
            if bu_uuids:
                # Only show requests from users in business units owned by this user
                query = query.where(
                    PluginAccessRequest.business_unit_id.in_(bu_uuids),
                    PluginAccessRequest.business_unit_id.isnot(None)
                )
        elif not is_admin:
            # User is not admin and doesn't own any BUs - return empty list
            return {"requests": [], "total": 0}
        
        # TODO: Add search functionality (would need User join)
        
        query = query.order_by(PluginAccessRequest.requested_at.desc())
        result = await db.execute(query)
        requests = result.scalars().all()
        
        # Enrich requests with user emails and plugin names
        enriched_requests = []
        for req in requests:
            request_dict = {
                "id": str(req.id),
                "plugin_id": req.plugin_id,
                "user_id": str(req.user_id),
                "business_unit_id": str(req.business_unit_id) if req.business_unit_id else "",
                "status": req.status,
                "note": req.note or "",
                "requested_at": req.requested_at.isoformat() if req.requested_at else "",
                "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else "",
                "reviewed_by": str(req.reviewed_by) if req.reviewed_by else "",
                "user_email": "",  # Will fetch from auth-service
                "user_name": "",
                "plugin_name": ""  # Will fetch from plugin table
            }
            
            # Get plugin name
            try:
                plugin_result = await db.execute(select(Plugin).where(Plugin.id == req.plugin_id))
                plugin = plugin_result.scalar_one_or_none()
                if plugin:
                    request_dict["plugin_name"] = plugin.name
            except Exception as e:
                logger.error(f"Error fetching plugin name: {e}")
            
            # Get user email from auth-service
            try:
                async with httpx.AsyncClient() as client:
                    auth_url = os.environ.get("AUTH_SERVICE_HTTP_URL", "http://auth-service:8000")
                    if ":" in auth_url and not auth_url.startswith("http"):
                        auth_url = f"http://{auth_url}"
                    user_response = await client.get(
                        f"{auth_url}/api/v1/users/{req.user_id}",
                        timeout=5.0
                    )
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        request_dict["user_email"] = user_data.get("email", "")
                        # Construct user name from email
                        email = user_data.get("email", "")
                        if email:
                            name_part = email.split('@')[0]
                            request_dict["user_name"] = name_part.replace('.', ' ').title()
            except Exception as e:
                logger.error(f"Error fetching user email: {e}")
            
            enriched_requests.append(request_dict)
        
        return {
            "requests": enriched_requests,
            "total": len(enriched_requests)
        }
    
    async def list_access_grants(
        self,
        plugin_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """List access grants"""
        query = select(PluginAccess)
        
        if plugin_id:
            query = query.where(PluginAccess.plugin_id == plugin_id)
        
        result = await db.execute(query)
        grants = result.scalars().all()
        
        return {
            "grants": [{
                "id": grant.id,
                "plugin_id": grant.plugin_id,
                "user_id": grant.user_id,
                "business_unit_id": grant.business_unit_id or "",
                "granted_by": grant.granted_by,
                "granted_at": grant.granted_at.isoformat() if grant.granted_at else ""
            } for grant in grants],
            "total": len(grants)
        }


# Singleton instance
plugin_service = PluginService()
