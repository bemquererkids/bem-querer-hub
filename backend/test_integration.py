"""
Integration Test Script
Tests the Clinicorp Adapter in Mock Mode.
"""
import asyncio
import sys
import os

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.clinicorp_service import ClinicorpClient

async def main():
    print("--- Iniciando Teste de Integração (Modo Mock) ---")
    
    # 1. Initialize Client (Empty config triggers Mock Mode)
    client = ClinicorpClient(clinic_id="test_clinic", integration_config={})
    
    # 2. Test Availability
    print("\n1. Consultando Horários para 2025-12-22...")
    slots = await client.check_availability("2025-12-22")
    print(f"   Resultado: Encontrados {len(slots)} horários.")
    for slot in slots:
        print(f"   - {slot['time']} com {slot['professional']}")
        
    # 3. Test Scheduling
    print("\n2. Tentando Agendar Paciente 'João da Silva'...")
    try:
        # Step A: Create Patient
        p_id = await client.create_patient({"full_name": "João da Silva", "phone": "5511999999999"})
        print(f"   [OK] Paciente criado/identificado. ID Externo: {p_id}")
        
        # Step B: Create Appointment
        a_id = await client.create_appointment({
            "patient_id": p_id,
            "date": "2025-12-22",
            "time": "14:00"
        })
        print(f"   [OK] Consulta agendada! ID do Agendamento: {a_id}")
        
    except Exception as e:
        print(f"   [ERRO] Falha no agendamento: {e}")

    print("\n--- Teste Concluído com Sucesso ---")

if __name__ == "__main__":
    asyncio.run(main())
