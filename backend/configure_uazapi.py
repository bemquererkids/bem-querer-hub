import os
import requests
import asyncio
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv("backend/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use Service Key to bypass RLS
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY (or SERVICE_KEY) in .env")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def check_and_configure():
    print("🔍 Verifying Database Schema for UAZAPI (via REST)...")
    
    # 1. Check for instance_name column
    # We try to select 'instance_name' from 'clinic_integrations'
    url = f"{SUPABASE_URL}/rest/v1/clinic_integrations?select=instance_name&limit=1"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            print("✅ Column 'instance_name' found (Query successful). Migration V3 applied!")
        else:
            # If status 400, it usually means column doesn't exist
            if "instance_name" in response.text and "does not exist" in response.text:
                 print("\n❌ Migration V3 NOT detected.")
                 print("The column 'instance_name' is missing.")
                 print("Please run 'supabase/migrations/v3_restore_uazapi.sql' in Supabase SQL Editor.")
                 return
            else:
                 print(f"⚠️ Unexpected error checking schema: {response.status_code} - {response.text}")
                 # We continue, maybe it's empty but exists
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Configure UAZAPI
    print("\n⚙️  Configuring UAZAPI Integration...")
    
    # Credentials from debug_uaz.py
    INSTANCE_NAME = "bemquerer"
    TOKEN = "f2b56a94-37e1-4e6d-8921-7da54069d797"
    CLINIC_ID = "00000000-0000-0000-0000-000000000001"
    
    data = {
        "clinica_id": CLINIC_ID,
        "type": "whatsapp",
        "instance_name": INSTANCE_NAME,
        "token": TOKEN,
        "phone_number_id": None,
        "waba_id": None,
        "access_token": None, 
        "is_active": True,
        "config": {} # Ensure jsonb is satisfied
    }
    
    try:
        # Upsert logic via PostgREST
        # on_conflict needs to be handled via 'resolution=merge-duplicates' in Prefer header 
        # BUT standard upsert in REST uses POST with Prefer: resolution=merge-duplicates,on_conflict=clinica_id,type
        
        upsert_headers = HEADERS.copy()
        upsert_headers["Prefer"] = "resolution=merge-duplicates,on_conflict=clinica_id,type"
        
        url_post = f"{SUPABASE_URL}/rest/v1/clinic_integrations"
        
        resp = requests.post(url_post, headers=upsert_headers, json=data)
        
        if resp.status_code in [200, 201, 204]:
            print(f"✅ UAZAPI configured for instance: {INSTANCE_NAME}")
            print("Backend should now be ready to send/receive via UazAPI.")
        else:
             print(f"❌ Failed to save configuration: {resp.status_code} - {resp.text}")
        
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")

if __name__ == "__main__":
    check_and_configure()
