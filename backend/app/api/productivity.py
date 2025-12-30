from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import SupabaseClient

router = APIRouter()

# --- Models ---

class Note(BaseModel):
    id: str
    conversation_id: str
    content: str
    created_at: str

class CreateNoteRequest(BaseModel):
    conversation_id: str
    content: str

class Reminder(BaseModel):
    id: str
    conversation_id: str
    title: str
    due_at: str
    status: str
    created_at: str

class CreateReminderRequest(BaseModel):
    conversation_id: str
    title: str
    due_at: str

class UpdateReminderStatusRequest(BaseModel):
    status: str

class TagRequest(BaseModel):
    tag: str

# --- Notes Endpoints ---

@router.get("/notes/{conversation_id}", response_model=List[Note])
async def get_notes(conversation_id: str):
    try:
        supabase = SupabaseClient.get_admin_client()
        res = supabase.table("crm_notes") \
            .select("*") \
            .eq("conversation_id", conversation_id) \
            .order("created_at", desc=True) \
            .execute()
        return res.data
    except Exception as e:
        print(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notes", response_model=Note)
async def create_note(req: CreateNoteRequest):
    try:
        supabase = SupabaseClient.get_admin_client()
        res = supabase.table("crm_notes") \
            .insert({
                "conversation_id": req.conversation_id,
                "content": req.content
            }) \
            .execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create note")
            
        return res.data[0]
    except Exception as e:
        print(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    try:
        supabase = SupabaseClient.get_admin_client()
        supabase.table("crm_notes").delete().eq("id", note_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Reminders Endpoints ---

@router.get("/reminders/{conversation_id}", response_model=List[Reminder])
async def get_reminders(conversation_id: str):
    try:
        supabase = SupabaseClient.get_admin_client()
        res = supabase.table("crm_reminders") \
            .select("*") \
            .eq("conversation_id", conversation_id) \
            .order("due_at", desc=False) \
            .execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reminders", response_model=Reminder)
async def create_reminder(req: CreateReminderRequest):
    try:
        supabase = SupabaseClient.get_admin_client()
        res = supabase.table("crm_reminders") \
            .insert({
                "conversation_id": req.conversation_id,
                "title": req.title,
                "due_at": req.due_at,
                "status": "pending"
            }) \
            .execute()
            
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create reminder")
            
        return res.data[0]
    except Exception as e:
        print(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/reminders/{reminder_id}/status")
async def update_reminder_status(reminder_id: str, req: UpdateReminderStatusRequest):
    try:
        supabase = SupabaseClient.get_admin_client()
        res = supabase.table("crm_reminders") \
            .update({"status": req.status}) \
            .eq("id", reminder_id) \
            .execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Tags Endpoints (Helper to add/remove specific tags easily) ---

@router.post("/tags/{conversation_id}")
async def add_tag(conversation_id: str, req: TagRequest):
    try:
        supabase = SupabaseClient.get_admin_client()
        # Fetch current tags
        res = supabase.table("whatsapp_conversations").select("tags").eq("id", conversation_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        current_tags = res.data[0].get("tags") or []
        if req.tag not in current_tags:
            current_tags.append(req.tag)
            supabase.table("whatsapp_conversations").update({"tags": current_tags}).eq("id", conversation_id).execute()
        
        return {"status": "success", "tags": current_tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tags/{conversation_id}")
async def remove_tag(conversation_id: str, req: TagRequest):
    try:
        supabase = SupabaseClient.get_admin_client()
        # Fetch current tags
        res = supabase.table("whatsapp_conversations").select("tags").eq("id", conversation_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        current_tags = res.data[0].get("tags") or []
        if req.tag in current_tags:
            current_tags = [t for t in current_tags if t != req.tag]
            supabase.table("whatsapp_conversations").update({"tags": current_tags}).eq("id", conversation_id).execute()
        
        return {"status": "success", "tags": current_tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
