"""
Live Authentication Test for UazAPI
Tests all authentication methods against real UazAPI endpoints
"""
import asyncio
import httpx
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://bemquerer.uazapi.com")
TOKEN = os.getenv("UAZAPI_TOKEN", "093b971c-f10f-4af1-b0aa-a13c6ad15909")

async def test_authentication():
    """Test all possible authentication methods"""
    
    print(f"\n{'='*80}")
    print(f"🔐 UazAPI Authentication Test")
    print(f"{'='*80}")
    print(f"Base URL: {BASE_URL}")
    print(f"Token: {TOKEN[:20]}...{TOKEN[-10:]}")
    print(f"{'='*80}\n")
    
    # Test configurations
    auth_methods = [
        {
            "name": "admintoken (Header)",
            "headers": {"admintoken": TOKEN, "Content-Type": "application/json"},
            "params": {}
        },
        {
            "name": "token (Header)",
            "headers": {"token": TOKEN, "Content-Type": "application/json"},
            "params": {}
        },
        {
            "name": "apikey (Header)",
            "headers": {"apikey": TOKEN, "Content-Type": "application/json"},
            "params": {}
        },
        {
            "name": "Authorization Bearer (Header)",
            "headers": {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
            "params": {}
        },
        {
            "name": "token (Query Param)",
            "headers": {"Content-Type": "application/json"},
            "params": {"token": TOKEN}
        },
        {
            "name": "admintoken (Query Param)",
            "headers": {"Content-Type": "application/json"},
            "params": {"admintoken": TOKEN}
        }
    ]
    
    # Endpoints to test
    endpoints = [
        "/instance/status",
        "/instance/list",
    ]
    
    working_configs = []
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for endpoint in endpoints:
            print(f"\n{'─'*80}")
            print(f"📡 Testing: {endpoint}")
            print(f"{'─'*80}")
            
            for method in auth_methods:
                url = f"{BASE_URL}{endpoint}"
                
                try:
                    response = await client.get(
                        url,
                        headers=method["headers"],
                        params=method["params"]
                    )
                    
                    status = response.status_code
                    
                    if status == 200:
                        print(f"✅ {method['name']:<30} Status: {status}")
                        try:
                            data = response.json()
                            print(f"   Response preview: {str(data)[:80]}...")
                            working_configs.append({
                                "endpoint": endpoint,
                                "method": method["name"],
                                "headers": method["headers"],
                                "params": method["params"],
                                "response": data
                            })
                        except:
                            print(f"   Response: {response.text[:80]}...")
                    elif status == 401:
                        print(f"❌ {method['name']:<30} Status: {status} (Unauthorized)")
                    elif status == 404:
                        print(f"⚠️  {method['name']:<30} Status: {status} (Not Found)")
                    else:
                        print(f"❌ {method['name']:<30} Status: {status}")
                        
                except httpx.TimeoutException:
                    print(f"⏱️  {method['name']:<30} Timeout")
                except Exception as e:
                    print(f"❌ {method['name']:<30} Error: {str(e)[:50]}")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 RESULTS SUMMARY")
    print(f"{'='*80}\n")
    
    if working_configs:
        print(f"✅ Found {len(working_configs)} working configuration(s)!\n")
        
        for i, config in enumerate(working_configs, 1):
            print(f"Configuration #{i}:")
            print(f"  Endpoint: {config['endpoint']}")
            print(f"  Method: {config['method']}")
            print(f"  Headers: {config['headers']}")
            if config['params']:
                print(f"  Params: {config['params']}")
            print(f"  Response: {config['response']}\n")
        
        # Recommend best method
        print(f"{'─'*80}")
        print(f"💡 RECOMMENDATION:")
        print(f"{'─'*80}")
        best = working_configs[0]
        print(f"Use: {best['method']}")
        print(f"Headers: {best['headers']}")
        if best['params']:
            print(f"Params: {best['params']}")
        print(f"{'─'*80}\n")
        
        return working_configs[0]
    else:
        print("❌ No working authentication method found!")
        print("\n🔍 Troubleshooting:")
        print("  1. Verify token is correct in .env file")
        print("  2. Check if token is expired in UazAPI dashboard")
        print("  3. Verify BASE_URL is correct")
        print("  4. Check if instance exists in UazAPI panel\n")
        return None

async def main():
    result = await test_authentication()
    
    if result:
        print(f"{'='*80}")
        print(f"✅ SUCCESS! Authentication method identified.")
        print(f"{'='*80}\n")
        return 0
    else:
        print(f"{'='*80}")
        print(f"❌ FAILED! No authentication method worked.")
        print(f"{'='*80}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
