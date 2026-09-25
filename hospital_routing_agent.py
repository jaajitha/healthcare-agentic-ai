from hospital_client import (
    get_hospital,
    get_departments,
    get_doctors,
)


# ============================================================
# SYMPTOM → SPECIALITY MAPPING
# ============================================================

SYMPTOM_SPECIALITY_MAP = {

    # Orthopaedics
    "joint_pain": "Orthopaedics",
    "knee_pain": "Orthopaedics",
    "back_pain": "Orthopaedics",
    "bone_pain": "Orthopaedics",
    "muscle_pain": "Orthopaedics",
    "swelling_joints": "Orthopaedics",
    "difficulty_walking": "Orthopaedics",

    # Internal Medicine
    "fever": "Internal Medicine",
    "high_fever": "Internal Medicine",
    "mild_fever": "Internal Medicine",
    "fatigue": "Internal Medicine",
    "vomiting": "Internal Medicine",
    "nausea": "Internal Medicine",
    "diarrhoea": "Internal Medicine",
    "dizziness": "Internal Medicine",
    "weakness": "Internal Medicine",
    "sweating": "Internal Medicine",

    # General Surgery
    "abdominal_pain": "General Surgery",
    "severe_abdominal_pain": "General Surgery",

    # Gynaecology
    "menstrual_irregularity": "Gynaecology",
    "pelvic_pain": "Gynaecology",

    # Obstetrics
    "pregnancy": "Obstetrics",

    # Pediatrics
    "child_fever": "Pediatrics",

    # Dentistry
    "toothache": "Dentistry",
    "tooth_pain": "Dentistry",
    "gum_pain": "Dentistry",
}


# ============================================================
# SPECIALITY ALIASES
# ============================================================

SPECIALITY_ALIASES = {
    "orthopaedics": [
        "orthopaedics",
        "orthopedics",
    ],

    "orthopedics": [
        "orthopaedics",
        "orthopedics",
    ],

    "general medicine": [
        "general medicine",
        "internal medicine",
    ],

    "internal medicine": [
        "general medicine",
        "internal medicine",
    ],
}


# ============================================================
# NORMALIZE SYMPTOM
# ============================================================

def normalize_symptom(symptom):
    """
    Convert symptom text into a standard format.
    """

    if not symptom:
        return ""

    symptom = str(symptom).strip().lower()

    symptom = symptom.replace(" ", "_")
    symptom = symptom.replace("-", "_")

    return symptom


# ============================================================
# FIND RELEVANT SPECIALITY
# ============================================================

def find_relevant_speciality(symptoms):
    """
    Determine the most relevant hospital speciality
    from the patient's reported symptoms.

    This is routing/decision support.
    It does NOT diagnose the patient.
    """

    if not symptoms:
        return None

    speciality_scores = {}

    for symptom in symptoms:

        normalized = normalize_symptom(symptom)

        speciality = SYMPTOM_SPECIALITY_MAP.get(
            normalized
        )

        if speciality:

            speciality_scores[speciality] = (
                speciality_scores.get(speciality, 0) + 1
            )

    if not speciality_scores:
        return None

    return max(
        speciality_scores,
        key=speciality_scores.get
    )


# ============================================================
# FIND RELEVANT DOCTORS
# ============================================================

def find_relevant_doctors(speciality):
    """
    Find doctors at Apollo Hospitals, Aragonda
    matching the requested speciality.
    """

    if not speciality:
        return []

    doctors = get_doctors()

    requested = speciality.strip().lower()

    accepted_names = SPECIALITY_ALIASES.get(
        requested,
        [requested]
    )

    matching_doctors = []

    for doctor in doctors:

        doctor_speciality = (
            doctor.get("speciality") or ""
        ).strip().lower()

        for name in accepted_names:

            if (
                name == doctor_speciality
                or name in doctor_speciality
                or doctor_speciality in name
            ):
                matching_doctors.append(doctor)
                break

    return matching_doctors


# ============================================================
# CHECK WHETHER SPECIALITY EXISTS IN HOSPITAL
# ============================================================

def speciality_exists(
    speciality,
    hospital_code="AH-ARAGONDA"
):
    """
    Check whether a speciality is represented
    in the hospital's department data.
    """

    if not speciality:
        return False

    departments = get_departments(hospital_code)

    requested = speciality.strip().lower()

    accepted_names = SPECIALITY_ALIASES.get(
        requested,
        [requested]
    )

    for department in departments:

        department_name = (
            department.get("department_name") or ""
        ).strip().lower()

        for name in accepted_names:

            if (
                name == department_name
                or name in department_name
                or department_name in name
            ):
                return True

    return False


# ============================================================
# MAIN HOSPITAL ROUTING AGENT
# ============================================================

def route_patient_to_hospital(
    symptoms=None,
    predicted_conditions=None,
    hospital_code="AH-ARAGONDA"
):
    """
    Route a patient toward a relevant speciality
    and listed doctor at Apollo Hospitals, Aragonda.

    Parameters
    ----------
    symptoms:
        Patient-reported symptoms.

    predicted_conditions:
        Optional ML predictions. Reserved for future
        expansion of the routing logic.

    hospital_code:
        Hospital identifier.

    Returns
    -------
    dict
        Structured routing result.
    """

    # --------------------------------------------------------
    # GET HOSPITAL
    # --------------------------------------------------------

    hospital = get_hospital(hospital_code)

    if not hospital:

        return {
            "success": False,
            "message": "Hospital information not found.",
            "hospital": None,
            "speciality": None,
            "speciality_available": False,
            "doctors": [],
        }

    # --------------------------------------------------------
    # FIND SPECIALITY
    # --------------------------------------------------------

    speciality = find_relevant_speciality(symptoms)

    # --------------------------------------------------------
    # NO SPECIALITY FOUND
    # --------------------------------------------------------

    if speciality is None:

        return {
            "success": True,
            "message": (
                "No specific hospital speciality could be "
                "identified from the available symptom mapping."
            ),
            "hospital": hospital,
            "speciality": None,
            "speciality_available": False,
            "doctors": [],
        }

    # --------------------------------------------------------
    # CHECK HOSPITAL DEPARTMENT
    # --------------------------------------------------------

    available = speciality_exists(
        speciality,
        hospital_code
    )

    # --------------------------------------------------------
    # FIND DOCTORS
    # --------------------------------------------------------

    doctors = find_relevant_doctors(
        speciality
    )

    # --------------------------------------------------------
    # SPECIALITY NOT AVAILABLE
    # --------------------------------------------------------

    if not available:

        return {
            "success": True,
            "message": (
                f"{speciality} was identified as potentially "
                "relevant, but it is not listed as a department "
                "in the Apollo Aragonda hospital data."
            ),
            "hospital": hospital,
            "speciality": speciality,
            "speciality_available": False,
            "doctors": [],
        }

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return {
        "success": True,
        "message": (
            f"{speciality} is the most relevant speciality "
            "based on the available symptom mapping."
        ),
        "hospital": hospital,
        "speciality": speciality,
        "speciality_available": True,
        "doctors": doctors,
    }


# ============================================================
# FORMAT ROUTING RESULT
# ============================================================

def format_routing_result(result):
    """
    Convert routing result into readable text.
    """

    if not result:
        return "No hospital routing result available."

    if not result.get("success"):

        return result.get(
            "message",
            "Hospital routing failed."
        )

    hospital = result.get("hospital")

    lines = []

    # Hospital
    if hospital:

        lines.append(
            f"Hospital: {hospital.get('name')}"
        )

    # Speciality
    speciality = result.get("speciality")

    if speciality:

        lines.append(
            f"Suggested Speciality: {speciality}"
        )

        # Doctors
        doctors = result.get("doctors", [])

        if doctors:

            lines.append(
                "Relevant Listed Doctor(s):"
            )

            for doctor in doctors:

                lines.append(
                    f"- {doctor.get('name')} "
                    f"({doctor.get('speciality')})"
                )

        else:

            lines.append(
                "No matching listed doctor was found."
            )

    else:

        lines.append(
            "Suggested Speciality: "
            "No specific speciality identified"
        )

    # Reason
    lines.append(
        "Reason: "
        + result.get("message", "")
    )

    # Safety note
    lines.append(
        "Note: This is hospital routing decision support "
        "and does not constitute a medical diagnosis."
    )

    return "\n".join(lines)