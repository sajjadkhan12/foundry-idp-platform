"""Deployment management gRPC servicer"""
import grpc
import json
import asyncio
from proto import deployment_pb2, deployment_pb2_grpc
from app.services.deployment_service import deployment_service
from app.audit_client import audit_client


class DeploymentServicer(deployment_pb2_grpc.DeploymentServiceServicer):
    """gRPC servicer for deployment management operations"""
    
    async def CreateDeployment(self, request, context):
        """Create deployment"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                inputs = json.loads(request.inputs) if request.inputs else {}
                deployment = await deployment_service.create_deployment(
                    request.name,
                    request.deployment_type,
                    request.plugin_id,
                    request.version,
                    request.environment,
                    request.user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    inputs,
                    request.cost_center if request.cost_center else None,
                    request.project_code if request.project_code else None,
                    db
                )
                
                # Log audit event (fire and forget)
                asyncio.create_task(audit_client.log_activity(
                    action="deployment.create",
                    user_id=request.user_id,
                    resource_type="deployment",
                    resource_id=deployment["id"],
                    resource_name=deployment["name"],
                    details={
                        "plugin_id": request.plugin_id,
                        "environment": request.environment,
                        "deployment_type": request.deployment_type
                    },
                    status="success",
                    business_unit_id=request.business_unit_id if request.business_unit_id else None
                ))
                
                return self._dict_to_deployment_response(deployment)
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.DeploymentResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.DeploymentResponse()
    
    async def GetDeployment(self, request, context):
        """Get deployment by ID"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                deployment = await deployment_service.get_deployment(
                    request.deployment_id,
                    request.include_tags,
                    request.include_history,
                    db
                )
                return self._dict_to_deployment_response(deployment, include_tags=request.include_tags)
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.DeploymentResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.DeploymentResponse()
    
    async def UpdateDeployment(self, request, context):
        """Update deployment"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                inputs = json.loads(request.inputs) if request.inputs else None
                deployment = await deployment_service.update_deployment(
                    request.deployment_id,
                    request.name if request.name else None,
                    request.environment if request.environment else None,
                    inputs,
                    request.cost_center if request.cost_center else None,
                    request.project_code if request.project_code else None,
                    request.status if request.status else None,
                    request.user_id if request.user_id else None,
                    db
                )
                
                # Log audit event (fire and forget)
                asyncio.create_task(audit_client.log_activity(
                    action="deployment.update",
                    user_id=request.user_id if request.user_id else None,
                    resource_type="deployment",
                    resource_id=deployment["id"],
                    resource_name=deployment["name"],
                    details={
                        "environment": deployment.get("environment"),
                        "status": deployment.get("status"),
                        "inputs_changed": inputs is not None
                    },
                    status="success",
                    business_unit_id=deployment.get("business_unit_id")
                ))
                
                return self._dict_to_deployment_response(deployment)
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.DeploymentResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.DeploymentResponse()
    
    async def DeleteDeployment(self, request, context):
        """Delete deployment"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await deployment_service.delete_deployment(
                    request.deployment_id,
                    request.user_email if request.user_email else "system",
                    db
                )
                
                # Log audit event (fire and forget)
                asyncio.create_task(audit_client.log_activity(
                    action="deployment.delete",
                    user_email=request.user_email if request.user_email else None,
                    resource_type="deployment",
                    resource_id=request.deployment_id,
                    details={
                        "job_id": result.get("job_id"),
                        "task_id": result.get("task_id")
                    },
                    status="success"
                ))
                
                # Return response with task_id and job_id
                return deployment_pb2.DeleteDeploymentResponse(
                    message=result.get("message", "Deployment deletion initiated"),
                    task_id=result.get("task_id", ""),
                    job_id=result.get("job_id", ""),
                    deployment_id=result.get("deployment_id", request.deployment_id),
                    status=result.get("status", "accepted")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.DeleteDeploymentResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.DeleteDeploymentResponse()
    
    async def ListDeployments(self, request, context):
        """List deployments"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await deployment_service.list_deployments(
                    request.search if request.search else None,
                    request.status if request.status else None,
                    request.cloud_provider if request.cloud_provider else None,
                    request.plugin_id if request.plugin_id else None,
                    request.environment if request.environment else None,
                    request.tags if request.tags else None,
                    request.user_id if request.user_id else None,
                    request.business_unit_id if request.business_unit_id else None,
                    request.skip if request.skip > 0 else 0,
                    request.limit if request.limit > 0 else 50,
                    db
                )
                return deployment_pb2.ListDeploymentsResponse(
                    deployments=[self._dict_to_deployment_response(d) for d in result["deployments"]],
                    total=result["total"],
                    skip=result["skip"],
                    limit=result["limit"]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.ListDeploymentsResponse()
    
    def _dict_to_deployment_response(self, deployment_dict: dict, include_tags: bool = True) -> deployment_pb2.DeploymentResponse:
        """Convert deployment dictionary to protobuf response"""
        response = deployment_pb2.DeploymentResponse(
            id=deployment_dict["id"],
            name=deployment_dict["name"],
            status=deployment_dict["status"],
            deployment_type=deployment_dict["deployment_type"],
            environment=deployment_dict["environment"],
            plugin_id=deployment_dict["plugin_id"],
            version=deployment_dict["version"],
            stack_name=deployment_dict.get("stack_name", ""),
            cloud_provider=deployment_dict.get("cloud_provider", ""),
            region=deployment_dict.get("region", ""),
            git_branch=deployment_dict.get("git_branch", ""),
            github_repo_url=deployment_dict.get("github_repo_url", ""),
            github_repo_name=deployment_dict.get("github_repo_name", ""),
            ci_cd_status=deployment_dict.get("ci_cd_status", ""),
            ci_cd_run_id=deployment_dict.get("ci_cd_run_id", 0),
            ci_cd_run_url=deployment_dict.get("ci_cd_run_url", ""),
            ci_cd_updated_at=deployment_dict.get("ci_cd_updated_at", ""),
            update_status=deployment_dict.get("update_status", ""),
            last_update_job_id=deployment_dict.get("last_update_job_id", ""),
            last_update_error=deployment_dict.get("last_update_error", ""),
            last_update_attempted_at=deployment_dict.get("last_update_attempted_at", ""),
            inputs=json.dumps(deployment_dict.get("inputs", {})) if isinstance(deployment_dict.get("inputs"), dict) else (deployment_dict.get("inputs", "{}")),
            outputs=json.dumps(deployment_dict.get("outputs", {})) if isinstance(deployment_dict.get("outputs"), dict) else (deployment_dict.get("outputs", "{}")),
            user_id=deployment_dict["user_id"],
            business_unit_id=deployment_dict.get("business_unit_id", ""),
            cost_center=deployment_dict.get("cost_center", ""),
            project_code=deployment_dict.get("project_code", ""),
            created_at=deployment_dict["created_at"],
            updated_at=deployment_dict["updated_at"],
            job_id=deployment_dict.get("job_id", "")
        )
        
        if include_tags and "tags" in deployment_dict:
            try:
                tags_list = deployment_dict["tags"] if isinstance(deployment_dict["tags"], list) else []
                response.tags.extend([
                    deployment_pb2.DeploymentTagResponse(
                        id=tag.get("id", ""),
                        deployment_id=tag.get("deployment_id", ""),
                        key=tag.get("key", ""),
                        value=tag.get("value", ""),
                        created_at=tag.get("created_at", "")
                    )
                    for tag in tags_list
                ])
            except Exception as e:
                # If tags can't be processed, just skip them
                pass
        
        return response
    
    async def GetDeploymentHistory(self, request, context):
        """Get deployment history"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await deployment_service.get_deployment_history(
                    request.deployment_id,
                    request.skip if request.skip > 0 else 0,
                    request.limit if request.limit > 0 else 50,
                    db
                )
                return deployment_pb2.ListDeploymentHistoryResponse(
                    history=[
                        deployment_pb2.DeploymentHistoryResponse(
                            id=h["id"],
                            deployment_id=h["deployment_id"],
                            version_number=h["version_number"],
                            inputs=h["inputs"],
                            outputs=h["outputs"],
                            status=h["status"],
                            job_id=h["job_id"] or "",
                            created_at=h["created_at"],
                            created_by=h["created_by"],
                            description=h["description"]
                        )
                        for h in result["history"]
                    ],
                    total=result["total"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.ListDeploymentHistoryResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.ListDeploymentHistoryResponse()
    
    async def GetDeploymentHistoryVersion(self, request, context):
        """Get specific deployment history version"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await deployment_service.get_deployment_history_version(
                    request.deployment_id,
                    request.version_number,
                    db
                )
                return deployment_pb2.DeploymentHistoryResponse(
                    id=result["id"],
                    deployment_id=result["deployment_id"],
                    version_number=result["version_number"],
                    inputs=result["inputs"],
                    outputs=result["outputs"],
                    status=result["status"],
                    job_id=result["job_id"] or "",
                    created_at=result["created_at"],
                    created_by=result["created_by"],
                    description=result["description"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.DeploymentHistoryResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.DeploymentHistoryResponse()
    
    async def AddDeploymentTag(self, request, context):
        """Add tag to deployment"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await deployment_service.add_deployment_tag(
                    request.deployment_id,
                    request.key,
                    request.value,
                    db
                )
                return deployment_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.Empty()
    
    async def RemoveDeploymentTag(self, request, context):
        """Remove tag from deployment"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await deployment_service.remove_deployment_tag(
                    request.deployment_id,
                    request.key,
                    db
                )
                return deployment_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.Empty()
    
    async def ListDeploymentTags(self, request, context):
        """List deployment tags"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                tags = await deployment_service.list_deployment_tags(
                    request.deployment_id,
                    db
                )
                return deployment_pb2.ListDeploymentTagsResponse(
                    tags=[
                        deployment_pb2.DeploymentTagResponse(
                            id=tag["id"],
                            deployment_id=tag["deployment_id"],
                            key=tag["key"],
                            value=tag["value"],
                            created_at=tag["created_at"]
                        )
                        for tag in tags
                    ]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.ListDeploymentTagsResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.ListDeploymentTagsResponse()
    
    async def UpdateCICDStatus(self, request, context):
        """Update CI/CD status"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await deployment_service.update_cicd_status(
                    request.deployment_id,
                    request.ci_cd_status,
                    request.ci_cd_run_id if request.ci_cd_run_id > 0 else None,
                    request.ci_cd_run_url if request.ci_cd_run_url else None,
                    db
                )
                return deployment_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.Empty()
    
    async def GetCICDStatus(self, request, context):
        """Get CI/CD status"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await deployment_service.get_cicd_status(
                    request.deployment_id,
                    db
                )
                return deployment_pb2.CICDStatusResponse(
                    ci_cd_status=result["ci_cd_status"],
                    ci_cd_run_id=result["ci_cd_run_id"],
                    ci_cd_run_url=result["ci_cd_run_url"],
                    ci_cd_updated_at=result["ci_cd_updated_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return deployment_pb2.CICDStatusResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.CICDStatusResponse()
    
    async def GetDeploymentStats(self, request, context):
        """Get deployment statistics"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await deployment_service.get_deployment_stats(
                    request.business_unit_id if request.business_unit_id else None,
                    request.user_id if request.user_id else None,
                    db
                )
                return deployment_pb2.DeploymentStatsResponse(
                    total=result["total"],
                    active=result["active"],
                    provisioning=result["provisioning"],
                    failed=result["failed"],
                    by_environment=result["by_environment"],
                    by_cloud_provider=result["by_cloud_provider"]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.DeploymentStatsResponse()
    
    async def GetDeploymentCosts(self, request, context):
        """Get deployment costs"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await deployment_service.get_deployment_costs(
                    request.deployment_id if request.deployment_id else None,
                    request.business_unit_id if request.business_unit_id else None,
                    request.start_date if request.start_date else None,
                    request.end_date if request.end_date else None,
                    db
                )
                cost_items = [
                    deployment_pb2.DeploymentCostItem(
                        deployment_id=item["deployment_id"],
                        deployment_name=item["deployment_name"],
                        cost=item["cost"],
                        period=item["period"]
                    )
                    for item in result["costs"]
                ]
                return deployment_pb2.DeploymentCostsResponse(
                    total_cost=result["total_cost"],
                    currency=result["currency"],
                    costs=cost_items
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return deployment_pb2.DeploymentCostsResponse()
