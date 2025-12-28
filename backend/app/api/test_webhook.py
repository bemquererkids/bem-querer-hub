from fastapi import APIRouter
from app.core.database import get_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/test", tags=["test"])

@router.get("/webhook-token")
async def test_webhook_token():
    """
    Endpoint de teste para verificar se conseguimos acessar o verify_token
    """
    try:
        supabase = get_supabase()
        
        # Buscar todos registros whatsapp
        result = supabase.table('clinic_integrations').select('*').eq('type', 'whatsapp').execute()
        
        if not result.data:
            return {
                "status": "error",
                "message": "Nenhum registro whatsapp encontrado",
                "records": 0
            }
        
        records_info = []
        for record in result.data:
            records_info.append({
                "id": record.get('id'),
                "verify_token": record.get('verify_token'),
                "verify_token_length": len(record.get('verify_token', '')),
                "is_active": record.get('is_active'),
                "phone_number_id": record.get('phone_number_id'),
                "matches_expected": record.get('verify_token') == '0addb8a5-a6cd-473d-af75-b8777f510fd9'
            })
        
        return {
            "status": "success",
            "total_records": len(result.data),
            "records": records_info,
            "expected_token": "0addb8a5-a6cd-473d-af75-b8777f510fd9"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
