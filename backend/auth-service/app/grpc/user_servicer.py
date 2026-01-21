"""User management gRPC servicer"""
import grpc
from proto import auth_pb2, auth_pb2_grpc
from app.services.user_service import user_service


class UserServicer(auth_pb2_grpc.UserServiceServicer):
    """gRPC servicer for user management operations"""
    
    async def CreateUser(self, request, context):
        """Create user"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                user = await user_service.create_user(
                    request.email,
                    request.username,
                    request.password,
                    request.full_name if request.full_name else None,
                    request.organization_id,
                    list(request.role_names) if request.role_names else [],
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
    
    async def UpdateUser(self, request, context):
        """Update user"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # Handle is_active: Since proto3 bool doesn't have presence without optional keyword,
                # we need to detect if is_active was explicitly provided
                # Workaround: Check if other fields were provided. If only password/email/full_name
                # are provided without is_active, assume is_active wasn't meant to be updated
                # If is_active is True, it was definitely set (can't be default)
                # If is_active is False and other fields are empty, it might be default or intentionally set
                # Since REST adapter only sets is_active when request.is_active is not None,
                # we can use a heuristic: if other fields are provided, is_active was likely set too
                has_other_updates = bool(request.email or request.full_name or request.password or request.role_names)
                
                # Determine if is_active should be updated:
                # - If is_active is True, it was definitely set
                # - If is_active is False and other fields are provided, assume it was set
                # - If is_active is False and no other fields, assume it wasn't provided (don't update)
                is_active_value = None
                if request.is_active is True:
                    is_active_value = True
                elif request.is_active is False and has_other_updates:
                    # If False and other fields updated, assume is_active was intentionally set to False
                    is_active_value = False
                # Otherwise (False with no other updates), leave as None to skip update
                
                user = await user_service.update_user(
                    request.user_id,
                    request.email if request.email else None,
                    request.full_name if request.full_name else None,
                    request.password if request.password else None,
                    is_active_value,
                    list(request.role_names) if request.role_names else None,
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
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.UserResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.UserResponse()
    
    async def DeleteUser(self, request, context):
        """Delete user"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await user_service.delete_user(request.user_id, db)
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
    
    async def GetUser(self, request, context):
        """Get user"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                user = await user_service.get_user(request.user_id, db)
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
                    organization_id=user.get("organization_id", ""),
                    active_business_unit_id=user.get("active_business_unit_id", "")
                )
            except ValueError as e:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(str(e))
                return auth_pb2.UserResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.UserResponse()
    
    async def ListUsers(self, request, context):
        """List users"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                result = await user_service.list_users(
                    request.skip,
                    request.limit,
                    request.search if request.search else None,
                    request.role_filter if request.role_filter else None,
                    request.organization_id if request.organization_id else None,
                    db
                )
                users = [
                    auth_pb2.UserResponse(
                        id=u["id"],
                        email=u["email"],
                        username=u["username"],
                        full_name=u.get("full_name", ""),
                        roles=u.get("roles", []),
                        avatar_url=u.get("avatar_url", ""),
                        is_active=u.get("is_active", True),
                        is_admin=u.get("is_admin", False),
                        created_at=u.get("created_at", ""),
                        organization_id=u.get("organization_id", "")
                    )
                    for u in result["users"]
                ]
                return auth_pb2.ListUsersResponse(
                    users=users,
                    total=result["total"],
                    skip=result["skip"],
                    limit=result["limit"]
                )
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.ListUsersResponse()
    
    async def GetCurrentUser(self, request, context):
        """Get current user"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                user = await user_service.get_current_user(request.token, db)
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
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(str(e))
                return auth_pb2.UserResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.UserResponse()
    
    async def UpdateCurrentUser(self, request, context):
        """Update current user"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                user = await user_service.update_current_user(
                    request.token,
                    request.email if request.email else None,
                    request.full_name if request.full_name else None,
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
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(str(e))
                return auth_pb2.UserResponse()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.UserResponse()
    
    async def ChangePassword(self, request, context):
        """Change password"""
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                await user_service.change_password(
                    request.token,
                    request.current_password,
                    request.new_password,
                    db
                )
                return auth_pb2.Empty()
            except ValueError as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(str(e))
                return auth_pb2.Empty()
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Internal error: {str(e)}")
                return auth_pb2.Empty()
