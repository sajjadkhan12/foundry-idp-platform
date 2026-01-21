
import os
import asyncio
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Standard Postgres connection string for dev
# Change this if your DB settings are different
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://default_user:default_password@localhost:5432/devplatform_idp")

async def update_schema():
    print(f"Connecting to database at {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Adding pulumi_stack_name and infrastructure_deployment_id to deployments table...")
        
        # Check if columns exist first
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='deployments' AND column_name='pulumi_stack_name';
        """))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE deployments ADD COLUMN pulumi_stack_name VARCHAR(255);"))
            print("Added pulumi_stack_name column.")
        else:
            print("pulumi_stack_name column already exists.")

        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='deployments' AND column_name='infrastructure_deployment_id';
        """))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE deployments ADD COLUMN infrastructure_deployment_id UUID REFERENCES deployments(id) ON DELETE SET NULL;"))
            print("Added infrastructure_deployment_id column.")
        else:
            print("infrastructure_deployment_id column already exists.")
            
        conn.commit()
        print("Schema update completed successfully.")

if __name__ == "__main__":
    asyncio.run(update_schema())
