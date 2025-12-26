
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
    print("\n🔍 VERIFICAÇÃO DETALHADA - AGENDA DA DRA. VANESSA BATTISTINI\n")
    print("Segundo a imagem fornecida:")
    print("  - Trabalha: Segunda a Sexta (com intervalos)")
    print("  - Horários BRANCOS (disponíveis):")
    print("    • 09:00-11:30")
    print("    • 13:30-14:30")
    print("    • 17:00-19:00 (varia por dia)")
    print("  - Horários CINZA (bloqueados): 08:00-08:30, 12:00-13:00, etc.\n")
    
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
    vanessa_id = None
    for p in profs:
        if "Vanessa Battistini" in p["name"]:
            vanessa_id = str(p["id"])
            print(f"✅ {p['name']} encontrada (ID: {vanessa_id})\n")
            break
    
    if not vanessa_id:
        print("❌ Vanessa não encontrada")
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
        
        # Buscar slots da Vanessa
        slots = await client.check_availability(date_str, professional_id=vanessa_id)
        
        # Expectativa: slots em dias de semana
        expected = day_name in ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        
        if slots:
            times = [s['From'] for s in slots]
            status = "✅ CORRETO" if expected else "⚠️ VERIFICAR"
            print(f"{day_name:10} ({date_str}): {len(slots):2} slots | {status}")
            print(f"           Horários: {', '.join(times[:5])}{' ...' if len(times) > 5 else ''}")
            
            # Verificar se há horários FORA dos períodos brancos
            invalid_times = []
            for s in slots:
                time = s['From']
                hour = int(time.split(':')[0])
                minute = int(time.split(':')[1])
                time_int = hour * 100 + minute
                
                # Períodos válidos (brancos): 09:00-11:30, 13:30-14:30, 17:00-19:00
                is_valid = (
                    (900 <= time_int <= 1130) or
                    (1330 <= time_int <= 1430) or
                    (1700 <= time_int <= 1900)
                )
                
                if not is_valid:
                    invalid_times.append(time)
            
            if invalid_times:
                print(f"           ⚠️ Horários FORA dos períodos brancos: {', '.join(invalid_times)}")
        else:
            status = "⚠️ VERIFICAR" if expected else "✅ CORRETO"
            print(f"{day_name:10} ({date_str}):  0 slots | {status}")

if __name__ == "__main__":
    asyncio.run(main())
