"""Plugin gRPC servicer"""
import grpc
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.plugin_service import plugin_service

try:
    from proto import plugin_pb2, plugin_pb2_grpc
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from proto import plugin_pb2, plugin_pb2_grpc


class PluginServicer(plugin_pb2_grpc.PluginServiceServicer):
    """gRPC servicer for plugin operations"""
    
    async def UploadPlugin(self, request, context):
        """Upload a plugin ZIP file"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.upload_plugin(
                    request.file_content,
                    request.filename,
                    request.git_repo_url if request.git_repo_url else None,
                    request.git_branch if request.git_branch else None,
                    request.user_id,
                    db
                )
                return plugin_pb2.PluginVersionResponse(
                    id=result["id"],
                    plugin_id=result["plugin_id"],
                    version=result["version"],
                    manifest=result["manifest"],
                    storage_path=result["storage_path"],
                    git_repo_url=result["git_repo_url"],
                    git_branch=result["git_branch"],
                    template_repo_url=result["template_repo_url"],
                    template_path=result["template_path"],
                    created_at=result["created_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return plugin_pb2.PluginVersionResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.PluginVersionResponse()
    
    async def UploadMicroserviceTemplate(self, request, context):
        """Create a microservice template"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.upload_microservice_template(
                    request.plugin_id,
                    request.name,
                    request.version,
                    request.description,
                    request.template_repo_url,
                    request.template_path,
                    request.author if request.author else None,
                    request.user_id,
                    db
                )
                return plugin_pb2.PluginVersionResponse(
                    id=result["id"],
                    plugin_id=result["plugin_id"],
                    version=result["version"],
                    manifest=result["manifest"],
                    storage_path=result["storage_path"],
                    git_repo_url=result["git_repo_url"],
                    git_branch=result["git_branch"],
                    template_repo_url=result["template_repo_url"],
                    template_path=result["template_path"],
                    created_at=result["created_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return plugin_pb2.PluginVersionResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.PluginVersionResponse()
    
    async def ProvisionPlugin(self, request, context):
        """Create a provisioning job"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                inputs = json.loads(request.inputs) if request.inputs else {}
                tags = json.loads(request.tags) if request.tags else {}
                
                result = await plugin_service.provision_plugin(
                    request.plugin_id,
                    request.version,
                    inputs,
                    request.environment,
                    tags,
                    request.deployment_name if request.deployment_name else None,
                    request.cost_center if request.cost_center else None,
                    request.project_code if request.project_code else None,
                    request.user_id,
                    request.user_email if request.user_email else request.user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    request.organization_id if request.organization_id else None,
                    db
                )
                return plugin_pb2.ProvisionResponse(
                    job_id=result["job_id"],
                    deployment_id=result["deployment_id"],
                    status=result["status"],
                    message=result["message"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return plugin_pb2.ProvisionResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.ProvisionResponse()
    
    async def GetJob(self, request, context):
        """Get a job by ID"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.get_job(request.job_id, db)
                return plugin_pb2.JobResponse(
                    id=result["id"],
                    plugin_version_id=result["plugin_version_id"],
                    deployment_id=result["deployment_id"],
                    status=result["status"],
                    triggered_by=result["triggered_by"],
                    inputs=result["inputs"],
                    outputs=result["outputs"],
                    retry_count=result["retry_count"],
                    error_state=result["error_state"],
                    error_message=result["error_message"],
                    created_at=result["created_at"],
                    finished_at=result["finished_at"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.JobResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.JobResponse()
    
    async def ListJobs(self, request, context):
        """List jobs"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.list_jobs(
                    request.user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    request.skip,
                    request.limit,
                    request.status if request.status else None,
                    db
                )
                return plugin_pb2.ListJobsResponse(
                    jobs=[
                        plugin_pb2.JobResponse(
                            id=j["id"],
                            plugin_version_id=j["plugin_version_id"],
                            deployment_id=j["deployment_id"],
                            status=j["status"],
                            triggered_by=j["triggered_by"],
                            inputs=j["inputs"],
                            outputs=j["outputs"],
                            retry_count=j["retry_count"],
                            error_state=j["error_state"],
                            error_message=j["error_message"],
                            created_at=j["created_at"],
                            finished_at=j["finished_at"]
                        )
                        for j in result["jobs"]
                    ],
                    total=result["total"],
                    skip=result["skip"],
                    limit=result["limit"]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.ListJobsResponse()
    
    async def GetJobLogs(self, request, context):
        """Get job logs"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.get_job_logs(
                    request.job_id,
                    request.skip,
                    request.limit,
                    db
                )
                return plugin_pb2.JobLogsResponse(
                    logs=[
                        plugin_pb2.JobLogResponse(
                            id=log["id"],
                            job_id=log["job_id"],
                            timestamp=log["timestamp"],
                            level=log["level"],
                            message=log["message"]
                        )
                        for log in result["logs"]
                    ],
                    total=result["total"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.JobLogsResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.JobLogsResponse()
    
    async def CancelJob(self, request, context):
        """Cancel a job"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.cancel_job(request.job_id, request.user_id, db)
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    async def DeleteJob(self, request, context):
        """Delete a job"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.delete_job(request.job_id, request.user_id, db)
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    # ==================== Plugin CRUD Methods ====================
    
    async def ListPlugins(self, request, context):
        """List all plugins"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.list_plugins(
                    request.user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    db
                )
                return plugin_pb2.ListPluginsResponse(
                    plugins=[
                        plugin_pb2.PluginResponse(
                            id=p["id"],
                            name=p["name"],
                            description=p.get("description", ""),
                            author=p.get("author", ""),
                            is_locked=p["is_locked"],
                            deployment_type=p.get("deployment_type", "infrastructure"),
                            has_access=p.get("has_access", True),
                            has_pending_request=p.get("has_pending_request", False),
                            created_at=p.get("created_at", ""),
                            updated_at=p.get("updated_at", ""),
                            cloud_provider=p.get("cloud_provider", "other"),
                            category=p.get("category", "service"),
                            latest_version=p.get("latest_version", "0.0.0"),
                            versions=[
                                plugin_pb2.PluginVersionResponse(
                                    id=v["id"],
                                    plugin_id=v["plugin_id"],
                                    version=v["version"],
                                    manifest=v.get("manifest", "{}"),
                                    storage_path=v.get("storage_path", ""),
                                    git_repo_url=v.get("git_repo_url", ""),
                                    git_branch=v.get("git_branch", ""),
                                    template_repo_url=v.get("template_repo_url", ""),
                                    template_path=v.get("template_path", ""),
                                    created_at=v.get("created_at", "")
                                )
                                for v in p.get("versions", [])
                            ]
                        )
                        for p in result["plugins"]
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.ListPluginsResponse()
    
    async def GetPlugin(self, request, context):
        """Get plugin details"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.get_plugin(
                    request.plugin_id,
                    request.user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    db
                )
                return plugin_pb2.PluginResponse(
                    id=result["id"],
                    name=result["name"],
                    description=result.get("description", ""),
                    author=result.get("author", ""),
                    is_locked=result["is_locked"],
                    deployment_type=result.get("deployment_type", "infrastructure"),
                    has_access=result.get("has_access", True),
                    has_pending_request=result.get("has_pending_request", False),
                    created_at=result.get("created_at", ""),
                    updated_at=result.get("updated_at", ""),
                    git_repo_url=result.get("git_repo_url", "") or "",
                    git_branch=result.get("git_branch", "") or "",
                    versions=[
                        plugin_pb2.PluginVersionResponse(
                            id=v["id"],
                            plugin_id=v["plugin_id"],
                            version=v["version"],
                            manifest=v.get("manifest", "{}"),
                            storage_path=v.get("storage_path", ""),
                            git_repo_url=v.get("git_repo_url", ""),
                            git_branch=v.get("git_branch", ""),
                            template_repo_url=v.get("template_repo_url", ""),
                            template_path=v.get("template_path", ""),
                            created_at=v.get("created_at", "")
                        )
                        for v in result.get("versions", [])
                    ]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.PluginResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.PluginResponse()
    
    async def DeletePlugin(self, request, context):
        """Delete a plugin"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.delete_plugin(request.plugin_id, request.user_id, db)
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    async def LockPlugin(self, request, context):
        """Lock a plugin"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.lock_plugin(request.plugin_id, request.user_id, db)
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    async def UnlockPlugin(self, request, context):
        """Unlock a plugin"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.unlock_plugin(request.plugin_id, request.user_id, db)
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    # ==================== Plugin Version Methods ====================
    
    async def ListPluginVersions(self, request, context):
        """List plugin versions"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.list_plugin_versions(request.plugin_id, db)
                return plugin_pb2.ListPluginVersionsResponse(
                    versions=[
                        plugin_pb2.PluginVersionResponse(
                            id=v["id"],
                            plugin_id=v["plugin_id"],
                            version=v["version"],
                            manifest=v.get("manifest", "{}"),
                            storage_path=v.get("storage_path", ""),
                            git_repo_url=v.get("git_repo_url", ""),
                            git_branch=v.get("git_branch", ""),
                            template_repo_url=v.get("template_repo_url", ""),
                            template_path=v.get("template_path", ""),
                            created_at=v.get("created_at", "")
                        )
                        for v in result["versions"]
                    ]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.ListPluginVersionsResponse()
    
    async def GetPluginVersion(self, request, context):
        """Get a specific plugin version"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.get_plugin_version(
                    request.plugin_id,
                    request.version,
                    db
                )
                return plugin_pb2.PluginVersionResponse(
                    id=result["id"],
                    plugin_id=result["plugin_id"],
                    version=result["version"],
                    manifest=result.get("manifest", "{}"),
                    storage_path=result.get("storage_path", ""),
                    git_repo_url=result.get("git_repo_url", ""),
                    git_branch=result.get("git_branch", ""),
                    template_repo_url=result.get("template_repo_url", ""),
                    template_path=result.get("template_path", ""),
                    created_at=result.get("created_at", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.PluginVersionResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.PluginVersionResponse()
    
    # ==================== Plugin Access Methods ====================
    
    async def RequestPluginAccess(self, request, context):
        """Request access to a plugin"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.request_plugin_access(
                    request.plugin_id,
                    request.user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    request.note if request.note else None,
                    db
                )
                return plugin_pb2.PluginAccessRequestResponse(
                    id=result["id"],
                    plugin_id=result["plugin_id"],
                    user_id=result["user_id"],
                    user_email=result.get("user_email", ""),
                    user_name=result.get("user_name", ""),
                    business_unit_id=result.get("business_unit_id", ""),
                    status=result["status"],
                    note=result.get("note", ""),
                    requested_at=result.get("requested_at", ""),
                    reviewed_at=result.get("reviewed_at", ""),
                    reviewed_by=result.get("reviewed_by", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return plugin_pb2.PluginAccessRequestResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.PluginAccessRequestResponse()
    
    async def GrantPluginAccess(self, request, context):
        """Grant plugin access"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.grant_plugin_access(
                    request.plugin_id,
                    request.user_id,
                    request.granted_by_user_id,
                    request.business_unit_id if request.business_unit_id else None,
                    db
                )
                return plugin_pb2.PluginAccessResponse(
                    id=str(result["id"]),
                    plugin_id=result["plugin_id"],
                    user_id=result["user_id"],
                    user_email=result.get("user_email", ""),
                    user_name=result.get("user_name", ""),
                    business_unit_id=result.get("business_unit_id", ""),
                    granted_by=result.get("granted_by", ""),
                    granted_at=result.get("granted_at", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return plugin_pb2.PluginAccessResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.PluginAccessResponse()
    
    async def RejectPluginAccess(self, request, context):
        """Reject plugin access request"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.reject_plugin_access(
                    request.plugin_id,
                    request.user_id,
                    request.rejected_by_user_id,
                    db
                )
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    async def RevokePluginAccess(self, request, context):
        """Revoke plugin access"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.revoke_plugin_access(
                    request.plugin_id,
                    request.user_id,
                    request.revoked_by_user_id,
                    db
                )
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    async def RestorePluginAccess(self, request, context):
        """Restore plugin access"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await plugin_service.restore_plugin_access(
                    request.plugin_id,
                    request.user_id,
                    request.restored_by_user_id,
                    db
                )
                return plugin_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return plugin_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.Empty()
    
    async def ListAccessRequests(self, request, context):
        """List access requests"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.list_access_requests(
                    request.plugin_id if request.plugin_id else None,
                    request.status if request.status else None,
                    request.search if request.search else None,
                    request.user_id if request.user_id else None,
                    db
                )
                return plugin_pb2.ListAccessRequestsResponse(
                    requests=[
                        plugin_pb2.PluginAccessRequestResponse(
                            id=req["id"],
                            plugin_id=req["plugin_id"],
                            user_id=req["user_id"],
                            user_email=req.get("user_email", ""),
                            user_name=req.get("user_name", ""),
                            business_unit_id=req.get("business_unit_id", ""),
                            status=req["status"],
                            note=req.get("note", ""),
                            requested_at=req.get("requested_at", ""),
                            reviewed_at=req.get("reviewed_at", ""),
                            reviewed_by=req.get("reviewed_by", "")
                        )
                        for req in result["requests"]
                    ],
                    total=result["total"]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.ListAccessRequestsResponse()
    
    async def ListAccessGrants(self, request, context):
        """List access grants"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await plugin_service.list_access_grants(
                    request.plugin_id if request.plugin_id else None,
                    db
                )
                return plugin_pb2.ListAccessGrantsResponse(
                    grants=[
                        plugin_pb2.PluginAccessResponse(
                            id=str(grant["id"]),
                            plugin_id=grant["plugin_id"],
                            user_id=grant["user_id"],
                            user_email=grant.get("user_email", ""),
                            user_name=grant.get("user_name", ""),
                            business_unit_id=grant.get("business_unit_id", ""),
                            granted_by=grant.get("granted_by", ""),
                            granted_at=grant.get("granted_at", "")
                        )
                        for grant in result["grants"]
                    ],
                    total=result["total"]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return plugin_pb2.ListAccessGrantsResponse()
