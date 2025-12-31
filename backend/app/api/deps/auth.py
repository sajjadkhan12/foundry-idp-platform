"""Authentication dependencies"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.rbac import User
from app.config import settings
from app.core.casbin import get_enforcer
from casbin import Enforcer
from .helpers import is_platform_admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Async query - eagerly load organization
    result = await db.execute(
        select(User)
        .options(selectinload(User.organization))
        .where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
    enforcer: Enforcer = Depends(get_enforcer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Check if user is a platform admin using permission-based checks instead of hardcoded role names.
    """
    # Use permission-based check instead of hardcoded role name
    is_admin = await is_platform_admin(current_user, db, enforcer)
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
