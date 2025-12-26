
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
    print("\n🔍 VERIFICAÇÃO - AGENDA DA DRA. KATIA LUZIA\n")
    print("Segundo a imagem fornecida:")
    print("  - TODOS os horários estão em CINZA (indisponível)")
    print("  - Sábado: Clínica indisponível (laranja)\n")
    print("  - Expectativa: 0 slots em todos os dias\n")
    
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
    
    # Buscar profissionais
    profs = await client.get_professionals()
    katia_id = None
    for p in profs:
        if "Katia" in p["name"]:
            katia_id = str(p["id"])
            print(f"✅ {p['name']} encontrada (ID: {katia_id})\n")
            break
    
    if not katia_id:
        print("❌ Katia não encontrada")
        return
    
    # Testar próximos 7 dias
    print(f"{'='*70}")
    print("TESTANDO PRÓXIMOS 7 DIAS:")
    print(f"{'='*70}\n")
    
    days_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    for i in range(7):
        date_obj = datetime.now() + timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        day_name = days_pt[date_obj.weekday()]
        
        # Buscar slots da Katia
        slots = await client.check_availability(date_str, professional_id=katia_id)
        
        if slots:
            times = [f"{s['From']}-{s['To']}" for s in slots]
            print(f"{day_name:10} ({date_str}): {len(slots):2} slots | ⚠️ INCONSISTÊNCIA")
            print(f"           API retornou: {times[0]} até {times[-1]}")
            print(f"           ⚠️ Agenda mostra TUDO INDISPONÍVEL!")
        else:
            print(f"{day_name:10} ({date_str}):  0 slots | ✅ CORRETO (agenda bloqueada)")

if __name__ == "__main__":
    asyncio.run(main())
