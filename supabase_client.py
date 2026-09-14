import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing from .env")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)



# ============================================================
# REGISTER NEW PATIENT
# ============================================================

def register_patient(name, age, gender, dob, medical_history, medications):
    response = (
        supabase
        .table("patients")
        .select("patient_id")
        .order("patient_id", desc=True)
        .limit(1)
        .execute()
    )
    
    if response.data:
        last_id = response.data[0]["patient_id"]
        try:
            num = int(last_id.replace("P", ""))
            new_id = f"P{num + 1:03d}"
        except:
            new_id = "P001"
    else:
        new_id = "P001"
        
    patient_data = {
        "patient_id": new_id,
        "name": name,
        "age": age,
        "gender": gender,
        "date_of_birth": dob
    }
    
    patient_res = supabase.table("patients").insert(patient_data).execute()
    if not patient_res.data:
        raise Exception("Failed to insert new patient.")
        
    patient_uuid = patient_res.data[0]["id"]
    
    if medical_history:
        if isinstance(medical_history, str):
            history_items = [item.strip() for item in medical_history.split(",") if item.strip()]
        else:
            history_items = medical_history
            
        if history_items:
            conditions_data = [
                {"patient_id": patient_uuid, "condition_name": item}
                for item in history_items
            ]
            supabase.table("conditions").insert(conditions_data).execute()
            
    if medications:
        if isinstance(medications, str):
            med_items = [item.strip() for item in medications.split(",") if item.strip()]
        else:
            med_items = medications
            
        if med_items:
            meds_data = [
                {"patient_id": patient_uuid, "medication_name": item}
                for item in med_items
            ]
            supabase.table("medications").insert(meds_data).execute()
            
    return new_id

# ============================================================
# GET ALL PATIENTS
# ============================================================

def get_patients():

    response = (
        supabase
        .table("patients")
        .select("*")
        .order("patient_id")
        .execute()
    )

    return response.data


# ============================================================
# GET COMPLETE PATIENT PROFILE
# ============================================================

def get_patient_profile(patient_id):

    # --------------------------------------------------------
    # Patient
    # --------------------------------------------------------

    patient_response = (
        supabase
        .table("patients")
        .select("*")
        .eq("patient_id", patient_id)
        .limit(1)
        .execute()
    )

    if not patient_response.data:
        return None

    patient = patient_response.data[0]


    patient_uuid = patient["id"]


    # --------------------------------------------------------
    # Medical History
    # --------------------------------------------------------

    conditions_response = (
        supabase
        .table("conditions")
        .select("*")
        .eq("patient_id", patient_uuid)
        .execute()
    )

    conditions = conditions_response.data


    # --------------------------------------------------------
    # Medications
    # --------------------------------------------------------

    medications_response = (
        supabase
        .table("medications")
        .select("*")
        .eq("patient_id", patient_uuid)
        .execute()
    )

    medications = medications_response.data


    # --------------------------------------------------------
    # Symptoms
    # --------------------------------------------------------

    symptoms_response = (
        supabase
        .table("symptoms")
        .select("*")
        .eq("patient_id", patient_uuid)
        .execute()
    )

    symptoms = symptoms_response.data


    # --------------------------------------------------------
    # Vital Observations
    # --------------------------------------------------------

    observations_response = (
        supabase
        .table("observations")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("recorded_at", desc=True)
        .execute()
    )

    observations = observations_response.data


    # --------------------------------------------------------
    # Latest observation
    # --------------------------------------------------------

    latest_observation = (
        observations[0]
        if observations
        else {}
    )


    # --------------------------------------------------------
    # Convert Supabase data into the same structure
    # expected by your existing Streamlit application
    # --------------------------------------------------------

    return {

        "patient_id":
            patient.get("patient_id"),

        "patient_uuid":
            patient_uuid,

        "patient_name":
            patient.get("name"),

        "age":
            patient.get("age"),

        "gender":
            patient.get("gender"),

        "medical_history": [

            condition["condition_name"]

            for condition in conditions

            if condition.get("condition_name")
        ],

        "medications": [

            medication["medication_name"]

            for medication in medications

            if medication.get("medication_name")
        ],

        "symptoms": [

            symptom["symptom_name"]

            for symptom in symptoms

            if symptom.get("symptom_name")
        ],

        "vitals": {

            "temperature":
                latest_observation.get("temperature"),

            "heart_rate":
                latest_observation.get("heart_rate"),

            "systolic_bp":
                latest_observation.get("systolic_bp"),

            "diastolic_bp":
                latest_observation.get("diastolic_bp"),

            "spo2":
                latest_observation.get("spo2")
        }
    }


# ============================================================
# SAVE PATIENT ASSESSMENT
# ============================================================

def save_assessment(
    patient_id, 
    top_prediction, 
    confidence, 
    confidence_level, 
    agent_decision, 
    agent_reason, 
    risk_flags, 
    medication_alerts, 
    briefing_summary,
    temperature=None,
    heart_rate=None,
    systolic_bp=None,
    diastolic_bp=None,
    spo2=None
):
    """
    Saves a completed assessment and its associated data to Supabase.
    """
    
    # 1. Resolve the patient UUID
    patient_response = (
        supabase
        .table("patients")
        .select("id")
        .eq("patient_id", patient_id)
        .limit(1)
        .execute()
    )
    
    if not patient_response.data:
        raise ValueError(f"Patient ID {patient_id} not found in Supabase. Cannot save assessment.")
        
    patient_uuid = patient_response.data[0]["id"]
    
    # 2. Insert into assessments
    assessment_data = {
        "patient_id": patient_uuid,
        "top_prediction": top_prediction,
        "confidence": confidence,
        "confidence_level": confidence_level,
        "agent_decision": agent_decision,
        "agent_reason": agent_reason
    }
    
    assessment_response = (
        supabase
        .table("assessments")
        .insert(assessment_data)
        .execute()
    )
    
    if not assessment_response.data:
        raise RuntimeError("Failed to insert assessment record.")
        
    assessment_id = assessment_response.data[0]["id"]
    
    # 3. Insert risk flags
    if risk_flags:
        risk_flags_data = [
            {
                "assessment_id": assessment_id,
                "patient_id": patient_uuid,
                "risk_type": "Vital Sign Risk",
                "risk_message": flag
            }
            for flag in risk_flags
        ]
        
        supabase.table("risk_flags").insert(risk_flags_data).execute()
        
    # 4. Insert medication alerts
    if medication_alerts:
        med_alerts_data = [
            {
                "assessment_id": assessment_id,
                "patient_id": patient_uuid,
                "medication_1": alert.get("medication_1"),
                "medication_2": alert.get("medication_2"),
                "severity": alert.get("severity"),
                "alert_message": alert.get("message", "Potential interaction detected.")
            }
            for alert in medication_alerts
        ]
        
        supabase.table("medication_alerts").insert(med_alerts_data).execute()
        
    # 5. Insert doctor briefing
    if briefing_summary:
        briefing_data = {
            "assessment_id": assessment_id,
            "patient_id": patient_uuid,
            "summary": briefing_summary
        }
        
        supabase.table("doctor_briefings").insert(briefing_data).execute()
        

    # 6. Insert manual vitals into observations
    if temperature or heart_rate or systolic_bp or diastolic_bp or spo2:
        obs_data = {
            "patient_id": patient_uuid,
            "temperature": temperature,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "spo2": spo2,
            "source": "MANUAL"
        }
        # Filter out None values
        obs_data = {k: v for k, v in obs_data.items() if v is not None}
        supabase.table("observations").insert(obs_data).execute()

    return assessment_id



# ============================================================
# GET PATIENT ASSESSMENT HISTORY
# ============================================================

def get_assessment_history_by_uuid(patient_uuid):
    """
    Retrieves the assessment history for a specific patient using their UUID.
    """
    
    if not patient_uuid:
        return []
    
    # Get assessments
    assessments_response = (
        supabase
        .table("assessments")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("created_at", desc=True)
        .execute()
    )
    
    assessments = assessments_response.data
    
    # We could also fetch associated risk_flags and doctor_briefings here if needed
    # But for the UI history list, the main assessment details are usually enough.
    return assessments

# ============================================================
# DOCTOR DASHBOARD: ADDITIONAL DATA FETCHERS
# ============================================================

def get_patient_observations(patient_uuid):
    if not patient_uuid:
        return []
    response = (
        supabase
        .table("observations")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("recorded_at", desc=True)
        .execute()
    )
    return response.data

def get_patient_risk_flags(patient_uuid):
    if not patient_uuid:
        return []
    response = (
        supabase
        .table("risk_flags")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data

def get_patient_medication_alerts(patient_uuid):
    if not patient_uuid:
        return []
    response = (
        supabase
        .table("medication_alerts")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data

def get_patient_doctor_briefings(patient_uuid):
    if not patient_uuid:
        return []
    response = (
        supabase
        .table("doctor_briefings")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data