import requests
import json
import random
import time

# URL do seu backend local
URL = "http://127.0.0.1:8000/webhooks/whatsapp"

# Cenários de Teste (Simulando Links de Anúncios)
SCENARIOS = [
    {
        "name": "Maria (Google)", 
        "phone": "5511999990001", 
        "msg": "Olá, vi no Google e quero agendar uma avaliação para meu filho."
    },
    {
        "name": "João (Instagram)", 
        "phone": "5511999990002", 
        "msg": "Oi, vi no Insta de vocês sobre o aparelho invisível. Quanto custa?"
    },
    {
        "name": "Carla (Indicação)", 
        "phone": "5511999990003", 
        "msg": "Boa tarde, recebi indicação da Dra. Fernanda."
    },
    {
        "name": "Pedro (Orgânico)", 
        "phone": "5511999990004", 
        "msg": "Gostaria de saber o horário de funcionamento."
    }
]

def simulate_lead(lead):
    payload = {
        "data": {
            "key": {
                "remoteJid": f"{lead['phone']}@s.whatsapp.net",
                "fromMe": False
            },
            "pushName": lead['name'],
            "message": {
                "conversation": lead['msg']
            }
        }
    }
    
    try:
        print(f"Enviando Lead: {lead['name']} ({lead['msg']})...")
        res = requests.post(URL, json=payload)
        print(f"Status: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"Erro ao conectar: {e}")

if __name__ == "__main__":
    print("--- Simulador de Leads Bem-Querer ---")
    print("Certifique-se que o Backend está rodando na porta 8000!")
    print("-------------------------------------")
    
    for lead in SCENARIOS:
        simulate_lead(lead)
        time.sleep(1) # Pausa dramática
        
    print("\nTodos os leads enviados! Verifique o banco de dados/frontend.")
