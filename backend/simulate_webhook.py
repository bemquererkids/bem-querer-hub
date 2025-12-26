
import asyncio
import sys
import os
import httpx
import json

async def main():
    print("--- Simulating WhatsApp Webhook ---")
    
    # 1. Payload mimicking UazAPI
    payload = {
        "event": "messages.upsert",
        "instance": "bemquerer",
        "data": {
            "key": {
                "remoteJid": "5511999998888@s.whatsapp.net",
                "fromMe": False,
                "id": "MSG_SIM_001"
            },
            "pushName": "Visitante Simulado",
            "message": {
                "conversation": "Carol, tem horário vago pra hoje?"
            },
            "messageTimestamp": 1672531200
        }
    }
    
    # 2. Send POST
    async with httpx.AsyncClient() as client:
        try:
            print("Sending 'Carol, tem horário vago pra hoje?'...")
            resp = await client.post("http://localhost:8000/api/webhooks/whatsapp", json=payload)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")
            
            print("\nCheck the backend terminal logs to see the AI response!")
            print("(Or check the database if you could, but logs are easier)")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
