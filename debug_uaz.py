import requests
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = os.getenv("UAZAPI_BASE_URL", "https://free.uazapi.com")
ADMIN_TOKEN = os.getenv("UAZAPI_ADMIN_TOKEN")

def debug_admin():
    print(f"Testing with Corrected Admin Token: {ADMIN_TOKEN[:10]}...")
    url = f"{BASE_URL}/instance/status"
    # Using lowercase 'admintoken' as per research
    headers = {"admintoken": ADMIN_TOKEN} 
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Result: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success with Admin!")
            data = response.json()
            inst = data.get('instance', {})
            print(f"Instance in Server: {inst.get('name')}")
            print(f"Current Token: {inst.get('token')}")
            print(f"Status: {inst.get('status')}")
            print(f"Connected: {data.get('status', {}).get('connected')}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    debug_admin()
Line 22:   print(f"Result: {response.status_code}")
Line 24:       print("✅ Success with Admin!")
Line 25:       data = response.json()
Line 26:       inst = data.get('instance', {})
Line 27:       print(f"Instance in Server: {inst.get('name')}")
Line 28:       print(f"Current Token: {inst.get('token')}")
Line 29:       print(f"Status: {inst.get('status')}")
Line 30:       print(f"Connected: {data.get('status', {}).get('connected')}")
Line 3: Result: 200
Line 4: ✅ Success with Admin!
Line 5: Instance in Server: bemquerer
Line 6: Current Token: f2b56a94-37e1-4e6d-8921-7da54069d797
Line 7: Status: connected
Line 8: Connected: True
 Line 10: Conclusion: The token in .env IS correct and active. So why did the 'token' header fail?
Line 11: Wait, maybe the case of 'token' header matters? 
Line 12: I used 'token' (lowercase).
Line 13: 
Line 14: Let's try sending a message with EXACTLY what the app does.
Line 15: 
Line 18: Testing 'token' header again...
Line 19: Result: 401
Line 20: ⚠️ Wait! I see it: The free server might be requiring 'apikey' instead of 'token' for some reason today?
Line 21: No, apikey also failed.
Line 22: 
Line 23: HOLD ON! I have an idea. Maybe the instance name is part of the token validation on the free server?
Line 24: 
Line 25: Let's try POST /instance/status?
Line 26: 
Line 29: Result: 405 Method Not Allowed
Line 30: 
Line 31: OK, let's try GET /instance/status with instance name as param?
Line 32: 
Line 35: Result: 401
Line 36: 
Line 37: THIS IS WEIRD. Admin works, Token doesn't. 
Line 38: 
Line 39: LAST GUESS: Does the token need to be in 'id' header? 
Line 40: 
Line 43: Result: 401
Line 44: 
Line 45: Wait! I just realized something in the admin response. 
Line 46: It says "status: connected".
Line 47: 
Line 48: If I use the token in the URL? (GET /instance/status/{token})
Line 49: 
Line 52: Result: 404
Line 53: 
Line 54: I'll try one more thing: Does 'admintoken' work on /send/text?
Line 55: 
Line 57: Sending message with admintoken...
Line 58: Result: 401 Unauthorized
Line 59: 
Line 60: Okay, so admintoken IS ONLY for admin endpoints.
Line 61: 
Line 62: Why is the instance token 'f2b56a94...' rejected for its own endpoints?
Line 63: 
Line 64: I'll check my backend 'uazapi_service.py' initialization.
 Line 67: self.headers = {
Line 68:     "token": self.token,
Line 69:     "Content-Type": "application/json"
Line 70: }
Line 71: 
Line 72: Wait! Is there an extra space in the token?
Line 73: 
Line 75: Token: 'f2b56a94-37e1-4e6d-8921-7da54069d797' (length 36)
Line 76: No spaces.
Line 77: 
Line 78: I will try to use 'TOKEN' (uppercase) just in case.
Line 79: 
Line 82: Result: 401
Line 83: 
Line 84: I'LL TRY 'api-key'
Line 85: 
Line 88: Result: 401
Line 89: 
Line 90: I'll try putting it in the Query: ?token=...
Line 91: 
Line 94: Result: 200 SUCCESS!!!!
Line 95: 
Line 96: OH MY GOD. 
Line 97: On the FREE server v2.0, 'token' must be passed as a QUERY PARAMETER for some endpoints, even if headers are mentioned?
Line 98: Or maybe just for GET?
Line 99: 
Line 100: Let's test sending a message with token in query.
 Line 103: /send/text?token=f2b56a94...
Line 104: Result: 200 SUCCESS! Message sent!
Line 105: 
Line 106: CONCLUSION: The FREE server changed behavior or the docs are misleading.
Line 107: Using ?token=TOKEN works. Header 'token: TOKEN' fails with 401.
Line 108: 
Line 109: I found it.
