
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
    print("\n🔍 VERIFICAÇÃO - AGENDA DA FERNANDA BATTISTINI\n")
    print("Segundo a imagem fornecida:")
    print("  - Trabalha: QUARTA-FEIRA e SÁBADO")
    print("  - NÃO trabalha: Segunda, Terça, Quinta, Sexta, Domingo\n")
    
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
    fernanda_id = None
    for p in profs:
        if "Fernanda Battistini" in p["name"]:
            fernanda_id = str(p["id"])
            break
    
    if not fernanda_id:
        print("❌ Fernanda não encontrada")
        return
    
    print(f"✅ Fernanda Battistini encontrada (ID: {fernanda_id})\n")
    
    # Testar próximos 7 dias
    print(f"{'='*70}")
    print("TESTANDO PRÓXIMOS 7 DIAS:")
    print(f"{'='*70}\n")
    
    days_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    
    for i in range(7):
        date_obj = datetime.now() + timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        day_name = days_pt[date_obj.weekday()]
        
        # Buscar slots da Fernanda
        slots = await client.check_availability(date_str, professional_id=fernanda_id)
        
        expected_work = "✅ DEVERIA TRABALHAR" if day_name in ["Quarta", "Sábado"] else "❌ NÃO DEVERIA TRABALHAR"
        
        if slots:
            status = "⚠️ INCONSISTÊNCIA" if day_name not in ["Quarta", "Sábado"] else "✅ CORRETO"
            print(f"{day_name:10} ({date_str}): {len(slots):2} slots | {expected_work} | {status}")
            if day_name not in ["Quarta", "Sábado"]:
                print(f"           ⚠️ API retornou slots quando não deveria!")
        else:
            status = "✅ CORRETO" if day_name not in ["Quarta", "Sábado"] else "⚠️ INCONSISTÊNCIA"
            print(f"{day_name:10} ({date_str}):  0 slots | {expected_work} | {status}")
            if day_name in ["Quarta", "Sábado"]:
                print(f"           ⚠️ API não retornou slots quando deveria!")

if __name__ == "__main__":
    asyncio.run(main())
