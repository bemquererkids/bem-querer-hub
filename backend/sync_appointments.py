"""
Sync Appointments Script
Fetches REAL appointments from Clinicorp using the configured credentials.
"""
import asyncio
import sys
import os
from datetime import date

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clinicorp_service import ClinicorpClient

# CONFIGURACAO DE TESTE (Mesma da tela de settings)
TEST_CONFIG = {
    "client_id": "bemquerer",
    "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
}

async def main():
    print(f"--- Iniciando Sincronizacao Real (Clinicorp) ---")
    print(f"Data: {date.today()}")
    
    # 1. Inicializar Cliente
    client = ClinicorpClient(clinic_id="bemquerer_prod", integration_config=TEST_CONFIG)
    
    try:
        # 2. Buscar Agendamentos de Hoje
        print("\n1. Buscando agendamentos...")
        appointments = await client.get_appointments(str(date.today()))
        
        if not appointments:
            print("   [INFO] Nenhum agendamento encontrado para hoje ou API retornou lista vazia.")
            print("   (Dica: Verifique se ha pacientes agendados para HOJE no sistema Clinicorp)")
        else:
            print(f"   [SUCESSO] Encontrados {len(appointments)} agendamentos!")
            for appt in appointments:
                # Tenta extrair dados comuns, adaptando conforme o retorno real da API
                paciente = appt.get('patientName') or appt.get('patient', {}).get('name') or 'Desconhecido'
                hora = appt.get('time') or appt.get('start') or '??:??'
                status = appt.get('status') or '---'
                print(f"   - {hora} | {paciente} ({status})")

    except Exception as e:
        print(f"   [ERRO] Falha na busca: {e}")
        print("   (Verifique se o Token tem permissão para ler agendamentos)")

    print("\n--- Fim da Sincronizacao ---")

if __name__ == "__main__":
    asyncio.run(main())