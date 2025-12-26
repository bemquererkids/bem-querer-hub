
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
    print("\n🔍 TESTE - FILTRAGEM POR PROFISSIONAL ESPECÍFICO\n")
    
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
    
    # Testar para sexta-feira (27/12)
    friday = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Buscar profissionais
    profs = await client.get_professionals()
    prof_map = {str(p["id"]): p["name"] for p in profs}
    
    print(f"📅 Testando disponibilidade para SEXTA-FEIRA ({friday})\n")
    
    # Buscar todos os slots
    all_slots = await client.check_availability(friday)
    
    # Agrupar por profissional
    prof_availability = {}
    for slot in all_slots:
        prof_id = str(slot.get("ProfessionalId"))
        prof_name = prof_map.get(prof_id, f"ID {prof_id}")
        if prof_name not in prof_availability:
            prof_availability[prof_name] = []
        prof_availability[prof_name].append(f"{slot['From']}-{slot['To']}")
    
    print(f"{'='*70}")
    print("PROFISSIONAIS QUE ATENDEM NA SEXTA-FEIRA:")
    print(f"{'='*70}\n")
    
    for prof_name in sorted(prof_availability.keys()):
        slots = prof_availability[prof_name]
        print(f"✅ {prof_name}")
        print(f"   {len(slots)} slots: {slots[0]} até {slots[-1]}\n")
    
    print(f"{'='*70}")
    print("PROFISSIONAIS QUE NÃO ATENDEM NA SEXTA-FEIRA:")
    print(f"{'='*70}\n")
    
    for prof in profs:
        prof_name = prof["name"]
        if prof_name not in prof_availability:
            print(f"❌ {prof_name} - SEM HORÁRIOS")
    
    print(f"\n{'='*70}")
    print("TESTE DE FILTRO POR PROFISSIONAL:")
    print(f"{'='*70}\n")
    
    # Testar filtro para um profissional que ATENDE na sexta
    test_prof_works = "Vanessa Battistini"
    print(f"🔍 Buscando horários de '{test_prof_works}' na sexta...")
    
    # Simular o que o GPT service faz
    prof_id_works = None
    for p in profs:
        if test_prof_works.lower() in p["name"].lower():
            prof_id_works = str(p["id"])
            break
    
    if prof_id_works:
        filtered_slots = await client.check_availability(friday, professional_id=prof_id_works)
        if filtered_slots:
            print(f"✅ ENCONTROU {len(filtered_slots)} slots para {test_prof_works}")
        else:
            print(f"⚠️ NÃO encontrou slots (profissional não atende neste dia)")
    
    # Testar filtro para um profissional que NÃO ATENDE na sexta (se houver)
    non_working_profs = [p["name"] for p in profs if p["name"] not in prof_availability]
    if non_working_profs:
        test_prof_doesnt_work = non_working_profs[0]
        print(f"\n🔍 Buscando horários de '{test_prof_doesnt_work}' na sexta...")
        
        prof_id_doesnt = None
        for p in profs:
            if test_prof_doesnt_work == p["name"]:
                prof_id_doesnt = str(p["id"])
                break
        
        if prof_id_doesnt:
            filtered_slots = await client.check_availability(friday, professional_id=prof_id_doesnt)
            if filtered_slots:
                print(f"⚠️ ENCONTROU {len(filtered_slots)} slots (inesperado)")
            else:
                print(f"✅ NÃO encontrou slots (correto - profissional não atende neste dia)")

if __name__ == "__main__":
    asyncio.run(main())
