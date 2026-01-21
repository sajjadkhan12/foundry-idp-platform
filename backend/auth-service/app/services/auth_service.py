"""Authentication service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
import uuid
import re
import logging

from app.models.rbac import User, RefreshToken, Organization
from app.services.security_service import security_service
from app.core.organization import get_user_organization, get_organization_domain
from app.core.casbin import get_enforcer
from app.utils.response_helpers import user_to_response

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    async def login(self, identifier: str, password: str, db: AsyncSession):
        """Authenticate user and return tokens"""
        # Determine if identifier is email or username
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_email = re.match(email_pattern, identifier.strip()) is not None
        
        # Fetch user with organization
        if is_email:
            result = await db.execute(
                select(User)
                .options(selectinload(User.organization))
                .where(User.email == identifier.strip().lower())
            )
        else:
            result = await db.execute(
                select(User)
                .options(selectinload(User.organization))
                .where(User.username == identifier.strip())
            )
        user = result.scalars().first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent identifier: {identifier}")
            raise ValueError("Incorrect email/username or password")
        
        # Verify password with detailed logging
        password_valid = security_service.verify_password(password, user.hashed_password)
        if not password_valid:
            logger.warning(f"Password verification failed for user: {user.email} (ID: {user.id})")
            raise ValueError("Incorrect email/username or password")
        
        if not user.is_active:
            raise ValueError("Inactive user")
        
        # Generate tokens
        access_token = security_service.create_access_token(data={"sub": str(user.id)})
        refresh_token = security_service.create_refresh_token(data={"sub": str(user.id)})
        
        # Get organization BEFORE committing refresh token (to avoid lazy loading issues)
        org = await get_user_organization(user, db)
        org_domain = get_organization_domain(org)
        
        # Store refresh token
        user_id_str = str(user.id)
        user_id = user.id  # Store user ID before commit
        max_retries = 3
        for attempt in range(max_retries):
            try:
                db_refresh_token = RefreshToken(
                    user_id=user.id,
                    token=refresh_token,
                    expires_at=datetime.now(timezone.utc) + timedelta(days=7)
                )
                db.add(db_refresh_token)
                await db.commit()
                break
            except IntegrityError:
                await db.rollback()
                if attempt < max_retries - 1:
                    refresh_token = security_service.create_refresh_token(data={"sub": user_id_str})
                    continue
                else:
                    raise ValueError("Failed to generate unique refresh token")
        
        # Re-query user with relationships after commit to avoid lazy loading issues
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Get user response with roles
        enforcer = get_enforcer()
        enforcer.set_org_domain(org_domain)
        user_response = await user_to_response(user, enforcer, db, include_admin_check=True)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
            "user": user_response
        }
    
    async def refresh_token(self, refresh_token: str, db: AsyncSession):
        """Refresh access token using refresh token"""
        # Decode refresh token
        payload = security_service.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid refresh token")
        
        # Verify refresh token exists in database
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.user_id == uuid.UUID(user_id)
            )
        )
        db_refresh_token = result.scalar_one_or_none()
        
        if not db_refresh_token:
            raise ValueError("Invalid refresh token")
        
        if db_refresh_token.expires_at < datetime.now(timezone.utc):
            # Delete expired token
            await db.delete(db_refresh_token)
            await db.commit()
            raise ValueError("Refresh token expired")
        
        # Get user
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Generate new access token
        access_token = security_service.create_access_token(data={"sub": str(user.id)})
        
        # Get user response
        org = await get_user_organization(user, db)
        org_domain = get_organization_domain(org)
        enforcer = get_enforcer()
        enforcer.set_org_domain(org_domain)
        user_response = await user_to_response(user, enforcer, db, include_admin_check=True)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    
    async def logout(self, refresh_token: str, db: AsyncSession):
        """Logout user by deleting refresh token"""
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        db_refresh_token = result.scalar_one_or_none()
        
        if db_refresh_token:
            await db.delete(db_refresh_token)
            await db.commit()
    
    async def validate_token(self, token: str, db: AsyncSession):
        """Validate access token and return user info"""
        payload = security_service.decode_token(token)
        if not payload or payload.get("type") != "access":
            raise ValueError("Invalid token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token")
        
        # Get user
        result = await db.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        org = await get_user_organization(user, db)
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "username": user.username,
            "organization_id": str(org.id),
            "is_active": user.is_active
        }
    
    async def register(self, email: str, username: str, password: str, full_name: str, organization_slug: str, db: AsyncSession):
        """Register a new user"""
        # Validate password
        is_valid, error = security_service.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Get or create organization
        result = await db.execute(
            select(Organization).where(Organization.slug == organization_slug)
        )
        org = result.scalar_one_or_none()
        
        if not org:
            raise ValueError(f"Organization not found: {organization_slug}")
        
        # Hash password
        hashed_password = security_service.hash_password(password)
        
        # Create user
        user = User(
            email=email.lower(),
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            organization_id=org.id,
            is_active=True
        )
        
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user, ["organization"])
        except IntegrityError:
            await db.rollback()
            raise ValueError("User with this email or username already exists")
        
        # Get user response
        org_domain = get_organization_domain(org)
        enforcer = get_enforcer()
        enforcer.set_org_domain(org_domain)
        user_response = await user_to_response(user, enforcer, db, include_admin_check=True)
        
        return user_response


auth_service = AuthService()
