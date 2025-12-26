
import asyncio
import json
from app.services.clinicorp_service import ClinicorpClient

async def main():
    # Load Credentials
    with open("clinic_integrations.json", "r") as f:
        creds = json.load(f)["clinicorp"]
    
    client = ClinicorpClient("debug", creds)
    
    # 1. Find Vanessa
    print("Finding Vanessa...")
    profs = await client.get_professionals()
    vanessa = next((p for p in profs if "Vanessa" in p["name"]), None)
    
    if not vanessa:
        print("Vanessa not found!")
        return
        
    print(f"Found: {vanessa['name']} (ID: {vanessa['id']})")
    
    # 2. Check Availability
    date = "2026-01-05" 
    # date = "2026-01-06" # Check next day too if needed
    
    print(f"Checking availability for {date}...")
    
    # NOTE: In the real app we filter. Here we want to see everything to debug the ID.
    # We pass None for filtering in this debug manual call IF we want raw. 
    # But wait, we want to test check_availability's internal logic?
    # No, check_availability logic is inside the class.
    
    # Let's call the class method with ID to see if it filters correctly or returns empty.
    print(f"Calling client.check_availability('{date}', professional_id='{str(vanessa['id'])}')")
    slots = await client.check_availability(date, professional_id=str(vanessa['id']))
    
    print(f"\nFiltered Slots (Count: {len(slots)}):")
    print(json.dumps(slots, indent=2))
    
    if len(slots) == 0:
        print("\n--- DEBUG: WHY EMPTY? ---")
        print("Fetching RAW list without ID filter to compare IDs...")
        raw_slots = await client.check_availability(date) # No ID = Raw list (per my previous edit logic? No, previous edit filters ONLY if ID passed)
        # Wait, if I pass None to check_availability, it returns filtered list?
        # My code: if professional_id: ... return filtered. else return results.
        
        # so lets call with None
        raw_slots = await client.check_availability(date, professional_id=None)
        
        unique_ids = set()
        for s in raw_slots:
            unique_ids.add(str(s.get("ProfessionalId") or s.get("professionalId")))
            
        print(f"Unique Professional IDs in RAW response: {unique_ids}")
        print(f"Target ID was: {str(vanessa['id'])}")
        
        if str(vanessa['id']) in unique_ids:
             print(">> MATCH EXISTED in RAW! The filter logic failed?")
        else:
             print(">> TARGET ID NOT IN RAW. She really has no slots, or API uses different ID in slots.")

if __name__ == "__main__":
    asyncio.run(main())
