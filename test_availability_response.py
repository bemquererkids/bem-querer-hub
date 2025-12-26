
import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.clinicorp_service import ClinicorpClient

def load_credentials():
    creds = {}
    try:
        with open("CLINICORP_CREDENTIALS.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    creds[k.strip()] = v.strip()
    except: pass
    return creds

async def main():
    print("\n🔍 TESTE DE RESPOSTA DA API CLINICORP - DISPONIBILIDADE\n")
    
    creds = load_credentials()
    username = creds.get("CLIENT_ID") 
    password = creds.get("CLIENT_SECRET")
    
    if not username or not password:
        print("❌ Erro: Credenciais não encontradas")
        return

    client = ClinicorpClient(
        clinic_id="bemquerer", 
        integration_config={
            "client_id": username,
            "client_secret": password
        }
    )
    
    # Testar para amanhã
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"📅 Consultando disponibilidade para: {tomorrow}\n")
    
    try:
        slots = await client.check_availability(tomorrow)
        print(f"✅ Total de slots retornados: {len(slots)}\n")
        
        if slots:
            print("📋 ESTRUTURA DOS PRIMEIROS 3 SLOTS:\n")
            for i, slot in enumerate(slots[:3], 1):
                print(f"Slot {i}:")
                for key, value in slot.items():
                    print(f"  {key}: {value}")
                print()
            
            # Verificar se há informação de profissional
            has_prof_id = any("ProfessionalId" in s or "professionalId" in s for s in slots)
            has_prof_name = any("ProfessionalName" in s or "professionalName" in s for s in slots)
            
            print(f"🔍 ANÁLISE:")
            print(f"  - Contém ProfessionalId? {has_prof_id}")
            print(f"  - Contém ProfessionalName? {has_prof_name}")
            
            # Listar horários únicos
            times = set()
            for s in slots:
                from_time = s.get("From", s.get("from", ""))
                times.add(from_time)
            
            print(f"\n⏰ HORÁRIOS ÚNICOS DISPONÍVEIS ({len(times)}):")
            for t in sorted(times):
                print(f"  - {t}")
                
        else:
            print("⚠️ Nenhum slot retornado pela API")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
