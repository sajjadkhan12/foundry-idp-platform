#!/usr/bin/env python3
"""Test script to verify plugin organization filtering"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.plugin_service import plugin_service
from app.database import AsyncSessionLocal

async def test_filtering():
    """Test that Devoteam sees 0 plugins"""
    async with AsyncSessionLocal() as db:
        # Devoteam organization ID
        devoteam_org_id = '1b21c655-4240-4943-9276-720e04adabfd'
        user_id = '287063a9-1df0-46d1-b155-561bc5d4b61d'
        
        result = await plugin_service.list_plugins(
            user_id=user_id,
            business_unit_id=None,
            organization_id=devoteam_org_id,
            db=db
        )
        
        plugins = result.get("plugins", [])
        print(f"Plugins found for Devoteam: {len(plugins)}")
        print(f"Plugin IDs: {[p['id'] for p in plugins]}")
        
        if len(plugins) == 0:
            print("✅ SUCCESS: Devoteam correctly sees 0 plugins")
        else:
            print(f"❌ FAILED: Devoteam should see 0 plugins but sees {len(plugins)}")
            for p in plugins:
                print(f"  - {p['id']} (org: {p.get('organization_id', 'N/A')})")
        
        # Test Default Organization
        default_org_id = '6e2f2942-d45f-4336-97fb-f55e291cee9c'
        result2 = await plugin_service.list_plugins(
            user_id=user_id,
            business_unit_id=None,
            organization_id=default_org_id,
            db=db
        )
        
        plugins2 = result2.get("plugins", [])
        print(f"\nPlugins found for Default Organization: {len(plugins2)}")
        print(f"Plugin IDs: {[p['id'] for p in plugins2]}")
        
        if len(plugins2) == 1 and plugins2[0]['id'] == 'gcp-bucket':
            print("✅ SUCCESS: Default Organization correctly sees 1 plugin")
        else:
            print(f"❌ FAILED: Default Organization should see 1 plugin but sees {len(plugins2)}")

if __name__ == "__main__":
    asyncio.run(test_filtering())
