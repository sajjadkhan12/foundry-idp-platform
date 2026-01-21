#!/usr/bin/env python3
"""
Script to create the organization_configurations table if it doesn't exist
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import AsyncSessionLocal

async def create_table():
    """Create organization_configurations table if it doesn't exist"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if table exists
            result = await db.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'organization_configurations'
                    );
                """)
            )
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ Table 'organization_configurations' already exists")
                return
            
            # Create the table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS organization_configurations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE NOT NULL,
                    business_unit_id UUID REFERENCES business_units(id) ON DELETE CASCADE,
                    config_key VARCHAR(255) NOT NULL,
                    config_value_encrypted TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(organization_id, business_unit_id, config_key)
                );
            """))
            
            # Create indexes
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_org_config_org ON organization_configurations(organization_id);
            """))
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_org_config_bu ON organization_configurations(business_unit_id);
            """))
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_org_config_key ON organization_configurations(config_key);
            """))
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_org_config_active ON organization_configurations(is_active) WHERE is_active = TRUE;
            """))
            
            await db.commit()
            print("✅ Successfully created 'organization_configurations' table and indexes")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating table: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(create_table())
