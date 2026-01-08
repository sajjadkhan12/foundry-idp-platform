"""
REST to gRPC adapter for worker microservice
This provides REST API endpoints for all worker service functionality
"""
import logging
# Configure logging to reduce verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from fastapi import FastAPI, HTTPException, Depends, Query, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import grpc
import json

from app.config import settings
from app.grpc.worker_servicer import WorkerServicer

# Import generated proto modules
try:
    from proto import worker_pb2, worker_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    worker_pb2 = None
    worker_pb2_grpc = None

app = FastAPI(title="Worker Service REST API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ProvisionInfrastructureRequest(BaseModel):
    job_id: str
    plugin_id: str
    version: str
    inputs: dict
    credential_name: Optional[str] = None
    deployment_id: Optional[str] = None


class ProvisionMicroserviceRequest(BaseModel):
    job_id: str
    plugin_id: str
    version: str
    deployment_name: str
    user_id: str
    deployment_id: Optional[str] = None
    inputs: Optional[dict] = None


# Create servicer instance
worker_servicer = WorkerServicer()


class MockContext:
    """Mock gRPC context for REST adapter"""
    def __init__(self):
        self.code = None
        self.details = None
    
    def set_code(self, code):
        self.code = code
    
    def set_details(self, details):
        self.details = details


# ==================== Provision Endpoints ====================

@app.post("/api/v1/provision/infrastructure", status_code=202)
async def provision_infrastructure(request: ProvisionInfrastructureRequest):
    """Provision infrastructure"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = worker_pb2.ProvisionInfrastructureRequest(
        job_id=request.job_id,
        plugin_id=request.plugin_id,
        version=request.version,
        inputs=json.dumps(request.inputs),
        credential_name=request.credential_name or "",
        deployment_id=request.deployment_id or ""
    )
    response = await worker_servicer.ProvisionInfrastructure(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to provision infrastructure")
    
    return {
        "success": response.success,
        "message": response.message,
        "task_id": response.task_id,
        "error": response.error
    }


@app.post("/api/v1/provision/microservice", status_code=202)
async def provision_microservice(request: ProvisionMicroserviceRequest):
    """Provision microservice"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = worker_pb2.ProvisionMicroserviceRequest(
        job_id=request.job_id,
        plugin_id=request.plugin_id,
        version=request.version,
        deployment_name=request.deployment_name,
        user_id=request.user_id,
        deployment_id=request.deployment_id or "",
        inputs=json.dumps(request.inputs or {})
    )
    response = await worker_servicer.ProvisionMicroservice(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to provision microservice")
    
    return {
        "success": response.success,
        "message": response.message,
        "task_id": response.task_id,
        "error": response.error
    }


@app.post("/api/v1/provision/destroy/{deployment_id}", status_code=202)
async def destroy_infrastructure(deployment_id: str):
    """Destroy infrastructure"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = worker_pb2.DestroyInfrastructureRequest(deployment_id=deployment_id)
    response = await worker_servicer.DestroyInfrastructure(grpc_request, context)
    
    if context.code:
        status_code = 400 if context.code.value == 3 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to destroy infrastructure")
    
    return {
        "success": response.success,
        "message": response.message,
        "task_id": response.task_id
    }


@app.get("/api/v1/provision/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = worker_pb2.GetTaskStatusRequest(task_id=task_id)
    response = await worker_servicer.GetTaskStatus(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Task not found")
    
    return {
        "status": response.status,
        "message": response.message,
        "error": response.error,
        "outputs": json.loads(response.outputs) if response.outputs else {}
    }


# ==================== GitHub Webhook Endpoint ====================

@app.post("/api/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None, alias="X-GitHub-Event"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """Process GitHub webhook"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Read request body
    body = await request.body()
    payload_json = body.decode('utf-8')
    
    context = MockContext()
    grpc_request = worker_pb2.ProcessGitHubWebhookRequest(
        event_type=x_github_event or "",
        payload=payload_json,
        signature=x_hub_signature_256 or "",
        payload_body=body
    )
    response = await worker_servicer.ProcessGitHubWebhook(grpc_request, context)
    
    if context.code:
        # Return 200 to prevent GitHub retries
        return JSONResponse(
            status_code=200,
            content={"success": False, "message": context.details or "Failed to process webhook"}
        )
    
    return {
        "success": response.success,
        "message": response.message,
        "deployment_updated": response.deployment_updated,
        "deployment_id": response.deployment_id
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "worker-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
