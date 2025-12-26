from fastapi import APIRouter
from app.core.database import get_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/test-webhook-token")
async def test_webhook_token():
    """
    Endpoint de debug para testar se o verify_token está acessível no banco
    """
    try:
        supabase = get_supabase()
        
        # Testar conexão
        result = supabase.table('clinic_integrations').select('*').eq('type', 'whatsapp').execute()
        
        if not result.data:
            return {
                "status": "error",
                "message": "Nenhum registro whatsapp encontrado",
                "supabase_connected": True
            }
        
        record = result.data[0]
        
        return {
            "status": "success",
            "supabase_connected": True,
            "record_found": True,
            "verify_token": record.get('verify_token'),
            "verify_token_matches": record.get('verify_token') == '0addb8a5-a6cd-473d-af75-b8777f510fd9',
            "is_active": record.get('is_active'),
            "phone_number_id": record.get('phone_number_id'),
            "full_record": record
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "supabase_connected": False
        }
