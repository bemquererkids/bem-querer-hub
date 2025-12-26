"""
Simple UazAPI Auth Test - Direct Output
"""
import asyncio
import httpx

# Credentials from VERCEL_WHATSAPP_CONFIG.md (newer)
BASE_URL = "https://bemquerer.uazapi.com"
TOKEN = "093b971c-f10f-4af1-b0aa-a13c6ad15909"
INSTANCE = "bemquerer"

async def test():
    print(f"\nTesting: {BASE_URL}/instance/status")
    print(f"Token: {TOKEN[:20]}...{TOKEN[-10:]}\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: admintoken header
        print("Test 1: admintoken header")
        try:
            response = await client.get(
                f"{BASE_URL}/instance/status",
                headers={"admintoken": TOKEN, "Content-Type": "application/json"}
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                print(f"  Response: {response.json()}\n")
                return "admintoken"
            else:
                print(f"  Response: {response.text[:200]}\n")
        except Exception as e:
            print(f"  Error: {e}\n")
        
        # Test 2: token header
        print("Test 2: token header")
        try:
            response = await client.get(
                f"{BASE_URL}/instance/status",
                headers={"token": TOKEN, "Content-Type": "application/json"}
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                print(f"  Response: {response.json()}\n")
                return "token"
            else:
                print(f"  Response: {response.text[:200]}\n")
        except Exception as e:
            print(f"  Error: {e}\n")
        
        # Test 3: apikey header
        print("Test 3: apikey header")
        try:
            response = await client.get(
                f"{BASE_URL}/instance/status",
                headers={"apikey": TOKEN, "Content-Type": "application/json"}
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                print(f"  Response: {response.json()}\n")
                return "apikey"
            else:
                print(f"  Response: {response.text[:200]}\n")
        except Exception as e:
            print(f"  Error: {e}\n")
    
    return None

if __name__ == "__main__":
    result = asyncio.run(test())
    print(f"\nWorking method: {result}")
