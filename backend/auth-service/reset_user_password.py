#!/usr/bin/env python3
"""
Script to reset a user's password
Usage: python reset_user_password.py <email> <new_password>
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models.rbac import User
from app.services.security_service import security_service

async def reset_password(email: str, new_password: str):
    """Reset user password"""
    async with AsyncSessionLocal() as db:
        # Find user
        result = await db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        # Validate password
        is_valid, error = security_service.validate_password_strength(new_password)
        if not is_valid:
            print(f"❌ Password does not meet requirements: {error}")
            return False
        
        # Hash and update password
        hashed_password = security_service.hash_password(new_password)
        user.hashed_password = hashed_password
        await db.commit()
        
        print(f"✅ Password reset successfully for user: {user.email} (ID: {user.id})")
        print(f"   Username: {user.username}")
        print(f"   Organization ID: {user.organization_id}")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_user_password.py <email> <new_password>")
        print("\nPassword requirements:")
        print("  - At least 12 characters")
        print("  - At least one uppercase letter")
        print("  - At least one lowercase letter")
        print("  - At least one digit")
        print("  - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    
    asyncio.run(reset_password(email, new_password))
