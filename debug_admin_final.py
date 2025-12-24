import requests
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://free.uazapi.com")
ADMIN_TOKEN = os.getenv("UAZAPI_ADMIN_TOKEN")

def debug_admin_final():
    print(f"Testing Admin Token: {ADMIN_TOKEN[:10]}...")
    url = f"{BASE_URL}/instance/list" # common endpoint
    
    headers_variants = [
        {"admintoken": ADMIN_TOKEN},
        {"adminToken": ADMIN_TOKEN},
        {"token": ADMIN_TOKEN},
        {"apikey": ADMIN_TOKEN},
        {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    ]
    
    for headers in headers_variants:
        h_name = list(headers.keys())[0]
        try:
            print(f"\nHeader: {h_name}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text[:200]}")
            if response.status_code == 200:
                print("✅ FOUND IT!")
                return
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_admin_final()
