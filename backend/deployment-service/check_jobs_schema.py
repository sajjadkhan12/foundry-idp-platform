
import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check_schema():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT column_name, is_nullable, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'jobs'
        """))
        for row in result:
            print(f"Column: {row[0]}, Nullable: {row[1]}, Type: {row[2]}")

if __name__ == "__main__":
    asyncio.run(check_schema())
