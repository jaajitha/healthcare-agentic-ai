from supabase_client import (
    get_patients,
    get_patient,
    get_patient_conditions,
    get_patient_medications,
    get_patient_symptoms,
    get_patient_observations,
)

patients = get_patients()

print("\n==============================")
print("SUPABASE PATIENT TEST")
print("==============================")

print(f"Patients found: {len(patients)}")

for patient in patients:
    print(
        patient["patient_id"],
        "-",
        patient["name"]
    )

print("\n--- Testing P001 ---")

patient = get_patient("P001")

print("Patient:")
print(patient)

print("\nConditions:")
print(get_patient_conditions(patient["id"]))

print("\nMedications:")
print(get_patient_medications(patient["id"]))

print("\nSymptoms:")
print(get_patient_symptoms(patient["id"]))

print("\nObservations:")
print(get_patient_observations(patient["id"]))