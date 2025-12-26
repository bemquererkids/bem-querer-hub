"""Create WhatsApp test instance"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_supabase

supabase = get_supabase()

# Clinic ID
clinic_id = "00000000-0000-0000-0000-000000000001"

# Check if instance already exists
existing = supabase.table('whatsapp_instances').select('*').eq('instance_name', 'bemquerer').execute()

if existing.data:
    print(f"✅ Instância 'bemquerer' já existe!")
    print(f"   ID: {existing.data[0]['id']}")
    print(f"   Clinic ID: {existing.data[0]['clinic_id']}")
else:
    # Create instance
    result = supabase.table('whatsapp_instances').insert({
        "clinic_id": clinic_id,
        "instance_name": "bemquerer",
        "phone_number": "5511991026844",
        "status": "connected",
        "webhook_url": "https://bem-querer-hub.vercel.app/api/webhooks/whatsapp"
    }).execute()
    
    print(f"✅ Instância criada com sucesso!")
    print(f"   ID: {result.data[0]['id']}")
    print(f"   Instance: {result.data[0]['instance_name']}")
    print(f"   Clinic ID: {result.data[0]['clinic_id']}")
