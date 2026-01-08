"""Deployment service for managing deployments"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, text
from sqlalchemy.orm import selectinload, joinedload
from app.models.deployment import Deployment, DeploymentHistory, DeploymentTag, DeploymentStatus
from typing import Optional, Dict, List
import uuid
import json
from datetime import datetime, timezone

# Import PluginVersion model (from plugin-service schema, but accessible via shared DB)
# We'll use raw SQL to avoid import issues


class DeploymentService:
    """Service for deployment operations"""
    
    async def create_deployment(
        self,
        name: str,
        deployment_type: str,
        plugin_id: str,
        version: str,
        environment: str,
        user_id: str,
        business_unit_id: Optional[str],
        inputs: Dict,
        cost_center: Optional[str],
        project_code: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """Create a new deployment"""
        # Extract metadata from inputs if provided
        cloud_provider = inputs.get("_cloud_provider")
        region = inputs.get("_region")
        
        # Handle business_unit_id - convert empty string to None, validate UUID if provided
        bu_id = None
        if business_unit_id and business_unit_id.strip():
            try:
                bu_id = uuid.UUID(business_unit_id)
            except ValueError:
                # Invalid UUID format, set to None
                bu_id = None
        
        deployment = Deployment(
            id=uuid.uuid4(),
            name=name,
            status=DeploymentStatus.PROVISIONING.value,
            deployment_type=deployment_type,
            environment=environment,
            plugin_id=plugin_id,
            version=version,
            user_id=uuid.UUID(user_id),
            business_unit_id=bu_id,
            inputs=inputs,
            cloud_provider=cloud_provider,
            region=region,
            cost_center=cost_center,
            project_code=project_code
        )
        
        db.add(deployment)
        await db.commit()
        # Refresh is not needed - we can construct the dict from the deployment object
        # await db.refresh(deployment)  # Removed to avoid async issues
        
        return self._deployment_to_dict(deployment)
    
    async def get_deployment(
        self,
        deployment_id: str,
        include_tags: bool,
        include_history: bool,
        db: AsyncSession
    ) -> Dict:
        """Get deployment by ID"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        query = select(Deployment).options(selectinload(Deployment.user))
        if include_tags:
            query = query.options(selectinload(Deployment.tags))
        if include_history:
            query = query.options(selectinload(Deployment.history))
        
        result = await db.execute(
            query.where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        
        if not deployment:
            raise ValueError("Deployment not found")
        
        deployment_dict = self._deployment_to_dict(deployment, include_tags, include_history)
        
        # Get latest job for this deployment (like monolith does)
        try:
            # deployment_id is UUID in jobs table; cast parameter to uuid to avoid type mismatch
            job_result = await db.execute(
                text("""
                    SELECT id FROM jobs
                    WHERE deployment_id = CAST(:deployment_id AS uuid)
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"deployment_id": str(deployment_uuid)}
            )
            job_row = job_result.first()
            if job_row:
                deployment_dict["job_id"] = str(job_row[0])  # Ensure string
        except Exception as job_err:
            # If job lookup fails, just continue without job_id
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get job_id for deployment {deployment_id}: {job_err}")
        
        return deployment_dict
    
    async def update_deployment(
        self,
        deployment_id: str,
        name: Optional[str],
        environment: Optional[str],
        inputs: Optional[Dict],
        cost_center: Optional[str],
        project_code: Optional[str],
        status: Optional[str],
        user_id: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """
        Update a deployment
        
        If inputs change, triggers infrastructure update via worker-service.
        Otherwise, performs metadata-only update.
        """
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        
        if not deployment:
            raise ValueError("Deployment not found")
        
        # Check if inputs changed (infrastructure update required)
        inputs_changed = inputs is not None and inputs != deployment.inputs
        job_id = None
        task_id = None
        
        # Only allow updates for active deployments (matching monolith behavior)
        if inputs_changed and deployment.status != DeploymentStatus.ACTIVE.value:
            raise ValueError(f"Cannot update deployment with status '{deployment.status}'. Only active deployments can be updated.")
        
        # Check if an update is already in progress (matching monolith behavior)
        if inputs_changed and deployment.update_status == "updating":
            raise ValueError("An update is already in progress for this deployment. Please wait for it to complete.")
        
        if inputs_changed:
            # Infrastructure update required - trigger worker-service
            # Create job record
            job_id = str(uuid.uuid4())
            
            try:
                # Get plugin_version_id using raw SQL
                plugin_version_result = await db.execute(
                    text("""
                        SELECT id FROM plugin_versions 
                        WHERE plugin_id = :plugin_id AND version = :version
                        LIMIT 1
                    """),
                    {
                        "plugin_id": deployment.plugin_id,
                        "version": deployment.version
                    }
                )
                plugin_version_row = plugin_version_result.first()
                
                if not plugin_version_row:
                    raise ValueError(f"Plugin version not found: {deployment.plugin_id}@{deployment.version}")
                
                plugin_version_id = plugin_version_row[0]
                
                # Get user email from user_id for triggered_by field
                triggered_by_email = "system"
                if user_id:
                    try:
                        user_result = await db.execute(
                            text("""
                                SELECT email FROM users 
                                WHERE id = :user_id
                                LIMIT 1
                            """),
                            {"user_id": user_id}
                        )
                        user_row = user_result.first()
                        if user_row:
                            triggered_by_email = user_row[0]
                    except Exception as user_err:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Failed to get user email for user_id {user_id}: {user_err}")
                        # Fallback to user_id if email lookup fails
                        triggered_by_email = user_id
                
                # Create update job
                job_inputs = inputs.copy()
                if deployment.business_unit_id:
                    job_inputs["_business_unit_id"] = str(deployment.business_unit_id)
                
                await db.execute(
                    text("""
                        INSERT INTO jobs (id, plugin_version_id, deployment_id, status, triggered_by, inputs, retry_count, created_at)
                        VALUES (:id, :plugin_version_id, :deployment_id, CAST(:status AS jobstatus), :triggered_by, CAST(:inputs AS jsonb), 0, NOW())
                    """),
                    {
                        "id": job_id,
                        "plugin_version_id": plugin_version_id,
                        "deployment_id": str(deployment_id),
                        "status": "pending",
                        "triggered_by": triggered_by_email,
                        "inputs": json.dumps(job_inputs)
                    }
                )
                await db.commit()
                
                # Update deployment tracking fields (matching monolith behavior)
                # Keep status as ACTIVE, but set update_status to "updating"
                deployment.update_status = "updating"
                deployment.last_update_job_id = job_id
                deployment.last_update_error = None
                deployment.last_update_attempted_at = datetime.now(timezone.utc)
                # DO NOT change deployment.status - keep it as ACTIVE
                
                # NOTE: History entry is created by worker-service when update completes,
                # NOT here. This prevents duplicate history entries.
                
                # Call worker-service via gRPC
                from app.grpc.worker_client import worker_client
                
                try:
                    worker_result = await worker_client.provision_infrastructure(
                        job_id=job_id,
                        plugin_id=deployment.plugin_id,
                        version=deployment.version,
                        inputs=inputs,
                        deployment_id=deployment_id
                    )
                    
                    if worker_result["success"]:
                        task_id = worker_result["task_id"]
                    else:
                        # Worker call failed - reset update status on error
                        deployment.update_status = None
                        deployment.last_update_job_id = None
                        await db.commit()
                        # Update job status
                        await db.execute(
                            text("""
                                UPDATE jobs 
                                SET status = CAST('failed' AS jobstatus),
                                    error_message = :error
                                WHERE id = :job_id
                            """),
                            {
                                "job_id": job_id,
                                "error": worker_result.get("error", "Unknown error")
                            }
                        )
                        raise RuntimeError(f"Worker service failed: {worker_result.get('error')}")
                except Exception as worker_err:
                    # Reset update status on error
                    deployment.update_status = None
                    deployment.last_update_job_id = None
                    await db.commit()
                    raise
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to trigger infrastructure update: {e}", exc_info=True)
                # Reset update status on error
                if deployment:
                    deployment.update_status = None
                    deployment.last_update_job_id = None
                    await db.commit()
                raise RuntimeError(f"Failed to trigger infrastructure update: {str(e)}")
        
        # Update metadata fields (applies to both infrastructure updates and metadata-only updates)
        if name is not None:
            deployment.name = name
        if environment is not None:
            deployment.environment = environment
        if inputs is not None and not inputs_changed:
            # Only update inputs if they didn't change (avoiding race condition with worker)
            deployment.inputs = inputs
        if cost_center is not None:
            deployment.cost_center = cost_center
        if project_code is not None:
            deployment.project_code = project_code
        if status is not None and not inputs_changed:
            # Only allow status override if not triggering infrastructure update
            deployment.status = status
        
        await db.commit()
        
        # Re-fetch deployment with all relationships to ensure they're loaded for serialization
        # and to avoid lazy loading issues after commit
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one()
        
        # Return response
        response = self._deployment_to_dict(deployment)
        if inputs_changed:
            response["job_id"] = job_id
            response["task_id"] = task_id or ""
            response["message"] = "Deployment update initiated"
        
        return response
    
    async def delete_deployment(
        self,
        deployment_id: str,
        user_email: str,
        db: AsyncSession
    ) -> Dict:
        """Delete a deployment - marks as DELETING and triggers worker-service"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        
        if not deployment:
            raise ValueError("Deployment not found")
        
        # Check if already deleted or being deleted
        if deployment.status == DeploymentStatus.DELETED.value:
            raise ValueError("Deployment is already deleted")
        if deployment.status == DeploymentStatus.DELETING.value:
            raise ValueError("Deployment is already being deleted")
        
        # Mark as DELETING (worker will mark as DELETED after successful destruction)
        deployment.status = DeploymentStatus.DELETING.value
        
        # Cancel any pending provisioning jobs for this deployment
        try:
            result = await db.execute(
                text("""
                    UPDATE jobs 
                    SET status = CAST('failed' AS jobstatus),
                        error_message = 'Deployment deletion requested - job cancelled'
                    WHERE deployment_id = :deployment_id 
                    AND status = CAST('pending' AS jobstatus)
                    AND (inputs->>'action' IS NULL OR (inputs->>'action')::text != 'destroy')
                """),
                {"deployment_id": str(deployment_id)}
            )
            rows_updated = result.rowcount
            if rows_updated > 0:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Cancelled {rows_updated} pending provisioning job(s) for deployment {deployment_id}")
            await db.commit()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to cancel pending jobs: {e}, continuing with deletion")
            # Still commit the status change
            await db.commit()
        
        # Create deletion job (similar to monolith)
        # Get plugin version to create a deletion job - use raw SQL to avoid import issues
        job_id = None
        try:
            # Query plugin_version_id using raw SQL
            plugin_version_result = await db.execute(
                text("""
                    SELECT id FROM plugin_versions 
                    WHERE plugin_id = :plugin_id AND version = :version
                    LIMIT 1
                """),
                {
                    "plugin_id": deployment.plugin_id,
                    "version": deployment.version
                }
            )
            plugin_version_row = plugin_version_result.first()
            
            if plugin_version_row:
                plugin_version_id = plugin_version_row[0]
                # Create deletion job using raw SQL to properly cast enum
                job_id = str(uuid.uuid4())
                deletion_inputs = {
                    "action": "destroy",
                    "deployment_id": str(deployment_id),
                    "deployment_name": deployment.name
                }
                if deployment.business_unit_id:
                    deletion_inputs["_business_unit_id"] = str(deployment.business_unit_id)
                
                await db.execute(
                    text("""
                        INSERT INTO jobs (id, plugin_version_id, deployment_id, status, triggered_by, inputs, retry_count, created_at)
                        VALUES (:id, :plugin_version_id, :deployment_id, CAST(:status AS jobstatus), :triggered_by, CAST(:inputs AS jsonb), 0, NOW())
                    """),
                    {
                        "id": job_id,
                        "plugin_version_id": plugin_version_id,
                        "deployment_id": str(deployment_id),
                        "status": "pending",
                        "triggered_by": user_email,
                        "inputs": json.dumps(deletion_inputs)
                    }
                )
                await db.commit()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to create deletion job: {e}, continuing without job tracking")
        
        # Trigger worker-service to destroy infrastructure
        task_id = None
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                worker_response = await client.post(
                    f"http://worker-service:8000/api/v1/provision/destroy/{deployment_id}",
                    timeout=30.0
                )
                if worker_response.status_code == 202:
                    task_data = worker_response.json()
                    task_id = task_data.get("task_id")
                    # Use the job_id we created, not from worker response
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to trigger worker-service for deletion: {e}", exc_info=True)
            # Don't fail - worker might pick it up later
        
        return {
            "message": "Deployment deletion initiated",
            "task_id": task_id or "",
            "job_id": job_id or "",
            "deployment_id": deployment_id,
            "status": "accepted"
        }
    
    async def list_deployments(
        self,
        search: Optional[str],
        status_filter: Optional[str],
        cloud_provider: Optional[str],
        plugin_id: Optional[str],
        environment: Optional[str],
        tags_filter: Optional[str],
        user_id: Optional[str],
        business_unit_id: Optional[str],
        skip: int,
        limit: int,
        db: AsyncSession
    ) -> Dict:
        """List deployments with filters"""
        query = select(Deployment).options(selectinload(Deployment.tags), joinedload(Deployment.user))
        count_query = select(func.count(Deployment.id))
        
        # Apply filters
        filters = []
        
        if status_filter:
            filters.append(Deployment.status == status_filter)
        
        if cloud_provider:
            filters.append(Deployment.cloud_provider == cloud_provider)
        
        if plugin_id:
            filters.append(Deployment.plugin_id == plugin_id)
        
        if environment:
            filters.append(Deployment.environment == environment)
        
        if user_id:
            try:
                filters.append(Deployment.user_id == uuid.UUID(user_id))
            except ValueError:
                pass
        
        if business_unit_id:
            try:
                filters.append(Deployment.business_unit_id == uuid.UUID(business_unit_id))
            except ValueError:
                pass
        
        if search:
            search_filter = or_(
                Deployment.name.ilike(f"%{search}%"),
                Deployment.plugin_id.ilike(f"%{search}%"),
                Deployment.stack_name.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Deployment.created_at.desc())
        
        result = await db.execute(query)
        deployments = result.scalars().all()
        
        # Convert deployments to dicts - handle errors gracefully
        deployment_dicts = []
        for d in deployments:
            try:
                deployment_dicts.append(self._deployment_to_dict(d, include_tags=True))
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error converting deployment {d.id} to dict: {e}", exc_info=True)
                # Skip this deployment if conversion fails
                continue
        
        return {
            "deployments": deployment_dicts,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def _deployment_to_dict(
        self,
        deployment: Deployment,
        include_tags: bool = True,
        include_history: bool = False
    ) -> Dict:
        """Convert deployment model to dictionary"""
        result = {
            "id": str(deployment.id),
            "name": deployment.name,
            "status": deployment.status,
            "deployment_type": deployment.deployment_type,
            "environment": deployment.environment,
            "plugin_id": deployment.plugin_id,
            "version": deployment.version,
            "stack_name": deployment.stack_name or "",
            "cloud_provider": deployment.cloud_provider or "",
            "region": deployment.region or "",
            "git_branch": deployment.git_branch or "",
            "github_repo_url": deployment.github_repo_url or "",
            "github_repo_name": deployment.github_repo_name or "",
            "ci_cd_status": deployment.ci_cd_status or "",
            "ci_cd_run_id": deployment.ci_cd_run_id or 0,
            "ci_cd_run_url": deployment.ci_cd_run_url or "",
            "ci_cd_updated_at": deployment.ci_cd_updated_at.isoformat() if deployment.ci_cd_updated_at else "",
            "update_status": deployment.update_status or "",
            "last_update_job_id": deployment.last_update_job_id or "",
            "last_update_error": deployment.last_update_error or "",
            "last_update_attempted_at": deployment.last_update_attempted_at.isoformat() if deployment.last_update_attempted_at else "",
            "inputs": deployment.inputs if isinstance(deployment.inputs, dict) else (json.loads(deployment.inputs) if isinstance(deployment.inputs, str) else {}),
            "outputs": deployment.outputs if isinstance(deployment.outputs, dict) else (json.loads(deployment.outputs) if isinstance(deployment.outputs, str) and deployment.outputs else {}),
            "user_id": str(deployment.user_id),
            "business_unit_id": str(deployment.business_unit_id) if deployment.business_unit_id else "",
            "cost_center": deployment.cost_center or "",
            "project_code": deployment.project_code or "",
            "created_at": deployment.created_at.isoformat(),
            "updated_at": deployment.updated_at.isoformat(),
            "user_name": "Unknown User",
            "user_email": ""
        }
        
        # Safely access user info if loaded
        try:
            # Check if user is loaded without triggering a lazy load
            # In async SQLAlchemy, we should check if the attribute is in the __dict__
            # or if it was explicitly loaded.
            if 'user' in deployment.__dict__ and deployment.user:
                result["user_name"] = deployment.user.full_name or deployment.user.email or "Unknown User"
                result["user_email"] = deployment.user.email or ""
        except Exception:
            pass
        
        if include_tags:
            # Safely access tags - they might not be loaded
            try:
                tags_list = list(deployment.tags) if hasattr(deployment, 'tags') and deployment.tags else []
                result["tags"] = [
                    {
                        "id": str(tag.id),
                        "deployment_id": str(tag.deployment_id),
                        "key": tag.key,
                        "value": tag.value,
                        "created_at": tag.created_at.isoformat()
                    }
                    for tag in tags_list
                ]
            except Exception as e:
                # If tags can't be accessed, return empty list
                result["tags"] = []
        
        return result
    
    async def get_deployment_history(
        self,
        deployment_id: str,
        skip: int,
        limit: int,
        db: AsyncSession
    ) -> Dict:
        """Get deployment history"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        # Verify deployment exists
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        if not deployment:
            raise ValueError("Deployment not found")
        
        # Get history entries
        history_result = await db.execute(
            select(DeploymentHistory)
            .where(DeploymentHistory.deployment_id == deployment_uuid)
            .order_by(DeploymentHistory.version_number.desc())
            .offset(skip)
            .limit(limit)
        )
        history_entries = history_result.scalars().all()
        
        # Get total count
        count_result = await db.execute(
            select(func.count(DeploymentHistory.id))
            .where(DeploymentHistory.deployment_id == deployment_uuid)
        )
        total = count_result.scalar()
        
        return {
            "history": [
                {
                    "id": str(entry.id),
                    "deployment_id": str(entry.deployment_id),
                    "version_number": entry.version_number,
                    "inputs": json.dumps(entry.inputs) if isinstance(entry.inputs, dict) else entry.inputs,
                    "outputs": json.dumps(entry.outputs) if entry.outputs and isinstance(entry.outputs, dict) else (entry.outputs or "{}"),
                    "status": entry.status,
                    "job_id": entry.job_id,
                    "created_at": entry.created_at.isoformat() if entry.created_at else "",
                    "created_by": entry.created_by or "",
                    "description": entry.description or ""
                }
                for entry in history_entries
            ],
            "total": total
        }
    
    async def get_deployment_history_version(
        self,
        deployment_id: str,
        version_number: int,
        db: AsyncSession
    ) -> Dict:
        """Get specific deployment history version"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        result = await db.execute(
            select(DeploymentHistory).where(
                DeploymentHistory.deployment_id == deployment_uuid,
                DeploymentHistory.version_number == version_number
            )
        )
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise ValueError(f"Version {version_number} not found in deployment history")
        
        return {
            "id": str(entry.id),
            "deployment_id": str(entry.deployment_id),
            "version_number": entry.version_number,
            "inputs": json.dumps(entry.inputs) if isinstance(entry.inputs, dict) else entry.inputs,
            "outputs": json.dumps(entry.outputs) if entry.outputs and isinstance(entry.outputs, dict) else (entry.outputs or "{}"),
            "status": entry.status,
            "job_id": entry.job_id,
            "created_at": entry.created_at.isoformat() if entry.created_at else "",
            "created_by": entry.created_by or "",
            "description": entry.description or ""
        }
    
    async def add_deployment_tag(
        self,
        deployment_id: str,
        key: str,
        value: str,
        db: AsyncSession
    ) -> None:
        """Add or update a tag for a deployment"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        # Verify deployment exists
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        if not deployment:
            raise ValueError("Deployment not found")
        
        # Check if tag already exists
        existing_tag_result = await db.execute(
            select(DeploymentTag).where(
                DeploymentTag.deployment_id == deployment_uuid,
                DeploymentTag.key == key
            )
        )
        existing_tag = existing_tag_result.scalar_one_or_none()
        
        if existing_tag:
            # Update existing tag
            existing_tag.value = value
        else:
            # Create new tag
            new_tag = DeploymentTag(
                deployment_id=deployment_uuid,
                key=key,
                value=value
            )
            db.add(new_tag)
        
        await db.commit()
    
    async def remove_deployment_tag(
        self,
        deployment_id: str,
        key: str,
        db: AsyncSession
    ) -> None:
        """Remove a tag from a deployment"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        # Delete the tag
        from sqlalchemy import delete as sql_delete
        delete_result = await db.execute(
            sql_delete(DeploymentTag).where(
                DeploymentTag.deployment_id == deployment_uuid,
                DeploymentTag.key == key
            )
        )
        
        if delete_result.rowcount == 0:
            raise ValueError(f"Tag '{key}' not found on this deployment")
        
        await db.commit()
    
    async def list_deployment_tags(
        self,
        deployment_id: str,
        db: AsyncSession
    ) -> List[Dict]:
        """List all tags for a deployment"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        # Verify deployment exists
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        if not deployment:
            raise ValueError("Deployment not found")
        
        # Get tags
        tags_result = await db.execute(
            select(DeploymentTag).where(DeploymentTag.deployment_id == deployment_uuid)
        )
        tags = tags_result.scalars().all()
        
        return [
            {
                "id": str(tag.id),
                "deployment_id": str(tag.deployment_id),
                "key": tag.key,
                "value": tag.value,
                "created_at": tag.created_at.isoformat() if tag.created_at else ""
            }
            for tag in tags
        ]
    
    async def update_cicd_status(
        self,
        deployment_id: str,
        ci_cd_status: str,
        ci_cd_run_id: Optional[int],
        ci_cd_run_url: Optional[str],
        db: AsyncSession
    ) -> None:
        """Update CI/CD status for a deployment"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        
        if not deployment:
            raise ValueError("Deployment not found")
        
        deployment.ci_cd_status = ci_cd_status
        if ci_cd_run_id is not None:
            deployment.ci_cd_run_id = ci_cd_run_id
        if ci_cd_run_url:
            deployment.ci_cd_run_url = ci_cd_run_url
        deployment.ci_cd_updated_at = datetime.now(timezone.utc)
        
        await db.commit()
    
    async def get_cicd_status(
        self,
        deployment_id: str,
        db: AsyncSession
    ) -> Dict:
        """Get CI/CD status for a deployment"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user), selectinload(Deployment.tags)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        
        if not deployment:
            raise ValueError("Deployment not found")
        
        return {
            "ci_cd_status": deployment.ci_cd_status or "",
            "ci_cd_run_id": deployment.ci_cd_run_id or 0,
            "ci_cd_run_url": deployment.ci_cd_run_url or "",
            "ci_cd_updated_at": deployment.ci_cd_updated_at.isoformat() if deployment.ci_cd_updated_at else ""
        }
    
    async def get_deployment_stats(
        self,
        business_unit_id: Optional[str],
        user_id: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """Get deployment statistics"""
        from app.models.deployment import Environment
        
        # Build base query
        query = select(Deployment)
        
        # Apply filters
        if user_id:
            query = query.where(Deployment.user_id == uuid.UUID(user_id))
        
        if business_unit_id:
            query = query.where(Deployment.business_unit_id == uuid.UUID(business_unit_id))
        
        # Get all deployments
        result = await db.execute(query)
        deployments = result.scalars().all()
        
        # Calculate stats
        total = len(deployments)
        active = sum(1 for d in deployments if d.status == DeploymentStatus.ACTIVE.value)
        provisioning = sum(1 for d in deployments if d.status == DeploymentStatus.PROVISIONING.value)
        failed = sum(1 for d in deployments if d.status == DeploymentStatus.FAILED.value)
        
        # By environment
        by_environment = {}
        for env in Environment:
            count = sum(1 for d in deployments if d.environment == env.value)
            if count > 0:
                by_environment[env.value] = count
        
        # By cloud provider
        by_cloud_provider = {}
        for deployment in deployments:
            if deployment.cloud_provider:
                provider = deployment.cloud_provider.lower()
                by_cloud_provider[provider] = by_cloud_provider.get(provider, 0) + 1
        
        return {
            "total": total,
            "active": active,
            "provisioning": provisioning,
            "failed": failed,
            "by_environment": json.dumps(by_environment),
            "by_cloud_provider": json.dumps(by_cloud_provider)
        }
    
    async def get_deployment_costs(
        self,
        deployment_id: Optional[str],
        business_unit_id: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """Get deployment costs (placeholder - cost calculation would need external services)"""
        # This is a placeholder implementation
        # In production, this would call cost estimation services (GCP, AWS, etc.)
        
        query = select(Deployment).where(Deployment.status != DeploymentStatus.DELETED.value)
        
        if deployment_id:
            query = query.where(Deployment.id == uuid.UUID(deployment_id))
        
        if business_unit_id:
            query = query.where(Deployment.business_unit_id == uuid.UUID(business_unit_id))
        
        result = await db.execute(query)
        deployments = result.scalars().all()
        
        # Placeholder: return zero costs
        # In production, this would calculate actual costs from cloud provider APIs
        costs = []
        total_cost = 0.0
        
        for deployment in deployments:
            # Placeholder cost calculation
            cost_item = {
                "deployment_id": str(deployment.id),
                "deployment_name": deployment.name,
                "cost": "0.00",
                "period": datetime.now(timezone.utc).strftime("%Y-%m")
            }
            costs.append(cost_item)
        
        return {
            "total_cost": str(total_cost),
            "currency": "USD",
            "costs": costs
        }



    async def create_deployment_history_entry(
        self,
        deployment_id: str,
        inputs: Dict,
        outputs: Optional[Dict],
        status: str,
        job_id: Optional[str],
        created_by: str,
        description: str,
        db: AsyncSession
    ) -> Dict:
        """Create a deployment history entry for versioning"""
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        # Get current max version number
        result = await db.execute(
            select(func.max(DeploymentHistory.version_number))
            .where(DeploymentHistory.deployment_id == deployment_uuid)
        )
        max_version = result.scalar()
        next_version = (max_version or 0) + 1
        
        # Create history entry
        history = DeploymentHistory(
            id=uuid.uuid4(),
            deployment_id=deployment_uuid,
            version_number=next_version,
            inputs=inputs,
            outputs=outputs or {},
            status=status,
            job_id=job_id,
            created_by=created_by,
            description=description
        )
        
        db.add(history)
        await db.commit()
        
        return {
            "id": str(history.id),
            "deployment_id": str(history.deployment_id),
            "version_number": history.version_number,
            "inputs": history.inputs,
            "outputs": history.outputs,
            "status": history.status,
            "job_id": history.job_id,
            "created_at": history.created_at.isoformat(),
            "created_by": history.created_by,
            "description": history.description
        }
    
    async def rollback_deployment(
        self,
        deployment_id: str,
        version_number: int,
        user_id: str,
        db: AsyncSession
    ) -> Dict:
        """
        Rollback deployment to a previous version
        
        Fetches historical inputs and triggers infrastructure update.
        """
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        # Get the deployment first to check its status
        deployment_result = await db.execute(
            select(Deployment).where(Deployment.id == deployment_uuid)
        )
        deployment = deployment_result.scalar_one_or_none()
        
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        # Check if deployment is active (can only rollback active deployments)
        if deployment.status != DeploymentStatus.ACTIVE.value:
            raise ValueError(f"Cannot rollback deployment with status '{deployment.status}'. Only active deployments can be rolled back.")
        
        # Check if an update is already in progress
        if deployment.update_status == "updating":
            raise ValueError("An update is already in progress for this deployment. Please wait for it to complete.")
        
        # Get the historical version
        result = await db.execute(
            select(DeploymentHistory)
            .where(and_(
                DeploymentHistory.deployment_id == deployment_uuid,
                DeploymentHistory.version_number == version_number
            ))
        )
        history = result.scalar_one_or_none()
        
        if not history:
            raise ValueError(f"Version {version_number} not found for deployment {deployment_id}")
        
        # Validate that history has inputs
        if not history.inputs:
            raise ValueError(f"Version {version_number} has no inputs to rollback to")
        
        # Ensure inputs is a dict (not None)
        rollback_inputs = history.inputs.copy() if isinstance(history.inputs, dict) else {}
        if not rollback_inputs:
            raise ValueError(f"Version {version_number} has empty inputs")
        
        # Use update_deployment to apply the historical inputs
        # This will trigger the infrastructure update flow
        response = await self.update_deployment(
            deployment_id=deployment_id,
            name=None,
            environment=None,
            inputs=rollback_inputs,
            cost_center=None,
            project_code=None,
            status=None,
            user_id=user_id,
            db=db
        )
        
        # Create history entry for the rollback
        if response.get("job_id"):
            await self.create_deployment_history_entry(
                deployment_id=deployment_id,
                inputs=rollback_inputs,
                outputs=None,
                status="provisioning",
                job_id=response.get("job_id"),
                created_by=user_id,
                description=f"Rollback to version {version_number}",
                db=db
            )
        
        response["rollback_from_version"] = version_number
        return response


deployment_service = DeploymentService()
