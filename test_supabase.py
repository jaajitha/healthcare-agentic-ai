import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not url or not key:
    print("❌ Supabase credentials not found.")
    exit()

supabase = create_client(url, key)

response = supabase.table("patients").select("*").execute()

print("✅ Supabase connected successfully!")
print(f"Patients found: {len(response.data)}")

for patient in response.data:
    print(
        patient["patient_id"],
        "-",
        patient["name"],
        "- UUID:",
        patient["id"]
    )

print("\n--- ASSESSMENTS DETAILS ---")
assessments = supabase.table("assessments").select("*").execute()
for a in assessments.data:
    print(f"[{a['patient_id']}] ML: {a.get('top_prediction')} | Agent: {a.get('agent_decision')}")