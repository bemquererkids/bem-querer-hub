from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
import json
import os
import uuid
from app.services.gpt_service import get_gpt_service

router = APIRouter()

# --- Schemas ---
class KnowledgeItem(BaseModel):
    id: Optional[str] = None
    category: str
    content: str
    keywords: List[str] = []

class KnowledgeBaseResponse(BaseModel):
    items: List[KnowledgeItem]

class PersonaConfig(BaseModel):
    assistant_name: str
    clinic_name: str
    tone: str
    target_audience: str

# --- Helpers ---
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge_base.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "clinic_integrations.json")

def load_kb():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_kb(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Endpoints ---

@router.get("/knowledge", response_model=List[KnowledgeItem])
async def get_knowledge_base():
    """List all knowledge base items"""
    return load_kb()

@router.post("/knowledge", response_model=KnowledgeItem)
async def save_knowledge_item(item: KnowledgeItem):
    """Add or Update a knowledge item"""
    data = load_kb()
    
    if item.id:
        # Update
        for idx, existing in enumerate(data):
            if existing["id"] == item.id:
                data[idx] = item.dict()
                save_kb(data)
                return item
        # If ID provided but not found, treat as new? Or error? Let's treat as new.
    
    # Create
    new_item = item.dict()
    new_item["id"] = str(uuid.uuid4())
    data.append(new_item)
    save_kb(data)
    return new_item

@router.delete("/knowledge/{item_id}")
async def delete_knowledge_item(item_id: str):
    """Delete a knowledge item"""
    data = load_kb()
    new_data = [d for d in data if d["id"] != item_id]
    if len(new_data) == len(data):
        raise HTTPException(status_code=404, detail="Item not found")
    
    save_kb(new_data)
    return {"status": "success", "deleted_id": item_id}

@router.get("/persona", response_model=PersonaConfig)
async def get_persona_config():
    """Get current AI Persona config"""
    data = load_config()
    persona = data.get("ai_persona", {
        "assistant_name": "Carol",
        "clinic_name": "Bem-Querer Odontologia",
        "tone": "Empático, acolhedor e eficiente.",
        "target_audience": "Mães preocupadas e pacientes ocupados."
    })
    return persona

@router.post("/persona")
async def update_persona_config(config: PersonaConfig):
    """Update AI Persona config"""
    data = load_config()
    data["ai_persona"] = config.dict()
    save_config(data)
    
    # Reload service context if needed
    # The service loads on each request or we can force it, 
    # but process_message re-reads config if we implement it that way.
    # checking gpt_service.py... it reads on process_message call? 
    # It reads self.context_config in __init__. We might need to refresh it.
    
    service = get_gpt_service()
    if service:
        service.context_config = config.dict() # Force update in-memory
        
    return config
