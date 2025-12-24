import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://free.uazapi.com")
TOKEN = os.getenv("UAZAPI_TOKEN")
ADMIN_TOKEN = os.getenv("UAZAPI_ADMIN_TOKEN")

def run_tests():
    # 1. Test Instance Token (Header)
    print("\n[TEST 1] Instance Token via Header 'token'")
    try:
        r = requests.get(f"{BASE_URL}/instance/status", headers={"token": TOKEN}, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")
    except Exception as e: print(f"Error: {e}")

    # 2. Test Instance Token (Query)
    print("\n[TEST 2] Instance Token via Query Param '?token='")
    try:
        r = requests.get(f"{BASE_URL}/instance/status", params={"token": TOKEN}, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")
    except Exception as e: print(f"Error: {e}")

    # 3. Test Admin Token (Header)
    print("\n[TEST 3] Admin Token via Header 'admintoken'")
    try:
        r = requests.get(f"{BASE_URL}/instance/status", headers={"admintoken": ADMIN_TOKEN}, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ Success! Raw Data:")
            print(json.dumps(r.json(), indent=2))
        else:
            print(f"Body: {r.text}")
    except Exception as e: print(f"Error: {e}")

    # 4. Test List Instances (Admin)
    print("\n[TEST 4] List Instances via Header 'admintoken'")
    try:
        r = requests.get(f"{BASE_URL}/instance/list", headers={"admintoken": ADMIN_TOKEN}, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Count: {len(r.json())}")
            # print(json.dumps(r.json(), indent=2))
        else:
            print(f"Body: {r.text}")
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_tests()
