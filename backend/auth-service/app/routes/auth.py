import logging
import traceback
from typing import Optional
from fastapi import APIRouter, HTTPException, Cookie
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, ValidateTokenRequest
from app.core.dependencies import auth_servicer, MockContext, auth_pb2

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint - REST wrapper for gRPC"""
    try:
        if not auth_pb2:
            raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
        
        context = MockContext()
        grpc_request = auth_pb2.LoginRequest(
            identifier=request.identifier,
            password=request.password
        )
        
        response = await auth_servicer.Login(grpc_request, context)
        
        if context.code:
            status_code = 401 if context.code.value == 16 else 500  # UNAUTHENTICATED = 16
            logger.error(f"Login failed with code {context.code.value}: {context.details}")
            raise HTTPException(status_code=status_code, detail=context.details)
        
        return {
            "access_token": response.access_token,
            "token_type": response.token_type,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "username": response.user.username,
                "full_name": response.user.full_name,
                "roles": list(response.user.roles),
                "avatar_url": response.user.avatar_url,
                "is_active": response.user.is_active,
                "is_admin": response.user.is_admin,
                "created_at": response.user.created_at,
                "organization_id": response.user.organization_id if response.user.organization_id else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in login endpoint: {str(e)}", exc_info=True)
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh token endpoint"""
    if not auth_pb2:
        raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
    
    if not request.refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    
    context = MockContext()
    grpc_request = auth_pb2.RefreshTokenRequest(refresh_token=request.refresh_token)
    
    response = await auth_servicer.RefreshToken(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details)
    
    return {
        "access_token": response.access_token,
        "token_type": response.token_type,
        "user": {
            "id": response.user.id,
            "email": response.user.email,
            "username": response.user.username,
            "full_name": response.user.full_name,
            "roles": list(response.user.roles),
            "avatar_url": response.user.avatar_url,
            "is_active": response.user.is_active,
            "is_admin": response.user.is_admin,
            "created_at": response.user.created_at,
            "organization_id": response.user.organization_id if response.user.organization_id else None,
        }
    }


@router.post("/auth/logout")
async def logout(
    request: Optional[RefreshTokenRequest] = None,
    refresh_token: Optional[str] = Cookie(None)
):
    """Logout endpoint"""
    if not auth_pb2:
        raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
    
    # Get refresh token from request body or cookie
    token = (request.refresh_token if request else None) or refresh_token
    
    # Only call logout service if we have a token
    if token:
        context = MockContext()
        grpc_request = auth_pb2.LogoutRequest(refresh_token=token)
        await auth_servicer.Logout(grpc_request, context)
        
        if context.code:
            raise HTTPException(status_code=500, detail=context.details)
    
    return {"message": "Logged out successfully"}


@router.post("/auth/validate")
async def validate_token(request: ValidateTokenRequest):
    """Validate token endpoint"""
    if not auth_pb2:
        raise HTTPException(status_code=503, detail="Proto files not generated. Service not ready.")
    
    context = MockContext()
    grpc_request = auth_pb2.ValidateTokenRequest(token=request.token)
    
    response = await auth_servicer.ValidateToken(grpc_request, context)
    
    if context.code:
        status_code = 401 if context.code.value == 16 else 500
        raise HTTPException(status_code=status_code, detail=context.details)
    
    return {
        "user_id": response.user_id,
        "email": response.email,
        "username": response.username,
        "organization_id": response.organization_id,
        "is_active": response.is_active,
        "roles": list(response.roles)
    }
