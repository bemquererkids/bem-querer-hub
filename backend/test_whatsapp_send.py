"""
Test WhatsApp Send Script
Uses UazAPI to send a text message.
"""
import asyncio
import sys
import httpx

# Configuração (Coloque sua URL e Token REAIS aqui para testar)
UAZAPI_URL = "https://api.uazapi.com" 
INSTANCE_ID = "instance123"
TOKEN = "token123"

# Telefone de Destino (Seu número)
DESTINO = "5511999999999" 

async def send_message():
    print(f"--- Teste de Envio WhatsApp (UazAPI) ---")
    
    url = f"{UAZAPI_URL}/message/text"
    headers = {
        "apikey": TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "number": DESTINO,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": "Olá! Esta é uma mensagem de teste do Bem-Querer Hub. 🦷"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Enviando para {DESTINO}...")
            # Uncomment to really send if you have creds
            # response = await client.post(url, json=payload, headers=headers)
            # print(f"Status: {response.status_code}")
            # print(f"Body: {response.text}")
            
            # Simulation output
            print("[SIMULAÇÃO] Mensagem enviada com sucesso (HTTP 200).")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(send_message())
