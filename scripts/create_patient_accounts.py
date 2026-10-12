import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, ClientOptions

def main():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    # Must use service role key for auth admin operations!
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        print("Please add SUPABASE_SERVICE_ROLE_KEY to your .env file to run this script.")
        return
        
    # We use service role key here
    client = create_client(url, key)
    
    dataset_path = "data/raw/agentic_ai_patient_context_15000_with_names.xlsx"
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return
        
    print("Loading synthetic dataset...")
    df = pd.read_excel(dataset_path)
    
    # We only process the patients found in the excel file
    total_processed = 0
    created = 0
    already_existed = 0
    unmatched_patients = 0
    failed = 0
    
    print("Fetching existing patients from Supabase...")
    # Fetch all patients from Supabase
    # Note: Supabase limit is typically 1000, so we paginate
    all_supabase_patients = {}
    
    # Pagination
    limit = 1000
    offset = 0
    while True:
        res = client.table("patients").select("id, patient_id").range(offset, offset + limit - 1).execute()
        data = res.data
        if not data:
            break
        for row in data:
            if row.get("patient_id"):
                all_supabase_patients[row["patient_id"]] = row["id"]
        
        offset += limit
        if len(data) < limit:
            break
            
    print(f"Found {len(all_supabase_patients)} patients in the database.")
    
    # Fetch existing mappings
    print("Fetching existing mappings...")
    existing_mappings = set()
    offset = 0
    while True:
        res = client.table("patient_auth").select("patient_id").range(offset, offset + limit - 1).execute()
        data = res.data
        if not data:
            break
        for row in data:
            existing_mappings.add(row["patient_id"])
        
        offset += limit
        if len(data) < limit:
            break
            
    print(f"Found {len(existing_mappings)} existing authentication mappings.")
    
    print("\nCreating patient accounts...")
    
    for index, row in df.iterrows():
        patient_code = str(row["patient_id"]).strip()
        total_processed += 1
        
        # Match to Supabase patients table
        patient_uuid = all_supabase_patients.get(patient_code)
        
        if not patient_uuid:
            unmatched_patients += 1
            continue
            
        if patient_uuid in existing_mappings:
            already_existed += 1
            continue
            
        # Create Auth account
        email = f"{patient_code.lower()}@demo.healthcare.local"
        password = f"Patient@{patient_code.replace('SYN', '')}"
        
        try:
            # Check if user already exists in auth.users by trying to create
            # Or use admin API to create user
            # Supabase Python Client Admin API:
            user_res = client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })
            
            auth_user_id = user_res.user.id
            
            # Create mapping
            client.table("patient_auth").insert({
                "auth_user_id": auth_user_id,
                "patient_id": patient_uuid
            }).execute()
            
            # Also update the patients table with the email so RLS policies work seamlessly
            client.table("patients").update({"email": email}).eq("id", patient_uuid).execute()
            
            created += 1
            if created % 100 == 0:
                print(f"  Created {created} accounts...")
                
        except Exception as e:
            err_msg = str(e)
            if "already been registered" in err_msg or "User already exists" in err_msg:
                # The auth user exists but mapping doesn't. 
                # This could happen if script failed midway.
                # In this demo script we'll just consider it failed or attempt to recover, 
                # but to keep it simple we count it as failed for manual intervention.
                failed += 1
            else:
                failed += 1
                
    print(f"\nProcessed: {total_processed}")
    print(f"Created: {created}")
    print(f"Already existed: {already_existed}")
    print(f"Unmatched patients: {unmatched_patients}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    main()
