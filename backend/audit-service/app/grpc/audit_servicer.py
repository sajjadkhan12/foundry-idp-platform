import grpc
from google.protobuf import timestamp_pb2, struct_pb2
from sqlalchemy import select, desc, func
from app.database import AsyncSessionLocal
from app.models.audit import AuditLog
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import generated proto
try:
    from proto import audit_pb2, audit_pb2_grpc
except ImportError:
    audit_pb2 = None
    audit_pb2_grpc = None

class AuditServicer(audit_pb2_grpc.AuditServiceServicer):
    async def LogActivity(self, request, context):
        """Log an activity from another microservice"""
        try:
            # Convert details Struct to dict
            details_dict = {}
            if request.details:
                for key, value in request.details.fields.items():
                    if value.HasField("string_value"):
                        details_dict[key] = value.string_value
                    elif value.HasField("number_value"):
                        details_dict[key] = value.number_value
                    elif value.HasField("bool_value"):
                        details_dict[key] = value.bool_value
                    elif value.HasField("struct_value"):
                        # Nested struct - convert to dict
                        nested = {}
                        for nk, nv in value.struct_value.fields.items():
                            if nv.HasField("string_value"):
                                nested[nk] = nv.string_value
                            elif nv.HasField("number_value"):
                                nested[nk] = nv.number_value
                        details_dict[key] = nested
            
            # Parse optional UUIDs
            user_uuid = None
            if request.user_id:
                try:
                    user_uuid = uuid.UUID(request.user_id)
                except ValueError:
                    pass
            
            resource_id = request.resource_id if request.resource_id else None
            
            # Create audit log
            audit_log = AuditLog(
                user_id=user_uuid,
                user_email=details_dict.get("user_email"),
                user_name=details_dict.get("user_name"),
                action=request.action,
                resource_type=request.resource_type,
                resource_id=resource_id,
                resource_name=details_dict.get("resource_name"),
                details=details_dict,
                ip_address=request.ip_address,
                status=request.status or "success",
                service_name=details_dict.get("service_name"),
                business_unit_id=uuid.UUID(details_dict.get("business_unit_id")) if details_dict.get("business_unit_id") else None,
                organization_id=uuid.UUID(details_dict.get("organization_id")) if details_dict.get("organization_id") else None,
            )
            
            async with AsyncSessionLocal() as db:
                db.add(audit_log)
                await db.commit()
                await db.refresh(audit_log)
            
            logger.info(f"Logged activity: {audit_log.action} for resource {audit_log.resource_type}/{audit_log.resource_id}")
                
            return audit_pb2.LogActivityResponse(
                success=True,
                id=str(audit_log.id)
            )
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return audit_pb2.LogActivityResponse(success=False, id="")

    async def ListAuditLogs(self, request, context):
        """List audit logs with filtering"""
        try:
            async with AsyncSessionLocal() as db:
                query = select(AuditLog).order_by(desc(AuditLog.created_at))
                
                # Filters
                if request.user_id:
                    try:
                        query = query.filter(AuditLog.user_id == uuid.UUID(request.user_id))
                    except ValueError:
                        pass
                if request.action:
                    query = query.filter(AuditLog.action.ilike(f"%{request.action}%"))
                if request.resource_type:
                    query = query.filter(AuditLog.resource_type == request.resource_type)
                if request.status:
                    query = query.filter(AuditLog.status == request.status)
                if request.search:
                    search_pattern = f"%{request.search}%"
                    from sqlalchemy import or_
                    query = query.filter(
                        or_(
                            AuditLog.action.ilike(search_pattern),
                            AuditLog.resource_type.ilike(search_pattern),
                            AuditLog.user_email.ilike(search_pattern)
                        )
                    )
                
                # Get total count
                count_query = select(func.count()).select_from(query.subquery())
                count_result = await db.execute(count_query)
                total = count_result.scalar_one()
                
                # Apply pagination
                query = query.offset(request.skip).limit(request.limit if request.limit > 0 else 50)
                result = await db.execute(query)
                logs = result.scalars().all()
                
                proto_logs = []
                for log in logs:
                    ts = timestamp_pb2.Timestamp()
                    if log.created_at:
                        ts.FromDatetime(log.created_at)
                    
                    # Convert details dict to Struct
                    details_struct = struct_pb2.Struct()
                    if log.details:
                        try:
                            details_struct.update(log.details)
                        except Exception:
                            pass
                        
                    proto_logs.append(audit_pb2.AuditLog(
                        id=str(log.id),
                        user_id=str(log.user_id) if log.user_id else "",
                        action=log.action,
                        resource_type=log.resource_type or "",
                        resource_id=log.resource_id or "",
                        details=details_struct,
                        ip_address=log.ip_address or "",
                        status=log.status or "success",
                        created_at=ts
                    ))
                
                return audit_pb2.ListAuditLogsResponse(
                    items=proto_logs,
                    total=total
                )
        except Exception as e:
            logger.error(f"Error listing audit logs: {e}")
            return audit_pb2.ListAuditLogsResponse(items=[], total=0)
