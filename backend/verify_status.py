from app.services.uazapi_service import get_uazapi_service
import sys
import json
from dotenv import load_dotenv

load_dotenv()

def verify_lead(phone):
    print(f"🔍 Consultando Lead na UazAPI: {phone}")
    uaz = get_uazapi_service()
    
    # Normaliza
    clean_phone = uaz.normalize_phone(phone)
    chat_id = f"{clean_phone}@s.whatsapp.net"
    
    # Endpoint /chat/find para buscar dados detalhados
    # Ou tentar ler via algum getLead se existir, mas vamos tentar find
    url = uaz._get_url("/chat/find")
    params = {"token": uaz.token}
    
    # Payload de busca pelo ID especifico
    payload = {
        "where": {
            "id": chat_id
        }
    }
    
    try:
        import requests
        res = requests.post(url, json=payload, params=params)
        data = res.json()
        
        if isinstance(data, list) and len(data) > 0:
            lead = data[0]
            print("\n📋 DADOS ENCONTRADOS NA UAZAPI:")
            print(f"Nome: {lead.get('wa_name')}")
            print(f"Status (CRM): {lead.get('lead_status')}")
            print(f"Tags/Etiquetas: {lead.get('lead_tags')}")
            print("-" * 30)
            print("Raw: ", json.dumps(lead, indent=2))
        else:
            print("❌ Lead não encontrado ou retorno vazio.")
            print(f"Resposta: {data}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    verify_lead("5511993308484")
