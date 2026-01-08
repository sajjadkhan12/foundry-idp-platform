from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
import grpc
import asyncio
from concurrent import futures
import uvicorn
import os
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import select, desc, func, or_
import uuid
import uuid
import logging
import httpx
from typing import Dict
from fastapi import Depends

from app.database import AsyncSessionLocal, init_db
from app.models.audit import AuditLog
from app.grpc.audit_servicer import AuditServicer
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
# Reduce verbosity for SQLAlchemy and uvicorn
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Import generated proto
try:
    from proto import audit_pb2, audit_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    audit_pb2 = None
    audit_pb2_grpc = None
    PROTO_AVAILABLE = False
    logger.warning("Proto files not found, gRPC will not be available")

# gRPC Server
grpc_server = None

async def start_grpc_server():
    global grpc_server
    if not PROTO_AVAILABLE:
        logger.warning("Proto files not found, skipping gRPC server start")
        return

    grpc_server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    audit_pb2_grpc.add_AuditServiceServicer_to_server(AuditServicer(), grpc_server)
    
    grpc_port = os.getenv("GRPC_PORT", "50057")
    listen_addr = f'[::]:{grpc_port}'
    grpc_server.add_insecure_port(listen_addr)
    logger.info(f"Starting gRPC server on {listen_addr}")
    await grpc_server.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing audit database...")
    await init_db()
    logger.info("Starting gRPC server...")
    await start_grpc_server()
    logger.info("Audit service ready!")
    yield
    # Shutdown
    if grpc_server:
        await grpc_server.stop(0)
        logger.info("gRPC server stopped")

app = FastAPI(title="Audit Service", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for REST API ---
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    business_unit_id: Optional[str] = None
    organization_id: Optional[str] = None
    service_name: Optional[str] = None
    correlation_id: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    user: Optional[dict] = None

class ListAuditLogsResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int

class CreateAuditLogRequest(BaseModel):
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    business_unit_id: Optional[str] = None
    organization_id: Optional[str] = None
    service_name: Optional[str] = None
    correlation_id: Optional[str] = None
    duration_ms: Optional[int] = None

    duration_ms: Optional[int] = None


async def verify_token(authorization: Optional[str] = Header(None)) -> Dict:
    """Validate token with auth-service"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://auth-service:8000/api/v1/auth/validate",
                json={"token": token},
                timeout=5.0
            )
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Auth service unavailable")


# --- REST Endpoints ---

@app.get("/api/v1/audit-logs", response_model=ListAuditLogsResponse)
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    status: Optional[str] = None,
    service_name: Optional[str] = None,
    business_unit_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_info: Dict = Depends(verify_token)
):
    """List audit logs with filtering and pagination"""
    async with AsyncSessionLocal() as db:
        query = select(AuditLog).order_by(desc(AuditLog.created_at))
        
        # Filters
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    AuditLog.action.ilike(search_pattern),
                    AuditLog.resource_type.ilike(search_pattern),
                    AuditLog.resource_name.ilike(search_pattern),
                    AuditLog.user_email.ilike(search_pattern),
                    AuditLog.user_name.ilike(search_pattern)
                )
            )
        if user_id:
            try:
                u_uuid = uuid.UUID(user_id)
                query = query.filter(AuditLog.user_id == u_uuid)
            except ValueError:
                pass
        if action:
            query = query.filter(AuditLog.action.ilike(f"%{action}%"))
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if status:
            query = query.filter(AuditLog.status == status)
        if service_name:
            query = query.filter(AuditLog.service_name == service_name)
        if business_unit_id:
            try:
                bu_uuid = uuid.UUID(business_unit_id)
                query = query.filter(AuditLog.business_unit_id == bu_uuid)
            except ValueError:
                pass
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
            
        # Get Total Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Execute query for items
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return {
            "items": [log.to_dict() for log in logs],
            "total": total
        }

@app.post("/api/v1/audit-logs", status_code=201)
async def create_audit_log(
    request: CreateAuditLogRequest,
    user_info: Dict = Depends(verify_token)
):
    """Create a new audit log entry"""
    async with AsyncSessionLocal() as db:
        try:
            audit_log = AuditLog(
                user_id=uuid.UUID(request.user_id) if request.user_id else None,
                user_email=request.user_email,
                user_name=request.user_name,
                action=request.action,
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                resource_name=request.resource_name,
                details=request.details or {},
                ip_address=request.ip_address,
                user_agent=request.user_agent,
                status=request.status,
                error_message=request.error_message,
                business_unit_id=uuid.UUID(request.business_unit_id) if request.business_unit_id else None,
                organization_id=uuid.UUID(request.organization_id) if request.organization_id else None,
                service_name=request.service_name,
                correlation_id=uuid.UUID(request.correlation_id) if request.correlation_id else None,
                duration_ms=request.duration_ms
            )
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)
            
            logger.info(f"Created audit log: {audit_log.action} by {audit_log.user_email or 'system'}")
            
            return {"id": str(audit_log.id), "success": True}
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/audit-logs/{log_id}")
async def get_audit_log(
    log_id: str,
    user_info: Dict = Depends(verify_token)
):
    """Get a single audit log by ID"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(AuditLog).where(AuditLog.id == uuid.UUID(log_id))
            )
            log = result.scalar_one_or_none()
            
            if not log:
                raise HTTPException(status_code=404, detail="Audit log not found")
            
            return log.to_dict()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid log ID format")

@app.get("/api/v1/audit-logs/stats/summary")

async def get_audit_stats(
    days: int = Query(7, ge=1, le=365),
    business_unit_id: Optional[str] = None,
    user_info: Dict = Depends(verify_token)
):
    """Get audit log statistics"""
    from datetime import timedelta
    
    async with AsyncSessionLocal() as db:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        base_query = select(AuditLog).where(AuditLog.created_at >= start_date)
        
        if business_unit_id:
            try:
                bu_uuid = uuid.UUID(business_unit_id)
                base_query = base_query.filter(AuditLog.business_unit_id == bu_uuid)
            except ValueError:
                pass
        
        # Total count
        count_result = await db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()
        
        # Count by status
        success_result = await db.execute(
            select(func.count()).select_from(
                base_query.filter(AuditLog.status == 'success').subquery()
            )
        )
        success_count = success_result.scalar_one()
        
        failure_result = await db.execute(
            select(func.count()).select_from(
                base_query.filter(AuditLog.status == 'failure').subquery()
            )
        )
        failure_count = failure_result.scalar_one()
        
        # Count by action (top 10)
        action_result = await db.execute(
            select(AuditLog.action, func.count(AuditLog.id).label('count'))
            .where(AuditLog.created_at >= start_date)
            .group_by(AuditLog.action)
            .order_by(desc('count'))
            .limit(10)
        )
        top_actions = [{"action": row[0], "count": row[1]} for row in action_result.all()]
        
        return {
            "period_days": days,
            "total": total,
            "success": success_count,
            "failure": failure_count,
            "top_actions": top_actions
        }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "audit-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
