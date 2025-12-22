from typing import Tuple, Optional

class LeadSourceDetector:
    """
    Analisa o conteúdo da primeira mensagem para determinar a origem do Lead (Marketing).
    """
    
    PATTERNS = {
        'google_ads': ['vi no google', 'pelo google', 'anuncio google'],
        'instagram': ['vi no insta', 'pelo instagram', 'vi no story', 'anuncio insta'],
        'facebook': ['vi no face', 'pelo facebook', 'anuncio face'],
        'tiktok': ['vi no tiktok', 'pelo tiktok'],
        'indication': ['indicação', 'indicou', 'recomendou']
    }

    @classmethod
    def detect(cls, message_content: str) -> str:
        content_lower = message_content.lower()
        
        for source, keywords in cls.PATTERNS.items():
            if any(keyword in content_lower for keyword in keywords):
                return source
                
        return 'organic' # Origem desconhecida/direta

    @staticmethod
    def extract_utm(message_content: str) -> Optional[dict]:
        """
        Futuro: Se usarmos links encurtados que expandem no texto,
        podemos extrair códigos específicos aqui.
        """
        pass
