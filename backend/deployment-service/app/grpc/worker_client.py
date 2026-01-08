"""gRPC client for worker-service communication"""
import grpc
from app.config import settings
from typing import Dict, Optional

try:
    from proto import worker_pb2, worker_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    worker_pb2 = None
    worker_pb2_grpc = None


class WorkerClient:
    """Client for communicating with worker-service via gRPC"""
    
    def __init__(self):
        self.service_url = settings.WORKER_SERVICE_URL
    
    async def provision_infrastructure(
        self,
        job_id: str,
        plugin_id: str,
        version: str,
        inputs: Dict,
        credential_name: Optional[str] = None,
        deployment_id: Optional[str] = None
    ) -> Dict:
        """
        Trigger infrastructure provisioning via worker-service
        
        Args:
            job_id: Job identifier
            plugin_id: Plugin UUID
            version: Plugin version string
            inputs: Input parameters for provisioning
            credential_name: Optional cloud credential name
            deployment_id: Optional deployment ID (for updates)
        
        Returns:
            Dict with keys: success, message, task_id, error
        """
        if not PROTO_AVAILABLE:
            raise RuntimeError("Worker proto files not available")
        
        import json
        
        # Create gRPC channel
        async with grpc.aio.insecure_channel(self.service_url) as channel:
            stub = worker_pb2_grpc.WorkerServiceStub(channel)
            
            # Prepare request
            request = worker_pb2.ProvisionInfrastructureRequest(
                job_id=job_id,
                plugin_id=plugin_id,
                version=version,
                inputs=json.dumps(inputs),
                credential_name=credential_name or "",
                deployment_id=deployment_id or ""
            )
            
            # Call service
            try:
                response = await stub.ProvisionInfrastructure(request)
                return {
                    "success": response.success,
                    "message": response.message,
                    "task_id": response.task_id,
                    "error": response.error
                }
            except grpc.RpcError as e:
                return {
                    "success": False,
                    "message": "Failed to communicate with worker service",
                    "task_id": "",
                    "error": str(e)
                }


# Global client instance
worker_client = WorkerClient()
