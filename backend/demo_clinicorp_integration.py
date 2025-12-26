
import asyncio
import sys
import os
import random
from datetime import datetime

# Add backend directory to python path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    print("\n🚀 DEMONSTRAÇÃO DO BACKEND: INTEGRAÇÃO CLINICORP\n")
    
    # 1. Carregar Credenciais Reais
    creds = load_credentials()
    username = creds.get("CLIENT_ID") 
    password = creds.get("CLIENT_SECRET")
    
    if not username or not password:
        print("❌ Erro: Credenciais não encontradas em CLINICORP_CREDENTIALS.txt")
        return

    print(f"🔑 Autenticando com usuário: {username}\n")

    # 2. Inicializar o Cliente Oficial (Refatorado)
    client = ClinicorpClient(
        clinic_id="bemquerer", 
        integration_config={
            "client_id": username,
            "client_secret": password
        }
    )
    
    # 3. Testar: Listar Profissionais
    print("📋 [1/4] Buscando Profissionais...")
    try:
        profs = await client.get_professionals()
        print(f"   ✅ Sucesso! Encontrados {len(profs)} profissionais.")
        if profs:
            print(f"   Exemplo: {profs[0].get('name')} (ID: {profs[0].get('id')})")
    except Exception as e:
        print(f"   ❌ Falha: {e}")

    # 4. Testar: Consultar Disponibilidade (Amanhã)
    tomorrow = (datetime.now().strftime("%Y-%m-%d")) # Usando hoje/amanhã
    print(f"\n📅 [2/4] Verificando Agenda para {tomorrow}...")
    try:
        slots = await client.check_availability(tomorrow)
        print(f"   ✅ Sucesso! Encontrados {len(slots)} horários vagos.")
    except Exception as e:
        print(f"   ❌ Falha: {e}")

    # 5. Testar: Criar Paciente (Com ID Aleatório para não repetir)
    rnd_id = random.randint(10000, 99999)
    new_patient = {
        "full_name": f"Demo User {rnd_id}",
        "phone": f"1199999{rnd_id}",
        "email": f"demo{rnd_id}@exemplo.com",
        "birth_date": "1990-01-01"
    }
    print(f"\n👤 [3/4] Criando Paciente: {new_patient['full_name']}...")
    try:
        # Nota: O service mapeia 'full_name' -> 'Name' (PascalCase) internamente agora
        patient_id = await client.create_patient(new_patient)
        print(f"   ✅ Sucesso! Paciente Criado. ID Clinicorp: {patient_id}")
    except Exception as e:
        print(f"   ❌ Falha: {e}")

    # 6. Testar: Listar Agendamentos (Usando o filtro de data correto)
    print(f"\ncard_index [4/4] Listando Agendamentos do Dia...")
    try:
        appts = await client.get_appointments(tomorrow)
        print(f"   ✅ Sucesso! Retornou {len(appts)} agendamentos.")
        if appts:
             print(f"   Exemplo: {appts[0]}")
        else:
             print("   (Nenhum agendamento encontrado para hoje, mas a consulta funcionou (200 OK))")
    except Exception as e:
         print(f"   ❌ Falha: {e}")

    print("\n✨ Demonstração Concluída!")

if __name__ == "__main__":
    asyncio.run(main())
