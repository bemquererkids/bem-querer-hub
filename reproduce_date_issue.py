
import asyncio
import os
import sys
from datetime import datetime

# Add backend directory to python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

from app.services.gemini_service import GeminiService

async def reproduce_issue():
    service = GeminiService()
    
    # Test case: asking for "amanhã" (tomorrow)
    # Expected: The service should detect "amanhã" and fetch slots for tomorrow.
    # Current Behavior (Hypothesis): It fetches slots for today.
    
    msg = "Tem horário para amanhã?"
    print(f"User Message: '{msg}'")
    
    # Needs a mock context to work?
    context = {"patient_name": "Test User"}
    
    # We want to intercept the context BEFORE it sends to Gemini Model to see what slots were fetched.
    # But process_message does it internally.
    # We can inspect the returned response or add logging. 
    # Since I cannot easily spy on internal variables without modifying code, 
    # I will rely on the printed logs if I run this with stdout enabled, or 
    # I can check the 'context' dictionary assuming it passes by reference and gets modified?
    # Inspecting line 136 of gemini_service.py: context['clinic_slots'] = slots
    # Yes, it modifies the context dict!
    
    response = await service.process_message(msg, context=context)
    
    model_context_slots = context.get('clinic_slots', 'Not Found')
    print(f"\n[DEBUG] Slots in Context: {model_context_slots}")
    
    if model_context_slots != 'Not Found':
         print("Slots were fetched.")
         # How to verify if it was for today or tomorrow?
         # The service logs doesn't show the date in the context structure stored in 'clinic_slots' unless the slot object has the date.
         # But the printed string in context_str (line 137) is local to the function.
         # Wait, looking at line 137: context_str += f"\n\n[SISTEMA] Horários disponíveis HOJE ({date_str}): {slots}"
         # It explicitly says "HOJE" and uses 'date_str' which is calculated as now().
         pass
         
    # To be certain, I'll modify the loop to print what happened.
    print("Test finished.")

if __name__ == "__main__":
    asyncio.run(reproduce_issue())
