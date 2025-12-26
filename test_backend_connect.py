"""
Test WhatsApp Connect Endpoint (QR Code Generation)
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.uazapi_service import get_uazapi_service
from app.core.config import settings

async def test_connect():
    print("\n" + "="*80)
    print("Testing WhatsApp Connect Endpoint (QR Code)")
    print("="*80)
    
    print(f"\nNote: Since WhatsApp is already connected, this may return")
    print(f"      the current status instead of a new QR code.\n")
    
    try:
        uazapi = get_uazapi_service()
        result = await uazapi.connect_instance(settings.UAZAPI_INSTANCE)
        
        print(f"✅ SUCCESS!")
        print(f"\nResponse:")
        import json
        print(json.dumps(result, indent=2))
        
        # Check if QR code is present
        has_qr = 'qrcode' in str(result).lower() or 'qr' in str(result).lower()
        is_connected = 'loggedIn' in str(result) and result.get('loggedIn', False)
        
        print(f"\n{'='*80}")
        if is_connected:
            print(f"✅ WhatsApp is already connected!")
            print(f"   No QR code needed.")
        elif has_qr:
            print(f"📱 QR Code available for scanning")
        else:
            print(f"ℹ️  Response received (check above for details)")
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connect())
    sys.exit(0 if success else 1)
