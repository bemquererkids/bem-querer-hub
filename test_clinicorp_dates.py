
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
    print("\n🔍 TESTE DETALHADO - DISPONIBILIDADE CLINICORP\n")
    
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
    
    # Testar múltiplas datas
    dates_to_test = [
        ("Hoje (25/12)", datetime.now()),
        ("Amanhã (26/12)", datetime.now() + timedelta(days=1)),
        ("27/12", datetime.now() + timedelta(days=2)),
        ("30/12", datetime.now() + timedelta(days=5)),
    ]
    
    for label, date_obj in dates_to_test:
        date_str = date_obj.strftime("%Y-%m-%d")
        print(f"\n{'='*60}")
        print(f"📅 {label} - {date_str}")
        print(f"{'='*60}")
        
        try:
            slots = await client.check_availability(date_str)
            print(f"✅ Total de slots: {len(slots)}")
            
            if slots:
                # Agrupar por profissional
                prof_slots = {}
                for s in slots:
                    prof_id = s.get("ProfessionalId", "unknown")
                    if prof_id not in prof_slots:
                        prof_slots[prof_id] = []
                    prof_slots[prof_id].append(f"{s['From']}-{s['To']}")
                
                print(f"\n📊 Distribuição por Profissional:")
                for prof_id, times in prof_slots.items():
                    print(f"  ProfessionalId {prof_id}: {len(times)} slots")
                    print(f"    Primeiro: {times[0]}, Último: {times[-1]}")
            else:
                print("  ⚠️ Nenhum slot disponível")
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    # Buscar profissionais para referência
    print(f"\n{'='*60}")
    print("👥 PROFISSIONAIS CADASTRADOS")
    print(f"{'='*60}")
    try:
        profs = await client.get_professionals()
        for p in profs:
            print(f"  - {p.get('name')} (ID: {p.get('id')})")
    except Exception as e:
        print(f"  ❌ Erro ao buscar profissionais: {e}")

if __name__ == "__main__":
    asyncio.run(main())
