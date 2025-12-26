"""
Test WhatsApp Status Endpoint
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.uazapi_service import get_uazapi_service
from app.core.config import settings

async def test_status():
    print("\n" + "="*80)
    print("Testing WhatsApp Status Endpoint")
    print("="*80)
    print(f"\nConfig:")
    print(f"  BASE_URL: {settings.UAZAPI_BASE_URL}")
    print(f"  TOKEN: {settings.UAZAPI_TOKEN[:20]}...{settings.UAZAPI_TOKEN[-10:]}")
    print(f"  INSTANCE: {settings.UAZAPI_INSTANCE}")
    
    print(f"\nTesting get_instance_status()...")
    
    try:
        uazapi = get_uazapi_service()
        status = await uazapi.get_instance_status(settings.UAZAPI_INSTANCE)
        
        print(f"\n✅ SUCCESS!")
        print(f"Response:")
        import json
        print(json.dumps(status, indent=2))
        
        # Check if connected
        is_connected = status.get('loggedIn', False)
        phone = status.get('instance', 'Unknown')
        
        print(f"\n{'='*80}")
        print(f"Status: {'✅ CONNECTED' if is_connected else '❌ DISCONNECTED'}")
        print(f"Phone: {phone}")
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_status())
    sys.exit(0 if success else 1)
