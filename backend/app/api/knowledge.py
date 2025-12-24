"""
Knowledge Base API Router
Endpoints for managing documents and embeddings.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.services.embedding_service import embedding_service
from app.core.database import get_supabase
import PyPDF2
import io

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

# Schemas
class DocumentCreate(BaseModel):
    titulo: str
    tipo: str  # 'preco', 'politica', 'procedimento', 'faq', 'outro'
    conteudo: str
    clinica_id: str

class DocumentResponse(BaseModel):
    id: str
    titulo: str
    tipo: str
    conteudo: str
    ativo: bool
    criado_em: str

class SearchRequest(BaseModel):
    query: str
    clinica_id: str
    limit: Optional[int] = 5

class SearchResult(BaseModel):
    documento_id: str
    titulo: str
    chunk_text: str
    similarity: float

# Endpoints
@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    titulo: str = None,
    tipo: str = "outro",
    clinica_id: str = None
):
    """
    Upload de documento (PDF ou TXT) e geração de embeddings.
    """
    if not clinica_id:
        raise HTTPException(status_code=400, detail="clinica_id é obrigatório")
    
    try:
        # Ler arquivo
        content = await file.read()
        
        # Extrair texto
        if file.filename.endswith('.pdf'):
            texto = extract_text_from_pdf(content)
        elif file.filename.endswith('.txt'):
            texto = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado. Use PDF ou TXT")
        
        # Salvar documento no banco
        supabase = get_supabase()
        doc_response = supabase.table("documentos_conhecimento").insert({
            "clinica_id": clinica_id,
            "titulo": titulo or file.filename,
            "tipo": tipo,
            "conteudo": texto,
            "ativo": True
        }).execute()
        
        documento_id = doc_response.data[0]["id"]
        
        # Gerar embeddings
        chunks_count = await embedding_service.embed_document(documento_id, texto)
        
        return {
            "success": True,
            "documento_id": documento_id,
            "titulo": titulo or file.filename,
            "chunks_processados": chunks_count,
            "message": f"Documento processado com sucesso! {chunks_count} chunks criados."
        }
    
    except Exception as e:
        print(f"[Upload Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/text")
async def create_text_document(doc: DocumentCreate):
    """
    Criar documento a partir de texto direto (sem upload de arquivo).
    """
    try:
        supabase = get_supabase()
        
        # Salvar documento
        doc_response = supabase.table("documentos_conhecimento").insert({
            "clinica_id": doc.clinica_id,
            "titulo": doc.titulo,
            "tipo": doc.tipo,
            "conteudo": doc.conteudo,
            "ativo": True
        }).execute()
        
        documento_id = doc_response.data[0]["id"]
        
        # Gerar embeddings
        chunks_count = await embedding_service.embed_document(documento_id, doc.conteudo)
        
        return {
            "success": True,
            "documento_id": documento_id,
            "chunks_processados": chunks_count
        }
    
    except Exception as e:
        print(f"[Create Document Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents(clinica_id: str):
    """
    Listar todos os documentos de uma clínica.
    """
    try:
        supabase = get_supabase()
        response = supabase.table("documentos_conhecimento").select(
            "id, titulo, tipo, ativo, criado_em"
        ).eq("clinica_id", clinica_id).eq("ativo", True).execute()
        
        return {"documents": response.data}
    
    except Exception as e:
        print(f"[List Documents Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{documento_id}")
async def delete_document(documento_id: str):
    """
    Deletar documento (soft delete - marca como inativo).
    """
    try:
        supabase = get_supabase()
        supabase.table("documentos_conhecimento").update({
            "ativo": False
        }).eq("id", documento_id).execute()
        
        return {"success": True, "message": "Documento desativado"}
    
    except Exception as e:
        print(f"[Delete Document Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(request: SearchRequest):
    """
    Busca semântica em documentos (para debug/teste).
    """
    try:
        results = await embedding_service.search_documents(
            request.query,
            request.clinica_id,
            request.limit
        )
        
        return {"results": results}
    
    except Exception as e:
        print(f"[Search Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper Functions
def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extrai texto de um PDF."""
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        print(f"[PDF Extract Error] {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao extrair texto do PDF: {str(e)}")
