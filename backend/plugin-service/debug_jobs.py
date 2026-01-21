
import asyncio
import os
import sys
import logging

# Configure logging to see the error output
logging.basicConfig(level=logging.ERROR)

async def test_service_list_jobs():
    try:
        from app.services.plugin_service import plugin_service
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            print("Connected to DB")
            
            user_id = "8b864ac3-e972-4780-b462-135f8a2d4b0a" # Random UUID
            business_unit_id = 'fb6aaf85-b181-4731-b0b8-d72973a2274d'
            organization_id = '13339cc1-9259-4b65-95d5-ad2a0357918b'
            
            print(f"Calling list_jobs with org_id={organization_id} bu_id={business_unit_id}")
            
            result = await plugin_service.list_jobs(
                user_id=user_id,
                business_unit_id=business_unit_id,
                organization_id=organization_id,
                skip=0,
                limit=50,
                db=db
            )
            
            print(f"Success! Found {len(result['jobs'])} jobs")
            
    except Exception as e:
        print(f"CAUGHT ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sys.path.append('/app')
    asyncio.run(test_service_list_jobs())
