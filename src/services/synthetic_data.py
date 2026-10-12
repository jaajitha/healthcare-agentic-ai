import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_synthetic_dataset():
    dataset_path = "data/raw/agentic_ai_patient_context_15000_with_names.xlsx"
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        return None
    return pd.read_excel(dataset_path)

def get_synthetic_patient_by_id(patient_id):
    patient_id = str(patient_id).strip()
    
    try:
        df = load_synthetic_dataset()
        if df is None:
            return None
        syn_patient = df[df['patient_id'] == patient_id]
        
        if not syn_patient.empty:
            row = syn_patient.iloc[0]
            # Map synthetic patient to the loaded_patient format
            return {
                "patient_id": row["patient_id"],
                "patient_name": row["patient_name"] if "patient_name" in row else "Synthetic Patient",
                "age": int(row["age"]),
                "gender": str(row["sex"]),
                "patient_uuid": f"syn-{row['patient_id']}",
                "vitals": {
                    "temperature": float(row["temperature_c"]),
                    "heart_rate": int(row["heart_rate_bpm"]),
                    "systolic_bp": int(row["systolic_bp_mmhg"]),
                    "diastolic_bp": int(row["diastolic_bp_mmhg"]),
                    "spo2": float(row["spo2_percent"])
                },
                "medical_history": [m.strip() for m in str(row["medical_history"]).split(",") if m.strip()],
                "medications": [m.strip() for m in str(row["current_medications"]).split(",") if m.strip()],
                "symptoms": [s.strip() for s in str(row["symptoms_text"]).split(",") if s.strip()],
                "prognosis": str(row.get("prognosis", ""))
            }
        
        print(f"Patient lookup:\nID = {patient_id}\nSource = 15K synthetic dataset\nFound = False")
        return None
    except Exception as e:
        print(f"Patient lookup:\nID = {patient_id}\nSource = 15K synthetic dataset\nException: {e}")
        return None
