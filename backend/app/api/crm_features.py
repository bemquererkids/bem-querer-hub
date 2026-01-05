from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_supabase

router = APIRouter(prefix="/api", tags=["crm-features"])

# --- Notes Endpoints ---

class NoteModel(BaseModel):
    id: str
    content: str
    created_at: str

class CreateNoteRequest(BaseModel):
    content: str

@router.get("/notes/{conversation_id}", response_model=List[NoteModel])
async def get_notes(conversation_id: str):
    """Get notes for a conversation"""
    try:
        supabase = get_supabase()
        res = supabase.table("crm_notes") \
            .select("*") \
            .eq("conversation_id", conversation_id) \
            .order("created_at", desc=True) \
            .execute()
        
        notes = []
        if res.data:
            for n in res.data:
                notes.append({
                    "id": n["id"],
                    "content": n["content"],
                    "created_at": n["created_at"]
                })
        return notes
    except Exception as e:
        print(f"Error fetching notes: {e}")
        return []

@router.post("/notes/{conversation_id}")
async def create_note(conversation_id: str, request: CreateNoteRequest):
    """Create a note for a conversation"""
    try:
        supabase = get_supabase()
        new_note = {
            "conversation_id": conversation_id,
            "content": request.content,
            "created_at": datetime.now().isoformat()
        }
        res = supabase.table("crm_notes").insert(new_note).execute()
        return {"status": "success", "note": res.data[0] if res.data else {}}
    except Exception as e:
        print(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Reminders Endpoints ---

class ReminderModel(BaseModel):
    id: str
    title: str
    due_at: str
    status: str

class CreateReminderRequest(BaseModel):
    title: str
    due_at: str

@router.get("/reminders/{conversation_id}", response_model=List[ReminderModel])
async def get_reminders(conversation_id: str):
    """Get reminders for a conversation"""
    try:
        supabase = get_supabase()
        res = supabase.table("crm_reminders") \
            .select("*") \
            .eq("conversation_id", conversation_id) \
            .order("due_at", desc=False) \
            .execute()
        
        reminders = []
        if res.data:
            for r in res.data:
                reminders.append({
                    "id": r["id"],
                    "title": r["title"],
                    "due_at": r["due_at"],
                    "status": r.get("status", "pending")
                })
        return reminders
    except Exception as e:
        print(f"Error fetching reminders: {e}")
        return []

@router.post("/reminders/{conversation_id}")
async def create_reminder(conversation_id: str, request: CreateReminderRequest):
    """Create a reminder for a conversation"""
    try:
        supabase = get_supabase()
        new_reminder = {
            "conversation_id": conversation_id,
            "title": request.title,
            "due_at": request.due_at,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        res = supabase.table("crm_reminders").insert(new_reminder).execute()
        return {"status": "success", "reminder": res.data[0] if res.data else {}}
    except Exception as e:
        print(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))
