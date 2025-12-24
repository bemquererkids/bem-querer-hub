import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://free.uazapi.com")
TOKEN = os.getenv("UAZAPI_TOKEN")

def test_query():
    print(f"\n--- Testing Query Param (?token=TOKEN) ---")
    url = f"{BASE_URL}/instance/status"
    params = {"token": TOKEN}
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_header():
    print(f"\n--- Testing Header (token: TOKEN) ---")
    url = f"{BASE_URL}/instance/status"
    headers = {"token": TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_query()
    test_header()
