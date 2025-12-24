import requests
import json
import time

def test_connect():
    print("Testing /api/integrations/whatsapp/connect...")
    url = "http://localhost:8000/api/integrations/whatsapp/connect"
    
    try:
        start_time = time.time()
        response = requests.post(url, timeout=30)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Time taken: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_connect()
