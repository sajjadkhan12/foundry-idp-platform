"""Configuration service for managing organization and business unit level configurations"""
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
import uuid
import logging
from app.models.configuration import OrganizationConfiguration
from app.services.crypto import crypto_service
from app.config import settings

logger = logging.getLogger(__name__)


class ConfigurationService:
    """Service for managing organization and business unit configurations"""
    
    async def get_config(
        self,
        organization_id: str,
        config_key: str,
        business_unit_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Optional[str]:
        """
        Get configuration value with fallback: BU -> Org -> System default
        
        Args:
            organization_id: Organization ID
            config_key: Configuration key
            business_unit_id: Optional business unit ID
            db: Database session (optional, will create if not provided)
        
        Returns:
            Configuration value (decrypted) or None if not found
        """
        if db is None:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                return await self.get_config(organization_id, config_key, business_unit_id, db)
        
        try:
            org_uuid = uuid.UUID(organization_id)
        except ValueError:
            raise ValueError("Invalid organization ID")
        
        bu_uuid = None
        if business_unit_id:
            try:
                bu_uuid = uuid.UUID(business_unit_id)
            except ValueError:
                raise ValueError("Invalid business unit ID")
        
        # 1. Try business unit level config (if BU provided)
        if bu_uuid:
            result = await db.execute(
                select(OrganizationConfiguration).where(
                    and_(
                        OrganizationConfiguration.organization_id == org_uuid,
                        OrganizationConfiguration.business_unit_id == bu_uuid,
                        OrganizationConfiguration.config_key == config_key,
                        OrganizationConfiguration.is_active == True
                    )
                )
            )
            bu_config = result.scalar_one_or_none()
            if bu_config:
                try:
                    decrypted = crypto_service.decrypt(bu_config.config_value_encrypted)
                    return decrypted.get("value") if isinstance(decrypted, dict) else str(decrypted)
                except Exception as e:
                    logger.error(f"Failed to decrypt BU config {config_key}: {e}")
        
        # 2. Try organization level config
        result = await db.execute(
            select(OrganizationConfiguration).where(
                and_(
                    OrganizationConfiguration.organization_id == org_uuid,
                    OrganizationConfiguration.business_unit_id.is_(None),
                    OrganizationConfiguration.config_key == config_key,
                    OrganizationConfiguration.is_active == True
                )
            )
        )
        org_config = result.scalar_one_or_none()
        if org_config:
            try:
                decrypted = crypto_service.decrypt(org_config.config_value_encrypted)
                return decrypted.get("value") if isinstance(decrypted, dict) else str(decrypted)
            except Exception as e:
                logger.error(f"Failed to decrypt org config {config_key}: {e}")
        
        # 3. Fallback to system default (from .env/settings)
        system_config_key = config_key.upper()
        if hasattr(settings, system_config_key):
            return getattr(settings, system_config_key)
        
        return None
    
    async def set_config(
        self,
        organization_id: str,
        config_key: str,
        config_value: str,
        user_id: str,
        business_unit_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """
        Set configuration value (encrypted)
        
        Args:
            organization_id: Organization ID
            config_key: Configuration key
            config_value: Configuration value (will be encrypted)
            user_id: User ID creating/updating the config
            business_unit_id: Optional business unit ID (None for org-level)
            db: Database session
        
        Returns:
            Configuration dict with id, key, and status
        """
        if db is None:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                return await self.set_config(
                    organization_id, config_key, config_value, user_id, business_unit_id, db
                )
        
        try:
            org_uuid = uuid.UUID(organization_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError as e:
            raise ValueError(f"Invalid ID: {e}")
        
        bu_uuid = None
        if business_unit_id:
            try:
                bu_uuid = uuid.UUID(business_unit_id)
            except ValueError:
                raise ValueError("Invalid business unit ID")
        
        # Encrypt the value
        encrypted_value = crypto_service.encrypt({"value": config_value})
        
        # Check if config already exists
        result = await db.execute(
            select(OrganizationConfiguration).where(
                and_(
                    OrganizationConfiguration.organization_id == org_uuid,
                    OrganizationConfiguration.business_unit_id == (bu_uuid if bu_uuid else None),
                    OrganizationConfiguration.config_key == config_key
                )
            )
        )
        existing_config = result.scalar_one_or_none()
        
        if existing_config:
            # Update existing config
            existing_config.config_value_encrypted = encrypted_value
            existing_config.is_active = True
            existing_config.created_by = user_uuid
            await db.commit()
            await db.refresh(existing_config)
            logger.info(f"Updated config {config_key} for org {organization_id}")
            return {
                "id": str(existing_config.id),
                "config_key": existing_config.config_key,
                "organization_id": str(existing_config.organization_id),
                "business_unit_id": str(existing_config.business_unit_id) if existing_config.business_unit_id else None,
                "is_active": existing_config.is_active
            }
        else:
            # Create new config
            new_config = OrganizationConfiguration(
                organization_id=org_uuid,
                business_unit_id=bu_uuid,
                config_key=config_key,
                config_value_encrypted=encrypted_value,
                is_active=True,
                created_by=user_uuid
            )
            db.add(new_config)
            await db.commit()
            await db.refresh(new_config)
            logger.info(f"Created config {config_key} for org {organization_id}")
            return {
                "id": str(new_config.id),
                "config_key": new_config.config_key,
                "organization_id": str(new_config.organization_id),
                "business_unit_id": str(new_config.business_unit_id) if new_config.business_unit_id else None,
                "is_active": new_config.is_active
            }
    
    async def list_configs(
        self,
        organization_id: str,
        business_unit_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, str]:
        """
        List all configurations for organization/BU (decrypted)
        
        Args:
            organization_id: Organization ID
            business_unit_id: Optional business unit ID
            db: Database session
        
        Returns:
            Dict mapping config_key to config_value (decrypted)
        """
        if db is None:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                return await self.list_configs(organization_id, business_unit_id, db)
        
        try:
            org_uuid = uuid.UUID(organization_id)
        except ValueError:
            raise ValueError("Invalid organization ID")
        
        bu_uuid = None
        if business_unit_id:
            try:
                bu_uuid = uuid.UUID(business_unit_id)
            except ValueError:
                raise ValueError("Invalid business unit ID")
        
        # Build query
        conditions = [
            OrganizationConfiguration.organization_id == org_uuid,
            OrganizationConfiguration.is_active == True
        ]
        
        if bu_uuid:
            # Get both BU-specific and org-level configs
            conditions.append(
                or_(
                    OrganizationConfiguration.business_unit_id == bu_uuid,
                    OrganizationConfiguration.business_unit_id.is_(None)
                )
            )
        else:
            # Only org-level configs
            conditions.append(OrganizationConfiguration.business_unit_id.is_(None))
        
        result = await db.execute(
            select(OrganizationConfiguration).where(and_(*conditions))
        )
        configs = result.scalars().all()
        
        # Decrypt and build result dict
        config_dict = {}
        for config in configs:
            try:
                decrypted = crypto_service.decrypt(config.config_value_encrypted)
                value = decrypted.get("value") if isinstance(decrypted, dict) else str(decrypted)
                config_dict[config.config_key] = value
            except Exception as e:
                logger.error(f"Failed to decrypt config {config.config_key}: {e}")
                continue
        
        return config_dict
    
    async def delete_config(
        self,
        organization_id: str,
        config_key: str,
        business_unit_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> None:
        """
        Delete configuration (soft delete by setting is_active=False)
        
        Args:
            organization_id: Organization ID
            config_key: Configuration key
            business_unit_id: Optional business unit ID
            db: Database session
        """
        if db is None:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                return await self.delete_config(organization_id, config_key, business_unit_id, db)
        
        try:
            org_uuid = uuid.UUID(organization_id)
        except ValueError:
            raise ValueError("Invalid organization ID")
        
        bu_uuid = None
        if business_unit_id:
            try:
                bu_uuid = uuid.UUID(business_unit_id)
            except ValueError:
                raise ValueError("Invalid business unit ID")
        
        result = await db.execute(
            select(OrganizationConfiguration).where(
                and_(
                    OrganizationConfiguration.organization_id == org_uuid,
                    OrganizationConfiguration.business_unit_id == (bu_uuid if bu_uuid else None),
                    OrganizationConfiguration.config_key == config_key
                )
            )
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.is_active = False
            await db.commit()
            logger.info(f"Deleted config {config_key} for org {organization_id}")
        else:
            raise ValueError(f"Configuration {config_key} not found")


# Singleton instance
configuration_service = ConfigurationService()
