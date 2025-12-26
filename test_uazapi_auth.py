"""
Test UazAPI Authentication Methods
Tests different authentication header formats to find the correct one
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://bemquerer.uazapi.com")
TOKEN = os.getenv("UAZAPI_TOKEN", "093b971c-f10f-4af1-b0aa-a13c6ad15909")

async def test_auth_methods():
    """Test different authentication methods"""
    
    # Test configurations
    tests = [
        {
            "name": "Method 1: Header 'token'",
            "headers": {"token": TOKEN, "Content-Type": "application/json"}
        },
        {
            "name": "Method 2: Header 'admintoken'",
            "headers": {"admintoken": TOKEN, "Content-Type": "application/json"}
        },
        {
            "name": "Method 3: Header 'apikey'",
            "headers": {"apikey": TOKEN, "Content-Type": "application/json"}
        },
        {
            "name": "Method 4: Header 'Authorization: Bearer'",
            "headers": {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        },
        {
            "name": "Method 5: Query param 'token'",
            "headers": {"Content-Type": "application/json"},
            "params": {"token": TOKEN}
        },
        {
            "name": "Method 6: Query param 'admintoken'",
            "headers": {"Content-Type": "application/json"},
            "params": {"admintoken": TOKEN}
        }
    ]
    
    # Endpoints to test
    endpoints = [
        "/instance/status",
        "/instance/list",
        "/instance/connect"
    ]
    
    print(f"\n{'='*80}")
    print(f"Testing UazAPI Authentication")
    print(f"Base URL: {BASE_URL}")
    print(f"Token: {TOKEN[:20]}...{TOKEN[-10:]}")
    print(f"{'='*80}\n")
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for endpoint in endpoints:
            print(f"\n{'─'*80}")
            print(f"📡 Testing Endpoint: {endpoint}")
            print(f"{'─'*80}")
            
            for test in tests:
                url = f"{BASE_URL}{endpoint}"
                headers = test["headers"]
                params = test.get("params", {})
                
                try:
                    response = await client.get(url, headers=headers, params=params)
                    
                    if response.status_code == 200:
                        print(f"✅ {test['name']}")
                        print(f"   Status: {response.status_code}")
                        data = response.json()
                        print(f"   Response: {str(data)[:100]}...")
                        print(f"\n   🎉 SUCCESS! This method works!\n")
                        return test['name'], headers, params, data
                    else:
                        print(f"❌ {test['name']}")
                        print(f"   Status: {response.status_code}")
                        print(f"   Error: {response.text[:100]}")
                        
                except Exception as e:
                    print(f"❌ {test['name']}")
                    print(f"   Error: {str(e)[:100]}")
    
    print(f"\n{'='*80}")
    print("❌ No authentication method worked!")
    print(f"{'='*80}\n")
    return None, None, None, None

async def main():
    result = await test_auth_methods()
    
    if result[0]:
        print(f"\n{'='*80}")
        print("✅ WORKING CONFIGURATION FOUND:")
        print(f"{'='*80}")
        print(f"Method: {result[0]}")
        print(f"Headers: {result[1]}")
        if result[2]:
            print(f"Params: {result[2]}")
        print(f"\nFull Response:")
        import json
        print(json.dumps(result[3], indent=2))
        print(f"{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(main())
