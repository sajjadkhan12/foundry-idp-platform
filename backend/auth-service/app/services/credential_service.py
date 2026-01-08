"""Credential service for managing cloud credentials"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.credential import CloudCredential, CloudProvider
from app.services.crypto import crypto_service
from typing import Optional, Dict, List
import json


class CredentialService:
    """Service for credential operations"""
    
    async def create_credential(
        self,
        name: str,
        provider: str,
        credentials: str,  # JSON string
        db: AsyncSession
    ) -> Dict:
        """Create or update a cloud credential"""
        # Validate provider
        try:
            provider_enum = CloudProvider(provider)
        except ValueError:
            raise ValueError(f"Invalid provider. Must be one of: {', '.join([p.value for p in CloudProvider])}")
        
        # Parse and validate credentials JSON
        try:
            creds_dict = json.loads(credentials)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in credentials")
        
        # Check if credential with this name exists
        result = await db.execute(
            select(CloudCredential).where(CloudCredential.name == name)
        )
        existing = result.scalar_one_or_none()
        
        # Encrypt credentials
        encrypted_data = crypto_service.encrypt(creds_dict)
        
        if existing:
            # Update existing
            existing.provider = provider_enum
            existing.encrypted_data = encrypted_data
            await db.commit()
            await db.refresh(existing)
        else:
            # Create new
            existing = CloudCredential(
                name=name,
                provider=provider_enum,
                encrypted_data=encrypted_data
            )
            db.add(existing)
            await db.commit()
            await db.refresh(existing)
        
        return {
            "id": existing.id,
            "name": existing.name,
            "provider": existing.provider.value,
            "created_at": existing.created_at.isoformat(),
            "updated_at": existing.updated_at.isoformat()
        }
    
    async def update_credential(
        self,
        credential_id: int,
        name: Optional[str],
        credentials: Optional[str],  # JSON string
        db: AsyncSession
    ) -> Dict:
        """Update a cloud credential"""
        result = await db.execute(
            select(CloudCredential).where(CloudCredential.id == credential_id)
        )
        credential = result.scalar_one_or_none()
        
        if not credential:
            raise ValueError("Credential not found")
        
        # Update fields
        if name is not None:
            # Check if name is taken by another credential
            result = await db.execute(
                select(CloudCredential).where(
                    (CloudCredential.name == name) & (CloudCredential.id != credential_id)
                )
            )
            if result.scalar_one_or_none():
                raise ValueError("Credential name already in use")
            credential.name = name
        
        if credentials is not None:
            # Parse and validate credentials JSON
            try:
                creds_dict = json.loads(credentials)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in credentials")
            
            # Encrypt credentials
            credential.encrypted_data = crypto_service.encrypt(creds_dict)
        
        await db.commit()
        await db.refresh(credential)
        
        return {
            "id": credential.id,
            "name": credential.name,
            "provider": credential.provider.value,
            "created_at": credential.created_at.isoformat(),
            "updated_at": credential.updated_at.isoformat()
        }
    
    async def delete_credential(
        self,
        credential_id: int,
        db: AsyncSession
    ) -> None:
        """Delete a cloud credential"""
        result = await db.execute(
            select(CloudCredential).where(CloudCredential.id == credential_id)
        )
        credential = result.scalar_one_or_none()
        
        if not credential:
            raise ValueError("Credential not found")
        
        await db.delete(credential)
        await db.commit()
    
    async def get_credential(
        self,
        credential_id: int,
        db: AsyncSession
    ) -> Dict:
        """Get a cloud credential by ID (without decrypted data)"""
        result = await db.execute(
            select(CloudCredential).where(CloudCredential.id == credential_id)
        )
        credential = result.scalar_one_or_none()
        
        if not credential:
            raise ValueError("Credential not found")
        
        return {
            "id": credential.id,
            "name": credential.name,
            "provider": credential.provider.value,
            "created_at": credential.created_at.isoformat(),
            "updated_at": credential.updated_at.isoformat()
        }
    
    async def list_credentials(
        self,
        db: AsyncSession
    ) -> List[Dict]:
        """List all credentials (without decrypted data)"""
        result = await db.execute(select(CloudCredential))
        credentials = result.scalars().all()
        
        return [
            {
                "id": cred.id,
                "name": cred.name,
                "provider": cred.provider.value,
                "created_at": cred.created_at.isoformat(),
                "updated_at": cred.updated_at.isoformat()
            }
            for cred in credentials
        ]


credential_service = CredentialService()
