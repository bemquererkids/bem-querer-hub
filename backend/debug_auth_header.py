
import asyncio
import httpx
import base64
import sys

async def main():
    print("--- Debug Clinicorp Auth ---")
    
    # HARDCODED FOR VERIFICATION
    username = "luiz.bezerra@bemquerer"
    password = "Vanessa123@"
    
    auth_str = f"{username}:{password}"
    base64_auth = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
    
    print(f"Credentials: {username}:{password}")
    print(f"Generated Header: Basic {base64_auth}")
    
    expected = "Basic bHVpei5iZXplcnJhQGJlbXF1ZXJlcjpWYW5lc3NhMTIzQA=="
    print(f"Expected Header:  {expected}")
    
    if f"Basic {base64_auth}" == expected:
        print("MATCH: Header generation is correct.")
    else:
        print("MISMATCH: Check encoding or trailing spaces.")

    BASE_URL = "https://api.clinicorp.com/rest/v1"
    headers = {
        "Authorization": expected, # Force the expected one provided by user (implied)
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        print(f"\nGET {BASE_URL}/professional/list_all_professionals")
        try:
            resp = await client.get(
                f"{BASE_URL}/professional/list_all_professionals", 
                headers=headers
            )
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
        except Exception as e: 
            print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
