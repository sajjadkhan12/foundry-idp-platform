import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def update_schema():
    async with AsyncSessionLocal() as db:
        print("Starting schema update for cost estimation...")
        
        # 1. Add columns to deployments table
        try:
            await db.execute(text("""
                ALTER TABLE deployments 
                ADD COLUMN IF NOT EXISTS estimated_monthly_cost NUMERIC(10, 2),
                ADD COLUMN IF NOT EXISTS actual_monthly_cost NUMERIC(10, 2)
            """))
            await db.commit()
            print("Successfully added cost columns to deployments table.")
        except Exception as e:
            await db.rollback()
            print(f"Error adding columns to deployments table: {e}")

        # 2. Create deployment_costs table
        try:
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS deployment_costs (
                    id UUID PRIMARY KEY,
                    deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
                    billing_month VARCHAR(7) NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL,
                    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
                    breakdown JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE (deployment_id, billing_month)
                )
            """))
            await db.commit()
            print("Successfully created deployment_costs table.")
        except Exception as e:
            await db.rollback()
            print(f"Error creating deployment_costs table: {e}")

        print("Schema update complete.")

if __name__ == "__main__":
    asyncio.run(update_schema())
