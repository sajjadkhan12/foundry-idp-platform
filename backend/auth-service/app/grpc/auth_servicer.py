"""Authentication gRPC servicer"""
import grpc
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import auth_service
try:
    from proto import auth_pb2, auth_pb2_grpc
except ImportError:
    # Fallback for development
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from proto import auth_pb2, auth_pb2_grpc


class AuthenticationServicer(auth_pb2_grpc.AuthenticationServiceServicer):
    """gRPC servicer for authentication operations"""
    
    async def Login(self, request: auth_pb2.LoginRequest, context: grpc.ServicerContext) -> auth_pb2.TokenResponse:
        """Handle login request"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await auth_service.login(request.identifier, request.password, db)
                
                user = result["user"]
                return auth_pb2.TokenResponse(
                    access_token=result["access_token"],
                    token_type=result["token_type"],
                    user=auth_pb2.UserResponse(
                        id=user["id"],
                        email=user["email"],
                        username=user["username"],
                        full_name=user.get("full_name", ""),
                        roles=user.get("roles", []),
                        avatar_url=user.get("avatar_url", ""),
                        is_active=user.get("is_active", True),
                        is_admin=user.get("is_admin", False),
                        created_at=user.get("created_at", ""),
                        organization_id=user.get("organization_id", "")
                    )
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(str(e))
                return auth_pb2.TokenResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.TokenResponse()
    
    async def RefreshToken(self, request: auth_pb2.RefreshTokenRequest, context: grpc.ServicerContext) -> auth_pb2.TokenResponse:
        """Handle refresh token request"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await auth_service.refresh_token(request.refresh_token, db)
                
                user = result["user"]
                return auth_pb2.TokenResponse(
                    access_token=result["access_token"],
                    token_type=result["token_type"],
                    user=auth_pb2.UserResponse(
                        id=user["id"],
                        email=user["email"],
                        username=user["username"],
                        full_name=user.get("full_name", ""),
                        roles=user.get("roles", []),
                        avatar_url=user.get("avatar_url", ""),
                        is_active=user.get("is_active", True),
                        is_admin=user.get("is_admin", False),
                        created_at=user.get("created_at", ""),
                        organization_id=user.get("organization_id", "")
                    )
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(str(e))
                return auth_pb2.TokenResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.TokenResponse()
    
    async def Logout(self, request: auth_pb2.LogoutRequest, context: grpc.ServicerContext) -> auth_pb2.Empty:
        """Handle logout request"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await auth_service.logout(request.refresh_token, db)
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def ValidateToken(self, request: auth_pb2.ValidateTokenRequest, context: grpc.ServicerContext) -> auth_pb2.UserInfo:
        """Validate token and return user info"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                user_info = await auth_service.validate_token(request.token, db)
                return auth_pb2.UserInfo(
                    user_id=user_info["user_id"],
                    email=user_info["email"],
                    username=user_info["username"],
                    organization_id=user_info["organization_id"],
                    is_active=user_info["is_active"],
                    roles=[]  # Can be populated if needed
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(str(e))
                return auth_pb2.UserInfo()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.UserInfo()
    
    async def Register(self, request: auth_pb2.RegisterRequest, context: grpc.ServicerContext) -> auth_pb2.UserResponse:
        """Handle user registration"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                user = await auth_service.register(
                    request.email,
                    request.username,
                    request.password,
                    request.full_name,
                    request.organization_slug,
                    db
                )
                return auth_pb2.UserResponse(
                    id=user["id"],
                    email=user["email"],
                    username=user["username"],
                    full_name=user.get("full_name", ""),
                    roles=user.get("roles", []),
                    avatar_url=user.get("avatar_url", ""),
                    is_active=user.get("is_active", True),
                    is_admin=user.get("is_admin", False),
                    created_at=user.get("created_at", ""),
                    organization_id=user.get("organization_id", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.UserResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.UserResponse()
