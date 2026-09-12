import json
from datetime import date


FHIR_FILE = "fhir/patient.json"


def calculate_age(birth_date):
    """Calculate patient's age from FHIR birthDate."""
    birth = date.fromisoformat(birth_date)
    today = date.today()

    age = today.year - birth.year

    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1

    return age


def load_fhir_patient(file_path=FHIR_FILE):
    """Load and parse a FHIR Bundle."""

    with open(file_path, "r", encoding="utf-8") as file:
        bundle = json.load(file)

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
        "age": patient.get("age"),
        "gender": patient.get("gender"),
        "birth_date": patient.get("birth_date"),

        "medical_history": conditions,

        "vitals": vitals,

        "medications": medications
    }

    return patient_profile


# --------------------------------
# Test the parser
# --------------------------------

if __name__ == "__main__":

    profile = load_fhir_patient()

    print("\n===================================")
    print("FHIR PATIENT PROFILE")
    print("===================================")

    print("Patient ID :", profile["patient_id"])
    print("Age        :", profile["age"])
    print("Gender     :", profile["gender"])

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