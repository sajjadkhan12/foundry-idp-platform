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
        db: AsyncSession,
        token: Optional[str] = None
    ) -> Dict:
        """Create a new deployment"""
        # Extract metadata from inputs if provided
        cloud_provider = inputs.get("_cloud_provider")
        region = inputs.get("_region")
        
        # Handle business_unit_id - convert empty string to None, validate UUID if provided
        bu_id = None
        org_id = None
        
        if business_unit_id and business_unit_id.strip():
            try:
                bu_id = uuid.UUID(business_unit_id)
                # Get organization_id from business_unit
                from sqlalchemy import text
                bu_result = await db.execute(
                    text("SELECT organization_id FROM business_units WHERE id = :bu_id"),
                    {"bu_id": str(bu_id)}
                )
                bu_row = bu_result.fetchone()
                if bu_row:
                    org_id = bu_row[0]
            except ValueError:
                # Invalid UUID format, set to None
                bu_id = None
        
        # If organization_id not found from BU, get it from user
        if not org_id:
            from sqlalchemy import text
            user_result = await db.execute(
                text("SELECT organization_id FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            user_row = user_result.fetchone()
            if user_row:
                org_id = user_row[0]
        
        if not org_id:
            raise ValueError("Could not determine organization_id for deployment")
        
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
            organization_id=org_id,
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
        db: AsyncSession,
        token: Optional[str] = None
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
                        INSERT INTO jobs (id, plugin_version_id, deployment_id, organization_id, status, triggered_by, inputs, retry_count, created_at)
                        VALUES (:id, :plugin_version_id, :deployment_id, :organization_id, CAST(:status AS job_status_enum), :triggered_by, CAST(:inputs AS jsonb), 0, NOW())
                    """),
                    {
                        "id": job_id,
                        "plugin_version_id": plugin_version_id,
                        "deployment_id": str(deployment_id),
                        "organization_id": str(deployment.organization_id) if deployment.organization_id else None,
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
                    if deployment.deployment_type == "microservice":
                        # Microservice logic merged with infrastructure or removed as requested
                        worker_result = await worker_client.provision_infrastructure(
                            job_id=job_id,
                            plugin_id=deployment.plugin_id,
                            version=deployment.version,
                            inputs=inputs,
                            deployment_id=deployment_id
                        )
                    else:
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
                                SET status = CAST('failed' AS job_status_enum),
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
        db: AsyncSession,
        token: Optional[str] = None
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
            # Use nested transaction (savepoint) so failure doesn't abort the main transaction
            async with db.begin_nested():
                result = await db.execute(
                    text("""
                        UPDATE jobs 
                        SET status = CAST('failed' AS job_status_enum),
                            error_message = 'Deployment deletion requested - job cancelled'
                        WHERE deployment_id = :deployment_id 
                        AND status = CAST('pending' AS job_status_enum)
                        AND (inputs->>'action' IS NULL OR (inputs->>'action')::text != 'destroy')
                    """),
                    {"deployment_id": str(deployment_id)}
                )
                rows_updated = result.rowcount
                if rows_updated > 0:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Cancelled {rows_updated} pending provisioning job(s) for deployment {deployment_id}")
            # db.commit() is NOT needed for begin_nested(), it auto-commits the savepoint if no error
            await db.commit() # Commit the transaction including status change and job updates
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to cancel pending jobs: {e}, continuing with deletion")
            # Transaction is still valid due to begin_nested rollback
            # Just commit the status change
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
                        INSERT INTO jobs (id, plugin_version_id, deployment_id, organization_id, status, triggered_by, inputs, retry_count, created_at)
                        VALUES (:id, :plugin_version_id, :deployment_id, :organization_id, CAST(:status AS job_status_enum), :triggered_by, CAST(:inputs AS jsonb), 0, NOW())
                    """),
                    {
                        "id": job_id,
                        "plugin_version_id": plugin_version_id,
                        "deployment_id": str(deployment_id),
                        "organization_id": str(deployment.organization_id) if deployment.organization_id else None,
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
        
        # Trigger worker-service to destroy infrastructure using gRPC
        task_id = None
        try:
            from app.grpc.worker_client import worker_client
            if deployment.deployment_type == "microservice":
                # Microservice logic merged with infrastructure or removed as requested
                worker_result = await worker_client.destroy_infrastructure(str(deployment_id), job_id)
            else:
                worker_result = await worker_client.destroy_infrastructure(str(deployment_id), job_id)
            
            if worker_result["success"]:
                task_id = worker_result.get("task_id")
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to trigger infrastructure destruction: {worker_result['error']}")
                # If job was created, mark it as failed
                if job_id:
                    await db.execute(
                        text("UPDATE jobs SET status = CAST('failed' AS job_status_enum), error_message = :error WHERE id = :job_id"),
                        {"job_id": job_id, "error": worker_result["error"]}
                    )
                    await db.commit()
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
        organization_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = None
    ) -> Dict:
        """List deployments with filters - automatically filtered by organization if provided"""
        if db is None:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                return await self.list_deployments(
                    search, status_filter, cloud_provider, plugin_id, environment,
                    tags_filter, user_id, business_unit_id, organization_id, skip, limit, db
                )
        
        query = select(Deployment).options(selectinload(Deployment.tags), joinedload(Deployment.user))
        count_query = select(func.count(Deployment.id))
        
        # Apply filters
        filters = []
        
        # Filter by organization directly using organization_id
        if organization_id:
            try:
                org_uuid = uuid.UUID(organization_id)
                filters.append(Deployment.organization_id == org_uuid)
            except ValueError:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Invalid organization_id format: {organization_id}")
                pass
        
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
                Deployment.stack_name.ilike(f"%{search}%"),
                Deployment.region.ilike(f"%{search}%"),
                Deployment.cloud_provider.ilike(f"%{search}%"),
                Deployment.environment.ilike(f"%{search}%"),
                Deployment.github_repo_name.ilike(f"%{search}%")
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
                id=uuid.uuid4(),
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
        """Get deployment costs from deployment_costs table"""
        from app.models.deployment import DeploymentCost
        
        query = select(Deployment).where(Deployment.status != DeploymentStatus.DELETED.value)
        
        if deployment_id:
            query = query.where(Deployment.id == uuid.UUID(deployment_id))
        
        if business_unit_id:
            query = query.where(Deployment.business_unit_id == uuid.UUID(business_unit_id))
        
        result = await db.execute(query)
        deployments = result.scalars().all()
        
        costs = []
        total_cost = 0.0
        
        for deployment in deployments:
            # Use estimated_monthly_cost if available, otherwise query deployment_costs table
            est_cost = float(deployment.estimated_monthly_cost) if deployment.estimated_monthly_cost else 0.0
            total_cost += est_cost
            
            cost_item = {
                "deployment_id": str(deployment.id),
                "deployment_name": deployment.name,
                "cost": f"{est_cost:.2f}",
                "period": datetime.now(timezone.utc).strftime("%Y-%m")
            }
            costs.append(cost_item)
        
        return {
            "total_cost": f"{total_cost:.2f}",
            "currency": "USD",
            "costs": costs
        }
    
    async def get_cost_trend(
        self,
        months: int,
        organization_id: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """Get monthly cost trend from deployment_costs table"""
        from app.models.deployment import DeploymentCost
        from dateutil.relativedelta import relativedelta
        
        # Get the last N months
        now = datetime.now(timezone.utc)
        trend = []
        total = 0.0
        
        for i in range(months - 1, -1, -1):
            month_date = now - relativedelta(months=i)
            billing_month = month_date.strftime("%Y-%m")
            month_label = month_date.strftime("%b")
            
            # Query costs for this month
            result = await db.execute(
                text("""
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM deployment_costs
                    WHERE billing_month = :billing_month
                """),
                {"billing_month": billing_month}
            )
            row = result.fetchone()
            amount = float(row[0]) if row else 0.0
            
            # If no historical data, use estimated costs from deployments
            if amount == 0.0 and i == 0:
                # Current month - use sum of estimated costs
                est_result = await db.execute(
                    text("""
                        SELECT COALESCE(SUM(estimated_monthly_cost), 0)
                        FROM deployments
                        WHERE status != 'deleted'
                    """)
                )
                est_row = est_result.fetchone()
                amount = float(est_row[0]) if est_row and est_row[0] else 0.0
            
            total += amount
            trend.append({
                "month": month_label,
                "amount": amount,
                "projected": i == 0,  # Current month is considered projected
                "currency": "USD"
            })
        
        return {
            "trend": trend,
            "total": total,
            "currency": "USD"
        }
    
    async def get_costs_by_provider(
        self,
        organization_id: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """Get costs grouped by cloud provider"""
        # Aggregate estimated costs by provider
        result = await db.execute(
            text("""
                SELECT 
                    COALESCE(cloud_provider, 'unknown') as provider,
                    COALESCE(SUM(estimated_monthly_cost), 0) as total,
                    COUNT(*) as deployment_count
                FROM deployments
                WHERE status != 'deleted'
                GROUP BY cloud_provider
                ORDER BY total DESC
            """)
        )
        
        costs = []
        total = 0.0
        
        for row in result:
            provider = row[0] or "unknown"
            amount = float(row[1]) if row[1] else 0.0
            count = row[2]
            total += amount
            
            costs.append({
                "provider": provider.upper(),
                "amount": amount,
                "currency": "USD",
                "deployment_count": count
            })
        
        return {
            "costs": costs,
            "total": total,
            "currency": "USD"
        }
    
    async def estimate_pre_provision_cost(
        self,
        plugin_id: str,
        inputs: Dict,
        db: AsyncSession
    ) -> Dict:
        """Estimate cost before provisioning based on plugin and inputs"""
        # Get plugin metadata for pricing info
        result = await db.execute(
            text("""
                SELECT pv.manifest, p.name
                FROM plugin_versions pv
                JOIN plugins p ON pv.plugin_id = p.id
                WHERE p.id = :plugin_id
                ORDER BY pv.created_at DESC
                LIMIT 1
            """),
            {"plugin_id": plugin_id}
        )
        row = result.fetchone()
        
        if not row:
            return {
                "estimated_monthly_cost": 0.0,
                "currency": "USD",
                "period": "month",
                "breakdown": {},
                "note": "Plugin not found"
            }
        
        manifest = row[0] if row[0] else {}
        plugin_name = row[1]
        
        # Extract cloud provider and region from inputs or manifest
        cloud_provider = inputs.get("_cloud_provider") or manifest.get("cloud_provider", "unknown")
        region = inputs.get("region") or inputs.get("_region") or manifest.get("default_region", "us-central1")
        
        # Simple cost estimation based on common resource patterns
        # This is a placeholder - in production, integrate with Infracost or cloud pricing APIs
        estimated_cost = 0.0
        breakdown = {}
        
        # GCS Bucket estimation
        if "bucket" in plugin_id.lower() or "storage" in plugin_id.lower():
            storage_class = inputs.get("storage_class", "STANDARD")
            base_cost = {"STANDARD": 0.020, "NEARLINE": 0.010, "COLDLINE": 0.004, "ARCHIVE": 0.0012}.get(storage_class, 0.020)
            # Assume 100GB baseline
            estimated_cost = base_cost * 100
            breakdown["storage"] = estimated_cost
        
        # Compute instance estimation
        if "compute" in plugin_id.lower() or "vm" in plugin_id.lower() or "instance" in plugin_id.lower():
            machine_type = inputs.get("machine_type", "e2-micro")
            # Simplified GCP pricing (monthly)
            machine_costs = {
                "e2-micro": 6.11,
                "e2-small": 12.23,
                "e2-medium": 24.46,
                "n1-standard-1": 24.27,
                "n1-standard-2": 48.55,
                "n1-standard-4": 97.09,
                "n2-standard-2": 69.35,
                "n2-standard-4": 138.70,
            }
            estimated_cost = machine_costs.get(machine_type, 25.0)
            breakdown["compute"] = estimated_cost
        
        # Cloud SQL estimation
        if "sql" in plugin_id.lower() or "database" in plugin_id.lower():
            tier = inputs.get("tier", "db-f1-micro")
            tier_costs = {
                "db-f1-micro": 7.67,
                "db-g1-small": 25.55,
                "db-n1-standard-1": 51.10,
                "db-n1-standard-2": 102.20,
            }
            estimated_cost = tier_costs.get(tier, 25.0)
            breakdown["database"] = estimated_cost
        
        # Default fallback
        if estimated_cost == 0.0:
            estimated_cost = 10.0  # Default $10/month for unknown resources
            breakdown["base"] = estimated_cost
        
        return {
            "estimated_monthly_cost": round(estimated_cost, 2),
            "currency": "USD",
            "period": "month",
            "breakdown": breakdown,
            "region": region,
            "source": "estimate",
            "note": f"Estimated cost for {plugin_name} based on {cloud_provider} pricing"
        }
    
    async def update_deployment_cost(
        self,
        deployment_id: str,
        estimated_cost: float,
        breakdown: Optional[Dict],
        db: AsyncSession
    ) -> None:
        """Update the estimated cost for a deployment"""
        deployment = await db.get(Deployment, uuid.UUID(deployment_id))
        if deployment:
            deployment.estimated_monthly_cost = estimated_cost
            await db.commit()




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
        
        # NOTE: History entry is created by worker-service when update completes,
        # which update_deployment triggers above.
        
        response["rollback_from_version"] = version_number
        return response


    async def retry_deployment(
        self,
        deployment_id: str,
        user_id: str,
        user_email: str,
        db: AsyncSession
    ) -> Dict:
        """
        Retry a deployment: Creates a new job for the existing deployment and triggers provisioning.
        """
        try:
            deployment_uuid = uuid.UUID(deployment_id)
        except ValueError:
            raise ValueError("Invalid deployment ID format")
        
        # Verify deployment exists
        result = await db.execute(
            select(Deployment).options(joinedload(Deployment.user)).where(Deployment.id == deployment_uuid)
        )
        deployment = result.scalar_one_or_none()
        if not deployment:
            raise ValueError("Deployment not found")
        
        # Determine deployment type
        deployment_type = deployment.deployment_type
        
        # Get plugin version ID
        plugin_version_result = await db.execute(
            text("SELECT id FROM plugin_versions WHERE plugin_id = :plugin_id AND version = :version LIMIT 1"),
            {"plugin_id": deployment.plugin_id, "version": deployment.version}
        )
        plugin_version_row = plugin_version_result.fetchone()
        if not plugin_version_row:
             # Try to find ANY version if specific one is gone (fallback)
             plugin_version_result = await db.execute(
                text("SELECT id FROM plugin_versions WHERE plugin_id = :plugin_id LIMIT 1"),
                {"plugin_id": deployment.plugin_id}
             )
             plugin_version_row = plugin_version_result.fetchone()
             if not plugin_version_row:
                 raise ValueError(f"Plugin version metadata not found for {deployment.plugin_id}:{deployment.version}")
        
        plugin_version_id = plugin_version_row[0]
        
        # Parse inputs
        inputs = deployment.inputs
        if isinstance(inputs, str):
            try:
                inputs = json.loads(inputs)
            except:
                inputs = {}
        
        # Create new job
        job_id = str(uuid.uuid4())
        job_inputs = inputs.copy()
        if deployment.business_unit_id:
            job_inputs["_business_unit_id"] = str(deployment.business_unit_id)
        
        # Cast status to job_status_enum enum
        await db.execute(
            text("""
                INSERT INTO jobs (id, plugin_version_id, deployment_id, organization_id, status, triggered_by, inputs, retry_count, created_at)
                VALUES (:id, :plugin_version_id, :deployment_id, :organization_id, CAST(:status AS job_status_enum), :triggered_by, CAST(:inputs AS jsonb), 0, NOW())
            """),
            {
                "id": job_id,
                "plugin_version_id": plugin_version_id,
                "deployment_id": str(deployment_id),
                "organization_id": str(deployment.organization_id) if deployment.organization_id else None,
                "status": "pending",
                "triggered_by": user_email or user_id,
                "inputs": json.dumps(job_inputs)
            }
        )
        
        # Update deployment status
        deployment.status = DeploymentStatus.PROVISIONING.value
        deployment.last_update_job_id = job_id
        deployment.last_update_attempted_at = datetime.now(timezone.utc)
        deployment.last_update_error = None
        
        await db.commit()
        
        # Trigger worker
        from app.grpc.worker_client import worker_client
        
        worker_result = {"success": False, "error": "Unknown deployment type"}
        
        try:
            if deployment_type == "microservice":
                # Microservice logic merged with infrastructure or removed as requested
                # Fallback to standard infrastructure provisioning logic
                worker_result = await worker_client.provision_infrastructure(
                    job_id=job_id,
                    plugin_id=deployment.plugin_id,
                    version=deployment.version,
                    inputs=inputs,
                    deployment_id=deployment_id,
                    credential_name=None
                )
            else:
                # Infrastructure
                credential_name = None
                if deployment.cloud_provider:
                    credential_name = f"{deployment.cloud_provider.lower()}_default"
                    
                worker_result = await worker_client.provision_infrastructure(
                    job_id=job_id,
                    plugin_id=deployment.plugin_id,
                    version=deployment.version,
                    inputs=inputs,
                    credential_name=credential_name,
                    deployment_id=deployment_id
                )
            
            if not worker_result["success"]:
                 # Job failed to dispatch
                 await db.execute(
                    text("UPDATE jobs SET status = CAST('failed' AS job_status_enum), error_message = :error WHERE id = :job_id"),
                    {"job_id": job_id, "error": worker_result.get("error", "Failed to dispatch to worker")}
                 )
                 deployment.status = DeploymentStatus.FAILED.value
                 deployment.last_update_error = worker_result.get("error")
                 await db.commit()
                 raise RuntimeError(f"Worker service execution failed: {worker_result.get('error')}")
            
            return {
                "message": "Retry job created successfully",
                "job_id": job_id,
                "deployment_id": deployment_id,
                "task_id": worker_result.get("task_id", "")
            }
            
        except Exception as e:
            # If dispatch fails exception
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to dispatch retry job {job_id}: {e}", exc_info=True)
            
            await db.execute(
                text("UPDATE jobs SET status = CAST('failed' AS job_status_enum), error_message = :error WHERE id = :job_id"),
                {"job_id": job_id, "error": str(e)}
            )
            deployment.status = DeploymentStatus.FAILED.value
            deployment.last_update_error = str(e)
            await db.commit()
            raise


deployment_service = DeploymentService()
