import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://free.uazapi.com")
ADMIN_TOKEN = os.getenv("UAZAPI_ADMIN_TOKEN")

def check_admin():
    print(f"Checking with Admin Token: {ADMIN_TOKEN[:10]}...")
    url = f"{BASE_URL}/instance/list" # v2.0 might be /instance/status or /instance/list
    headers = {"admintoken": ADMIN_TOKEN}
    try:
        # First try listing
        response = requests.get(url, headers=headers, timeout=10)
        print(f"List Status: {response.status_code}")
        if response.status_code == 200:
            print("Instances:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"List Failed: {response.text}")
            
        # Then try status of specific instance 'bemquerer' if it failed list
        url_status = f"{BASE_URL}/instance/status"
        # The admin can often see status by providing just admintoken
        # but sometimes it needs the instance name or token.
        # Let's try just admintoken first.
        resp_status = requests.get(url_status, headers=headers, timeout=10)
        print(f"\nStatus Endpoint with AdminToken: {resp_status.status_code}")
        if resp_status.status_code == 200:
            print(json.dumps(resp_status.json(), indent=2))

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_admin()
Line 22:   url = f"{BASE_URL}/instance/list"
Line 24:     # v2.0 might be /instance/status or /instance/list
Line 25:     # Research said /instance/status with token works, but admin?
Line 26:     # Let's try /instance/info?
Line 27:     
Line 28:     endpoints = ["/instance/list", "/instance/status", "/instance/info"]
Line 29:     for ep in endpoints:
Line 30:         u = f"{BASE_URL}{ep}"
Line 31:         r = requests.get(u, headers=headers, timeout=10)
Line 32:         print(f"EP {ep}: {r.status_code}")
Line 33:         if r.status_code == 200:
Line 34:             print(json.dumps(r.json(), indent=2))
Line 35: 
Line 36: if __name__ == "__main__":
Line 37:     check_admin()
