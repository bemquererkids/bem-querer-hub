import requests
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://free.uazapi.com")
ADMIN_TOKEN = os.getenv("UAZAPI_ADMIN_TOKEN")

def list_instances():
    print(f"Listing instances using Admin Token: {ADMIN_TOKEN[:10]}...")
    url = f"{BASE_URL}/instance/list"
    headers = {
        "adminToken": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            instances = response.json()
            print("Instances found:")
            for inst in instances:
                print(f"- Name: {inst.get('name')}, Status: {inst.get('status')}, Token: {inst.get('token')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_instances()
