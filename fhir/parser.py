import json
from datetime import date


FHIR_FILE = "fhir/patient.json"


def calculate_age(birth_date):
    """Calculate patient's age from FHIR birthDate."""
    try:
        birth = date.fromisoformat(birth_date)
    except (ValueError, TypeError):
        return None
    today = date.today()

    age = today.year - birth.year

    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1

    return age


def _load_fhir_database(file_path=FHIR_FILE):
    """Load the FHIR JSON array containing multiple patient bundles."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            db = json.load(file)
            if isinstance(db, list):
                return db
            else:
                return [db]  # Wrap in list if it's a single bundle
    except FileNotFoundError:
        raise RuntimeError(f"FHIR patient file not found at: {file_path}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Malformed JSON in FHIR patient file: {file_path}")


def get_available_patients(file_path=FHIR_FILE):
    """Return a list of available patients as dictionaries with id and name."""
    db = _load_fhir_database(file_path)
    patients = []
    
    for bundle in db:
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") == "Patient":
                pat_id = resource.get("id")
                names = resource.get("name", [])
                pat_name = "Not provided"
                if names:
                    first_name = " ".join(names[0].get("given", []))
                    last_name = names[0].get("family", "")
                    pat_name = f"{first_name} {last_name}".strip()
                patients.append({"id": pat_id, "name": pat_name})
                break  # Only one Patient resource per bundle in our mock
                
    return patients


def _parse_bundle(bundle):
    """Parse a single FHIR bundle into the unified patient profile."""
    patient = {}
    conditions = []
    vitals = {}
    medications = []

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        # -------------------------
        # Patient
        # -------------------------
        if resource_type == "Patient":

            patient["patient_id"] = resource.get("id")
            patient["gender"] = resource.get("gender")
            
            names = resource.get("name", [])
            if names:
                first_name = " ".join(names[0].get("given", []))
                last_name = names[0].get("family", "")
                patient["patient_name"] = f"{first_name} {last_name}".strip()

            birth_date = resource.get("birthDate")

            if birth_date:
                patient["birth_date"] = birth_date
                patient["age"] = calculate_age(birth_date)

        # -------------------------
        # Medical Conditions
        # -------------------------
        elif resource_type == "Condition":

            condition_name = (
                resource.get("code", {})
                .get("text")
            )

            if condition_name:
                conditions.append(condition_name)

        # -------------------------
        # Observations / Vitals
        # -------------------------
        elif resource_type == "Observation":

            code = (
                resource.get("code", {})
                .get("text", "")
                .lower()
            )

            value_quantity = resource.get("valueQuantity", {})
            value = value_quantity.get("value")

            if "temperature" in code:
                vitals["temperature"] = value

            elif "heart rate" in code:
                vitals["heart_rate"] = value

            elif "oxygen saturation" in code:
                vitals["spo2"] = value

            elif "blood pressure" in code:

                components = resource.get("component", [])

                for component in components:

                    component_name = (
                        component.get("code", {})
                        .get("text", "")
                        .lower()
                    )

                    component_value = (
                        component.get("valueQuantity", {})
                        .get("value")
                    )

                    if "systolic" in component_name:
                        vitals["systolic_bp"] = component_value

                    elif "diastolic" in component_name:
                        vitals["diastolic_bp"] = component_value

        # -------------------------
        # Medications
        # -------------------------
        elif resource_type == "MedicationStatement":

            status = resource.get("status")

            if status == "active":

                medication = (
                    resource
                    .get("medicationCodeableConcept", {})
                    .get("text")
                )

                if medication:
                    medications.append(medication)

    # --------------------------------
    # Create unified patient profile
    # --------------------------------

    patient_profile = {
        "patient_id": patient.get("patient_id"),
        "patient_name": patient.get("patient_name"),
        "age": patient.get("age"),
        "gender": patient.get("gender"),
        "birth_date": patient.get("birth_date"),

        "medical_history": conditions,

        "vitals": vitals,

        "medications": medications
    }

    return patient_profile


def get_patient_by_id(patient_id, file_path=FHIR_FILE):
    """Find a patient's bundle by ID and parse it into a profile."""
    db = _load_fhir_database(file_path)
    
    for bundle in db:
        # Check if this bundle belongs to the patient_id
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") == "Patient" and resource.get("id") == patient_id:
                return _parse_bundle(bundle)
                
    # If not found
    return None


# --------------------------------
# Test the parser
# --------------------------------

if __name__ == "__main__":

    available = get_available_patients()
    print("Available patients:", [p["id"] for p in available])

    if available:
        profile = get_patient_by_id("P003")
        
        if profile:
            print("\n===================================")
            print("FHIR PATIENT PROFILE")
            print("===================================")
            print("Patient ID   :", profile["patient_id"])
            print("Patient Name :", profile.get("patient_name", "N/A"))
            print("Age          :", profile["age"])
            print("Gender       :", profile["gender"])
            print("\nMedical History:")
            for condition in profile["medical_history"]:
                print("-", condition)
            print("\nVitals:")
            for name, value in profile["vitals"].items():
                print("-", name, ":", value)
            print("\nMedications:")
            for medication in profile["medications"]:
                print("-", medication)
            print("===================================")
        else:
            print("Patient P003 not found in database.")