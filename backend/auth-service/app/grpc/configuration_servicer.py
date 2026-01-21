"""Configuration management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.configuration_service import configuration_service


class ConfigurationServicer(auth_pb2_grpc.ConfigurationServiceServicer):
    """gRPC servicer for configuration management operations"""
    
    async def GetConfiguration(self, request, context):
        """Get configuration value"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                value = await configuration_service.get_config(
                    organization_id=request.organization_id,
                    config_key=request.config_key,
                    business_unit_id=request.business_unit_id if request.business_unit_id else None,
                    db=db
                )
                
                if value is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Configuration {request.config_key} not found")
                    return auth_pb2.ConfigurationResponse()
                
                return auth_pb2.ConfigurationResponse(
                    config_key=request.config_key,
                    config_value=value,
                    organization_id=request.organization_id,
                    business_unit_id=request.business_unit_id if request.business_unit_id else "",
                    is_active=True
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.ConfigurationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ConfigurationResponse()
    
    async def SetConfiguration(self, request, context):
        """Set configuration value"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await configuration_service.set_config(
                    organization_id=request.organization_id,
                    config_key=request.config_key,
                    config_value=request.config_value,
                    user_id=request.user_id,
                    business_unit_id=request.business_unit_id if request.business_unit_id else None,
                    db=db
                )
                
                return auth_pb2.ConfigurationResponse(
                    config_key=result["config_key"],
                    config_value=request.config_value,  # Return the value that was set
                    organization_id=result["organization_id"],
                    business_unit_id=result["business_unit_id"] or "",
                    is_active=result["is_active"]
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.ConfigurationResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ConfigurationResponse()
    
    async def ListConfigurations(self, request, context):
        """List all configurations"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                configs = await configuration_service.list_configs(
                    organization_id=request.organization_id,
                    business_unit_id=request.business_unit_id if request.business_unit_id else None,
                    db=db
                )
                
                return auth_pb2.ListConfigurationsResponse(
                    configurations=configs
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.ListConfigurationsResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListConfigurationsResponse()
    
    async def DeleteConfiguration(self, request, context):
        """Delete configuration"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await configuration_service.delete_config(
                    organization_id=request.organization_id,
                    config_key=request.config_key,
                    business_unit_id=request.business_unit_id if request.business_unit_id else None,
                    db=db
                )
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND if "not found" in str(e).lower() else grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
