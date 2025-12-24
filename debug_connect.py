import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://free.uazapi.com")
TOKEN = os.getenv("UAZAPI_TOKEN")

def run_debug():
    print(f"Testing with Token: {TOKEN}")
    headers = {"token": TOKEN, "Content-Type": "application/json"}
    
    # Test 1: Connect
    try:
        print("\n--- POST /instance/connect ---")
        r = requests.post(f"{BASE_URL}/instance/connect", headers=headers, json={}, timeout=15)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")
    except Exception as e: print(f"Error: {e}")

    # Test 2: Send Text
    try:
        print("\n--- POST /send/text ---")
        payload = {"number": "551144361721", "text": "Teste de conexão Bem-Querer"}
        r = requests.post(f"{BASE_URL}/send/text", headers=headers, json=payload, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")
    except Exception as e: print(f"Error: {e}")

    # Test 3: Status
    try:
        print("\n--- GET /instance/status ---")
        r = requests.get(f"{BASE_URL}/instance/status", headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_debug()
