"""
REST to gRPC adapter for deployment microservice
This provides REST API endpoints for all deployment service functionality
"""
import logging
# Configure logging to reduce verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from fastapi import FastAPI, HTTPException, Depends, Query, Header, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import grpc
import json

from app.config import settings
from app.grpc.deployment_servicer import DeploymentServicer
from app.services.deployment_service import deployment_service

# Import generated proto modules
try:
    from proto import deployment_pb2, deployment_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    deployment_pb2 = None
    deployment_pb2_grpc = None

app = FastAPI(title="Deployment Service REST API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Helper functions for authentication
def _get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header"""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None


async def _get_user_info_from_token(token: Optional[str]) -> Optional[Dict]:
    """Extract user info from token by calling auth-service"""
    if not token:
        return None
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://auth-service:8000/api/v1/auth/validate",
                json={"token": token},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user_id")
                
                # Fetch full user details to get is_admin
                user_response = await client.get(
                    f"http://auth-service:8000/api/v1/users/{user_id}",
                    timeout=5.0
                )
                if user_response.status_code == 200:
                    user_details = user_response.json()
                    return {
                        "user_id": user_id,
                        "email": user_details.get("email"),
                        "is_admin": user_details.get("is_admin", False),
                        "active_business_unit_id": user_details.get("active_business_unit_id")
                    }
                
                return {
                    "user_id": user_id,
                    "email": data.get("email"),
                    "is_admin": False,
                    "active_business_unit_id": None
                }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to get user info from token: {e}")
    return None


async def verify_token(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Dependency to verify token and return user info.
    Raises HTTPException(401) if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
    user_info = await _get_user_info_from_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    return user_info


# Request/Response models
class CreateDeploymentRequest(BaseModel):
    name: str
    deployment_type: str
    plugin_id: str
    version: str
    environment: str
    user_id: str
    business_unit_id: Optional[str] = None
    inputs: Dict = {}
    cost_center: Optional[str] = None
    project_code: Optional[str] = None


class UpdateDeploymentRequest(BaseModel):
    name: Optional[str] = None
    environment: Optional[str] = None
    inputs: Optional[Dict] = None
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    status: Optional[str] = None


class AddDeploymentTagRequest(BaseModel):
    key: str
    value: str


class UpdateCICDStatusRequest(BaseModel):
    ci_cd_status: str
    ci_cd_run_id: Optional[int] = None
    ci_cd_run_url: Optional[str] = None


# Create servicer instance
deployment_servicer = DeploymentServicer()


class MockContext:
    """Mock gRPC context for REST adapter"""
    def __init__(self):
        self.code = None
        self.details = None
    
    def set_code(self, code):
        self.code = code
    
    def set_details(self, details):
        self.details = details


# ==================== Deployment CRUD Endpoints ====================

@app.post("/api/v1/deployments", status_code=201)
async def create_deployment(request: CreateDeploymentRequest):
    """Create deployment"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    # Convert inputs dict to JSON string for gRPC
    inputs_json = json.dumps(request.inputs) if isinstance(request.inputs, dict) else (request.inputs if isinstance(request.inputs, str) else "{}")
    
    # Handle business_unit_id - convert empty string to None
    business_unit_id = request.business_unit_id if request.business_unit_id and request.business_unit_id.strip() else None
    
    grpc_request = deployment_pb2.CreateDeploymentRequest(
        name=request.name,
        deployment_type=request.deployment_type,
        plugin_id=request.plugin_id,
        version=request.version,
        environment=request.environment,
        user_id=request.user_id,
        business_unit_id=business_unit_id or "",
        inputs=inputs_json,
        cost_center=request.cost_center or "",
        project_code=request.project_code or ""
    )
    response = await deployment_servicer.CreateDeployment(grpc_request, context)
    
    if context.code:
        # Map gRPC status codes to HTTP status codes
        status_code = 500
        if context.code.value == 16:  # UNAUTHENTICATED
            status_code = 401
        elif context.code.value == 3:  # INVALID_ARGUMENT
            status_code = 400
        elif context.code.value == 5:  # NOT_FOUND
            status_code = 404
        elif context.code.value == 6:  # ALREADY_EXISTS
            status_code = 409
        elif context.code.value == 7:  # PERMISSION_DENIED
            status_code = 403
            
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to create deployment")
    
    return {
        "id": response.id,
        "name": response.name,
        "status": response.status,
        "deployment_type": response.deployment_type,
        "environment": response.environment,
        "plugin_id": response.plugin_id,
        "version": response.version,
        "inputs": json.loads(response.inputs) if response.inputs else {},
        "user_id": response.user_id,
        "business_unit_id": response.business_unit_id,
        "created_at": response.created_at,
        "updated_at": response.updated_at
    }


@app.get("/api/v1/deployments")
async def list_deployments(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    cloud_provider: Optional[str] = Query(None),
    plugin_id: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    user_info: Dict = Depends(verify_token)
):
    """List deployments"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # User info comes from dependency
    # Regular users can only see their own deployments
    # Admins can see all (None) or filter by user_id
    pass
    
    # Regular users can only see their own deployments
    # Admins can see all (None) or filter by user_id
    if user_info.get("is_admin"):
        actual_user_id = user_id
    else:
        actual_user_id = user_info.get("user_id")
    
    context = MockContext()
    grpc_request = deployment_pb2.ListDeploymentsRequest(
        search=search or "",
        status=status or "",
        cloud_provider=cloud_provider or "",
        plugin_id=plugin_id or "",
        environment=environment or "",
        tags=tags or "",
        user_id=actual_user_id or "",
        business_unit_id=business_unit_id or "",
        skip=skip,
        limit=limit
    )
    response = await deployment_servicer.ListDeployments(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to list deployments")
    
    # Return format matching monolith: {"items": [...], "total": ..., "skip": ..., "limit": ...}
    # Parse inputs/outputs from JSON strings to objects for frontend
    items = []
    for d in response.deployments:
        try:
            inputs_obj = json.loads(d.inputs) if d.inputs and isinstance(d.inputs, str) else (d.inputs if d.inputs else {})
        except (json.JSONDecodeError, TypeError):
            inputs_obj = {}
        
        try:
            outputs_obj = json.loads(d.outputs) if d.outputs and isinstance(d.outputs, str) else (d.outputs if d.outputs else {})
        except (json.JSONDecodeError, TypeError):
            outputs_obj = {}
        
        items.append({
            "id": d.id,
            "name": d.name,
            "status": d.status,
            "deployment_type": d.deployment_type,
            "environment": d.environment,
            "plugin_id": d.plugin_id,
            "version": d.version,
            "stack_name": d.stack_name or "",
            "cloud_provider": d.cloud_provider or "",
            "region": d.region or "",
            "git_branch": d.git_branch or "",
            "github_repo_url": d.github_repo_url or "",
            "github_repo_name": d.github_repo_name or "",
            "ci_cd_status": d.ci_cd_status or "",
            "ci_cd_run_id": d.ci_cd_run_id or 0,
            "ci_cd_run_url": d.ci_cd_run_url or "",
            "ci_cd_updated_at": d.ci_cd_updated_at or "",
            "update_status": d.update_status or "",
            "last_update_job_id": d.last_update_job_id or "",
            "last_update_error": d.last_update_error or "",
            "last_update_attempted_at": d.last_update_attempted_at or "",
            "inputs": inputs_obj,
            "outputs": outputs_obj,
            "user_id": d.user_id,
            "business_unit_id": d.business_unit_id or "",
            "cost_center": d.cost_center or "",
            "project_code": d.project_code or "",
            "created_at": d.created_at,
            "updated_at": d.updated_at,
            "tags": [{
                "id": t.id,
                "key": t.key,
                "value": t.value,
                "created_at": t.created_at
            } for t in d.tags]
        })
    
    return {
        "items": items,
        "total": response.total,
        "skip": response.skip,
        "limit": response.limit
    }


@app.get("/api/v1/deployments/{deployment_id}")
async def get_deployment(
    deployment_id: str,
    include_tags: bool = Query(True),
    include_history: bool = Query(False),
    user_info: Dict = Depends(verify_token)
):
    """Get deployment by ID"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetDeploymentRequest(
        deployment_id=deployment_id,
        include_tags=include_tags,
        include_history=include_history
    )
    response = await deployment_servicer.GetDeployment(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Deployment not found")
    
    return {
        "id": response.id,
        "name": response.name,
        "status": response.status,
        "deployment_type": response.deployment_type,
        "environment": response.environment,
        "plugin_id": response.plugin_id,
        "version": response.version,
        "stack_name": response.stack_name or "",
        "cloud_provider": response.cloud_provider or "",
        "region": response.region or "",
        "git_branch": response.git_branch or "",
        "github_repo_url": response.github_repo_url or "",
        "github_repo_name": response.github_repo_name or "",
        "inputs": json.loads(response.inputs) if response.inputs else {},
        "outputs": json.loads(response.outputs) if response.outputs else {},
        "user_id": response.user_id,
        "business_unit_id": response.business_unit_id,
        "ci_cd_status": response.ci_cd_status or "",
        "ci_cd_run_id": response.ci_cd_run_id or 0,
        "ci_cd_run_url": response.ci_cd_run_url or "",
        "ci_cd_updated_at": response.ci_cd_updated_at or "",
        "update_status": response.update_status or "",
        "last_update_job_id": response.last_update_job_id or "",
        "last_update_error": response.last_update_error or "",
        "last_update_attempted_at": response.last_update_attempted_at or "",
        "job_id": response.job_id or "",
        "cost_center": response.cost_center or "",
        "project_code": response.project_code or "",
        "created_at": response.created_at,
        "updated_at": response.updated_at,
        "tags": [{
            "id": t.id,
            "key": t.key,
            "value": t.value,
            "created_at": t.created_at
        } for t in response.tags] if include_tags else []
    }


@app.put("/api/v1/deployments/{deployment_id}")
async def update_deployment(
    deployment_id: str, 
    request: UpdateDeploymentRequest,
    user_info: Dict = Depends(verify_token)
):
    """Update deployment"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # User info comes from dependency now
    user_id = user_info.get("user_id", "")
    is_admin = user_info.get("is_admin", False)


    context = MockContext()
    grpc_request = deployment_pb2.UpdateDeploymentRequest(
        deployment_id=deployment_id,
        name=request.name or "",
        environment=request.environment or "",
        inputs=json.dumps(request.inputs) if request.inputs else "",
        cost_center=request.cost_center or "",
        project_code=request.project_code or "",
        status=request.status or "",
        user_id=user_id
    )
    response = await deployment_servicer.UpdateDeployment(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update deployment")
    
    return {
        "id": response.id,
        "name": response.name,
        "status": response.status,
        "inputs": json.loads(response.inputs) if response.inputs else {},
        "updated_at": response.updated_at
    }


@app.delete("/api/v1/deployments/{deployment_id}")
async def delete_deployment(
    deployment_id: str,
    user_info: Dict = Depends(verify_token)
):
    """Delete deployment"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Extract user email from token
    user_email = user_info.get("email")
    
    if not user_email:
        # Fallback if email not in token (should differ based on auth service version)
        # But verify_token guarantees user_info is present.
        raise HTTPException(status_code=401, detail="Authentication required (Email missing)")
    
    context = MockContext()
    grpc_request = deployment_pb2.DeleteDeploymentRequest(
        deployment_id=deployment_id,
        user_email=user_email
    )
    response = await deployment_servicer.DeleteDeployment(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to delete deployment")
    
    return {
        "message": response.message,
        "task_id": response.task_id,
        "job_id": response.job_id,
        "deployment_id": response.deployment_id,
        "status": response.status
    }


# ==================== Deployment History Endpoints ====================

@app.get("/api/v1/deployments/{deployment_id}/history")
async def get_deployment_history(
    deployment_id: str,
    skip: int = Query(0),
    limit: int = Query(50)
):
    """Get deployment history"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetDeploymentHistoryRequest(
        deployment_id=deployment_id,
        skip=skip,
        limit=limit
    )
    response = await deployment_servicer.GetDeploymentHistory(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to get history")
    
    return {
        "history": [{
            "id": h.id,
            "version_number": h.version_number,
            "inputs": json.loads(h.inputs) if h.inputs else {},
            "outputs": json.loads(h.outputs) if h.outputs else {},
            "status": h.status,
            "job_id": h.job_id,
            "created_at": h.created_at,
            "created_by": h.created_by,
            "description": h.description
        } for h in response.history],
        "total": response.total
    }


@app.get("/api/v1/deployments/{deployment_id}/history/{version_number}")
async def get_deployment_history_version(deployment_id: str, version_number: int):
    """Get specific deployment history version"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetDeploymentHistoryVersionRequest(
        deployment_id=deployment_id,
        version_number=version_number
    )
    response = await deployment_servicer.GetDeploymentHistoryVersion(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Version not found")
    
    return {
        "id": response.id,
        "version_number": response.version_number,
        "inputs": json.loads(response.inputs) if response.inputs else {},
        "outputs": json.loads(response.outputs) if response.outputs else {},
        "status": response.status,
        "job_id": response.job_id,
        "created_at": response.created_at,
        "created_by": response.created_by,
        "description": response.description
    }




@app.post("/api/v1/deployments/{deployment_id}/rollback/{version_number}")
async def rollback_deployment(
    deployment_id: str,
    version_number: int,
    user_info: Dict = Depends(verify_token)
):
    """Rollback deployment to a previous version"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Extract user ID from token
    user_id = user_info.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from app.database import AsyncSessionLocal
    import logging
    logger = logging.getLogger(__name__)
    
    async with AsyncSessionLocal() as db:
        try:
            result = await deployment_service.rollback_deployment(
                deployment_id,
                version_number,
                user_id,
                db
            )
            return result
        except ValueError as e:
            logger.warning(f"Rollback validation error: {str(e)}")
            # Check if it's a 400-level error (bad request) or 404 (not found)
            error_msg = str(e).lower()
            if "not found" in error_msg or "invalid" in error_msg:
                raise HTTPException(status_code=404, detail=str(e))
            else:
                raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            logger.error(f"Rollback runtime error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Rollback unexpected error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ==================== Deployment Tags Endpoints ====================

@app.post("/api/v1/deployments/{deployment_id}/tags")
async def add_deployment_tag(deployment_id: str, request: AddDeploymentTagRequest):
    """Add deployment tag"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.AddDeploymentTagRequest(
        deployment_id=deployment_id,
        key=request.key,
        value=request.value
    )
    await deployment_servicer.AddDeploymentTag(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to add tag")
    
    return {"message": "Tag added successfully"}


@app.delete("/api/v1/deployments/{deployment_id}/tags/{tag_key}")
async def remove_deployment_tag(deployment_id: str, tag_key: str):
    """Remove deployment tag"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.RemoveDeploymentTagRequest(
        deployment_id=deployment_id,
        key=tag_key
    )
    await deployment_servicer.RemoveDeploymentTag(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to remove tag")
    
    return {"message": "Tag removed successfully"}


@app.get("/api/v1/deployments/{deployment_id}/tags")
async def list_deployment_tags(deployment_id: str):
    """List deployment tags"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.ListDeploymentTagsRequest(deployment_id=deployment_id)
    response = await deployment_servicer.ListDeploymentTags(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to list tags")
    
    return {
        "tags": [{
            "id": t.id,
            "key": t.key,
            "value": t.value,
            "created_at": t.created_at
        } for t in response.tags]
    }


# ==================== CI/CD Status Endpoints ====================

@app.get("/api/v1/deployments/{deployment_id}/ci-cd-status")
async def get_cicd_status(deployment_id: str):
    """Get CI/CD status"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetCICDStatusRequest(deployment_id=deployment_id)
    response = await deployment_servicer.GetCICDStatus(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Deployment not found")
    
    return {
        "ci_cd_status": response.ci_cd_status,
        "ci_cd_run_id": response.ci_cd_run_id,
        "ci_cd_run_url": response.ci_cd_run_url,
        "ci_cd_updated_at": response.ci_cd_updated_at
    }


@app.put("/api/v1/deployments/{deployment_id}/ci-cd-status")
async def update_cicd_status(deployment_id: str, request: UpdateCICDStatusRequest):
    """Update CI/CD status"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.UpdateCICDStatusRequest(
        deployment_id=deployment_id,
        ci_cd_status=request.ci_cd_status,
        ci_cd_run_id=request.ci_cd_run_id or 0,
        ci_cd_run_url=request.ci_cd_run_url or ""
    )
    await deployment_servicer.UpdateCICDStatus(grpc_request, context)
    
    if context.code:
        status_code = 404 if context.code.value == 5 else 500
        raise HTTPException(status_code=status_code, detail=context.details or "Failed to update CI/CD status")
    
    return {"message": "CI/CD status updated successfully"}


# ==================== Deployment Stats Endpoints ====================

@app.get("/api/v1/deployments/stats/environments")
async def list_environments():
    """Get list of available environments"""
    from app.models.deployment import Environment
    return [
        {
            "name": env.value,
            "display": env.value.title(),
            "description": f"{env.value.title()} environment"
        }
        for env in Environment
    ]


@app.get("/api/v1/deployments/stats/by-environment")
async def deployment_stats_by_environment(
    user_id: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None)
):
    """Get deployment counts grouped by environment"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetDeploymentStatsRequest(
        user_id=user_id or "",
        business_unit_id=business_unit_id or ""
    )
    response = await deployment_servicer.GetDeploymentStats(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to get stats")
    
    # Parse by_environment JSON
    by_env = json.loads(response.by_environment) if response.by_environment else {}
    
    return [
        {"environment": env, "count": count}
        for env, count in by_env.items()
    ]


@app.get("/api/v1/deployments/stats/tags")
async def tag_usage_stats(
    limit: int = Query(20),
    user_id: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None)
):
    """Get most commonly used tags across all deployments"""
    # This would need a separate method or we can use list_deployments and aggregate
    # For now, return empty list - can be enhanced later
    return []


# ==================== Deployment Cost Endpoints ====================

@app.post("/api/v1/deployments/costs/estimate/pre-provision")
async def estimate_cost_pre_provision(
    plugin_id: str = Query(...),
    inputs: Dict = Body(...)
):
    """Estimate cost before provisioning (placeholder)"""
    # This would need integration with cost estimation services
    # For now, return placeholder
    return {
        "estimated_monthly_cost": 0.0,
        "currency": "USD",
        "period": "month",
        "breakdown": {},
        "note": "Cost estimation not yet implemented in deployment-service"
    }


@app.get("/api/v1/deployments/costs/estimate/{deployment_id}")
async def get_cost_estimate(deployment_id: str):
    """Get cost estimate for a deployment"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetDeploymentCostsRequest(deployment_id=deployment_id)
    response = await deployment_servicer.GetDeploymentCosts(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to get cost estimate")
    
    # Return first cost item or placeholder
    if response.costs:
        cost_item = response.costs[0]
        return {
            "estimated_monthly_cost": float(cost_item.cost),
            "currency": response.currency,
            "period": "month",
            "breakdown": {}
        }
    
    return {
        "estimated_monthly_cost": 0.0,
        "currency": response.currency,
        "period": "month",
        "breakdown": {}
    }


@app.get("/api/v1/deployments/costs/actual/{deployment_id}")
async def get_actual_costs(
    deployment_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get actual costs for a deployment (placeholder)"""
    # This would need integration with cloud provider billing APIs
    return {
        "total_cost": 0.0,
        "currency": "USD",
        "period": {
            "start": start_date or "",
            "end": end_date or ""
        },
        "breakdown": {},
        "note": "Actual cost retrieval not yet implemented in deployment-service"
    }


@app.get("/api/v1/deployments/costs/trend")
async def get_cost_trend(
    months: int = Query(6),
    business_unit_id: Optional[str] = Query(None)
):
    """Get monthly cost trend (placeholder)"""
    return {
        "trend": [],
        "total": 0.0,
        "currency": "USD"
    }


@app.get("/api/v1/deployments/costs/by-provider")
async def get_costs_by_provider(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None)
):
    """Get costs grouped by cloud provider"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetDeploymentCostsRequest(
        business_unit_id=business_unit_id or "",
        start_date=start_date or "",
        end_date=end_date or ""
    )
    response = await deployment_servicer.GetDeploymentCosts(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to get costs")
    
    # Group by provider (would need enhancement)
    return {
        "costs": [
            {
                "provider": "unknown",
                "amount": float(response.total_cost),
                "currency": response.currency,
                "deployment_count": len(response.costs)
            }
        ],
        "total": float(response.total_cost),
        "currency": response.currency
    }


@app.get("/api/v1/deployments/costs/aggregate")
async def get_aggregate_costs(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    business_unit_id: Optional[str] = Query(None)
):
    """Get aggregated costs with optional filters"""
    if not PROTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    context = MockContext()
    grpc_request = deployment_pb2.GetDeploymentCostsRequest(
        business_unit_id=business_unit_id or "",
        start_date=start_date or "",
        end_date=end_date or ""
    )
    response = await deployment_servicer.GetDeploymentCosts(grpc_request, context)
    
    if context.code:
        raise HTTPException(status_code=500, detail=context.details or "Failed to get aggregate costs")
    
    return {
        "total_cost": float(response.total_cost),
        "currency": response.currency,
        "period": {
            "start": start_date or "",
            "end": end_date or ""
        },
        "deployment_count": len(response.costs),
        "deployments": [
            {
                "id": item.deployment_id,
                "name": item.deployment_name,
                "cost": float(item.cost),
                "period": item.period
            }
            for item in response.costs
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "deployment-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
