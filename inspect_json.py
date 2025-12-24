import requests
import json

def inspect_status():
    print("Requesting instance status...")
    url = "http://localhost:8000/api/integrations/whatsapp/status"
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_status()
