
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
    print("\n🔍 VERIFICAÇÃO - AGENDA DA DRA. THAYNA SCARPIELLO\n")
    print("Segundo a imagem fornecida:")
    print("  - Segunda a Sexta: TODOS os horários BRANCOS (disponíveis)")
    print("  - Sábado: Horários laranja (clínica indisponível) das 14:30-20:00\n")
    print("  - Expectativa: Muitos slots de Segunda a Sexta\n")
    
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
    thayna_id = None
    for p in profs:
        if "Thayna" in p["name"]:
            thayna_id = str(p["id"])
            print(f"✅ {p['name']} encontrada (ID: {thayna_id})\n")
            break
    
    if not thayna_id:
        print("❌ Thayna não encontrada")
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
        
        # Buscar slots da Thayna
        slots = await client.check_availability(date_str, professional_id=thayna_id)
        
        # Expectativa: slots em dias de semana
        expected = day_name in ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        
        if slots:
            times = [f"{s['From']}-{s['To']}" for s in slots]
            status = "✅ CORRETO" if expected else "⚠️ VERIFICAR"
            print(f"{day_name:10} ({date_str}): {len(slots):2} slots | {status}")
            print(f"           Horários: {times[0]} até {times[-1]}")
        else:
            status = "⚠️ VERIFICAR" if expected else "✅ CORRETO"
            print(f"{day_name:10} ({date_str}):  0 slots | {status}")
            if expected:
                print(f"           ⚠️ Esperava slots (agenda mostra disponível)")

if __name__ == "__main__":
    asyncio.run(main())
