"""Worker gRPC servicer"""
import grpc
import json
from app.services.worker_service import worker_service

try:
    from proto import worker_pb2, worker_pb2_grpc
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from proto import worker_pb2, worker_pb2_grpc


class WorkerServicer(worker_pb2_grpc.WorkerServiceServicer):
    """gRPC servicer for worker operations"""
    
    async def ProvisionInfrastructure(self, request, context):
        """Provision infrastructure"""
        try:
            inputs = json.loads(request.inputs) if request.inputs else {}
            result = await worker_service.provision_infrastructure(
                request.job_id,
                request.plugin_id,
                request.version,
                inputs,
                request.credential_name if request.credential_name else None,
                request.deployment_id if request.deployment_id else None
            )
            return worker_pb2.TaskResponse(
                success=result["success"],
                message=result["message"],
                task_id=result["task_id"],
                error=result["error"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskResponse(
                success=False,
                message="Failed to start task",
                task_id="",
                error=str(e)
            )
    
    async def DestroyInfrastructure(self, request, context):
        """Destroy infrastructure"""
        try:
            result = await worker_service.destroy_infrastructure(request.deployment_id)
            return worker_pb2.TaskResponse(
                success=result["success"],
                message=result["message"],
                task_id=result["task_id"],
                error=result["error"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskResponse(
                success=False,
                message="Failed to start task",
                task_id="",
                error=str(e)
            )
    
    async def ProvisionMicroservice(self, request, context):
        """Provision microservice"""
        try:
            inputs = json.loads(request.inputs) if request.inputs else {}
            result = await worker_service.provision_microservice(
                request.job_id,
                request.plugin_id,
                request.version,
                request.deployment_name,
                request.user_id,
                request.deployment_id if request.deployment_id else None,
                inputs
            )
            return worker_pb2.TaskResponse(
                success=result["success"],
                message=result["message"],
                task_id=result["task_id"],
                error=result["error"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskResponse(
                success=False,
                message="Failed to start task",
                task_id="",
                error=str(e)
            )
    
    async def DestroyMicroservice(self, request, context):
        """Destroy microservice"""
        try:
            result = await worker_service.destroy_microservice(request.deployment_id)
            return worker_pb2.TaskResponse(
                success=result["success"],
                message=result["message"],
                task_id=result["task_id"],
                error=result["error"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskResponse(
                success=False,
                message="Failed to start task",
                task_id="",
                error=str(e)
            )
    
    async def CleanupStuckDeployments(self, request, context):
        """Cleanup stuck deployments"""
        try:
            result = await worker_service.cleanup_stuck_deployments()
            return worker_pb2.TaskResponse(
                success=result["success"],
                message=result["message"],
                task_id=result["task_id"],
                error=result["error"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskResponse(
                success=False,
                message="Cleanup failed",
                task_id="",
                error=str(e)
            )
    
    async def CleanupExpiredRefreshTokens(self, request, context):
        """Cleanup expired refresh tokens"""
        try:
            result = await worker_service.cleanup_expired_refresh_tokens()
            return worker_pb2.TaskResponse(
                success=result["success"],
                message=result["message"],
                task_id=result["task_id"],
                error=result["error"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskResponse(
                success=False,
                message="Cleanup failed",
                task_id="",
                error=str(e)
            )
    
    async def PollGitHubActionsStatus(self, request, context):
        """Poll GitHub Actions status"""
        try:
            result = await worker_service.poll_github_actions_status()
            return worker_pb2.TaskResponse(
                success=result["success"],
                message=result["message"],
                task_id=result["task_id"],
                error=result["error"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskResponse(
                success=False,
                message="Polling failed",
                task_id="",
                error=str(e)
            )
    
    async def GetTaskStatus(self, request, context):
        """Get task status"""
        try:
            result = await worker_service.get_task_status(request.task_id)
            return worker_pb2.TaskStatusResponse(
                status=result["status"],
                message=result["message"],
                error=result["error"],
                outputs=result["outputs"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.TaskStatusResponse(
                status="failed",
                message="Failed to get status",
                error=str(e),
                outputs=""
            )
    
    async def ProcessGitHubWebhook(self, request, context):
        """Process GitHub webhook event"""
        try:
            result = await worker_service.process_github_webhook(
                request.event_type,
                request.payload,
                request.signature if request.signature else None,
                request.payload_body
            )
            return worker_pb2.ProcessGitHubWebhookResponse(
                success=result["success"],
                message=result["message"],
                deployment_updated=result["deployment_updated"],
                deployment_id=result["deployment_id"]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return worker_pb2.ProcessGitHubWebhookResponse(
                success=False,
                message=f"Error: {str(e)}",
                deployment_updated=False,
                deployment_id=""
            )
