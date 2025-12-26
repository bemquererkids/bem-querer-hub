
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
    print("\n🔍 ANÁLISE ESPECÍFICA - HORÁRIOS DA VANESSA BATTISTINI\n")
    
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
    
    # ID da Vanessa (confirmado no teste anterior)
    VANESSA_ID = "5070281037119488"
    
    # Testar múltiplas datas
    dates_to_test = [
        ("26/12 (Quinta)", datetime.now() + timedelta(days=1)),
        ("27/12 (Sexta)", datetime.now() + timedelta(days=2)),
        ("30/12 (Segunda)", datetime.now() + timedelta(days=5)),
        ("31/12 (Terça)", datetime.now() + timedelta(days=6)),
    ]
    
    for label, date_obj in dates_to_test:
        date_str = date_obj.strftime("%Y-%m-%d")
        print(f"\n{'='*60}")
        print(f"📅 {label} - {date_str}")
        print(f"{'='*60}")
        
        try:
            # Buscar TODOS os slots
            all_slots = await client.check_availability(date_str)
            
            # Filtrar apenas da Vanessa
            vanessa_slots = [s for s in all_slots if str(s.get("ProfessionalId")) == VANESSA_ID]
            
            if vanessa_slots:
                print(f"✅ Vanessa tem {len(vanessa_slots)} slots disponíveis:")
                times = [f"{s['From']}-{s['To']}" for s in vanessa_slots]
                print(f"   Primeiro: {times[0]}")
                print(f"   Último: {times[-1]}")
                print(f"   Todos: {', '.join(times)}")
            else:
                print("⚠️ Vanessa não tem slots disponíveis (agenda bloqueada ou sem horários)")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
