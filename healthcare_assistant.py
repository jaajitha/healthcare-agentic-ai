import json
import pandas as pd
import joblib

from knowledge.medication_checker import check_medication_interactions
from hospital_routing_agent import route_patient_to_hospital


# ============================================================
# AGENTIC AI HEALTHCARE ASSISTANT
# ============================================================

print("=" * 70)
print("AGENTIC AI HEALTHCARE ASSISTANT")
print("=" * 70)


# ============================================================
# 1. LOAD ML MODEL
# ============================================================

model = joblib.load(
    "data/processed/random_forest_model.pkl"
)

label_encoder = joblib.load(
    "data/processed/label_encoder.pkl"
)

feature_columns = joblib.load(
    "data/processed/feature_columns.pkl"
)

print("\n[OK] ML model loaded successfully.")


# ============================================================
# 2. LOAD KNOWLEDGE BASE
# ============================================================

try:

    with open(
        "knowledge/medical_knowledge.json",
        "r",
        encoding="utf-8"
    ) as file:

        knowledge_base = json.load(file)

    print("[OK] Medical knowledge base loaded successfully.")

except FileNotFoundError:

    print("\n[ERROR] Medical knowledge base not found.")
    print("Expected: knowledge/medical_knowledge.json")
    exit()

except json.JSONDecodeError:

    print("\n[ERROR] Medical knowledge base contains invalid JSON.")
    exit()


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def normalize_text(text):

    return (
        text.lower()
        .strip()
        .replace("_", " ")
        .replace("-", " ")
    )


def get_valid_number(prompt, minimum, maximum, data_type=float):

    while True:

        try:

            value = data_type(input(prompt))

            if minimum <= value <= maximum:

                return value

            print(
                f"[ERROR] Value must be between "
                f"{minimum} and {maximum}."
            )

        except ValueError:

            print("[ERROR] Please enter a valid number.")


def retrieve_disease_information(disease_name):

    target = normalize_text(disease_name)

    mappings = {

        "peptic ulcer diseae":
            "peptic ulcer",

        "bronchial asthma":
            "asthma",

        "paralysis (brain hemorrhage)":
            "paralysis (brain hemorrhage)",

        "(vertigo) paroymsal positional vertigo":
            "(vertigo) paroymsal positional vertigo"
    }

    target = mappings.get(target, target)

    for disease in knowledge_base["diseases"]:

        names = [disease["name"]]

        names.extend(
            disease.get("aliases", [])
        )

        for name in names:

            if normalize_text(name) == target:

                return disease

    return None


# ============================================================
# 4. PATIENT INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("PATIENT INFORMATION")
print("=" * 70)

patient_id = input("\nPatient ID: ")

age = get_valid_number(
    "Age: ",
    0,
    120,
    int
)

sex = input(
    "Sex (Male/Female/Other): "
)


# ============================================================
# 5. SYMPTOMS
# ============================================================

print("\n" + "=" * 70)
print("SYMPTOM INFORMATION")
print("=" * 70)

print(
    "\nEnter symptoms separated by commas."
)

print(
    "Example: fatigue, vomiting, headache"
)

user_input = input(
    "\nSymptoms: "
)


# ============================================================
# 6. SYMPTOM ALIASES
# ============================================================

symptom_aliases = {

    "vomitings": "vomiting",
    "vomit": "vomiting",

    "high fever": "high_fever",
    "fever": "mild_fever",

    "stomach pain": "abdominal_pain",
    "stomach ache": "abdominal_pain",
    "belly pain": "abdominal_pain",

    "yellow skin": "yellowish_skin",
    "yellow eyes": "yellowing_of_eyes",

    "body pain": "muscle_pain",
    "joint pain": "joint_pain",

    "breathing difficulty": "breathlessness",
    "difficulty breathing": "breathlessness",

    "fast heartbeat": "fast_heart_rate",

    "skin rash": "skin_rash"
}


# ============================================================
# 7. VALIDATE SYMPTOMS
# ============================================================

entered_symptoms = [

    symptom.strip().lower()

    for symptom in user_input.split(",")

    if symptom.strip()
]


valid_symptoms = []
invalid_symptoms = []


for symptom in entered_symptoms:

    normalized = symptom.replace(
        " ",
        "_"
    )

    if symptom in symptom_aliases:

        normalized = symptom_aliases[
            symptom
        ]

    elif normalized in symptom_aliases:

        normalized = symptom_aliases[
            normalized
        ]

    if normalized in feature_columns:

        if normalized not in valid_symptoms:

            valid_symptoms.append(
                normalized
            )

    else:

        invalid_symptoms.append(
            symptom
        )


if invalid_symptoms:

    print(
        "\n[WARNING] Unrecognized symptoms:"
    )

    for symptom in invalid_symptoms:

        print("->", symptom)


if not valid_symptoms:

    print(
        "\n[ERROR] No valid symptoms were entered."
    )

    exit()


# ============================================================
# 8. VITAL SIGNS
# ============================================================

print("\n" + "=" * 70)
print("VITAL SIGNS")
print("=" * 70)


temperature = get_valid_number(
    "\nTemperature (C): ",
    25,
    45,
    float
)


heart_rate = get_valid_number(
    "Heart rate (bpm): ",
    20,
    250,
    int
)


systolic = get_valid_number(
    "Systolic blood pressure (mmHg): ",
    50,
    250,
    int
)


diastolic = get_valid_number(
    "Diastolic blood pressure (mmHg): ",
    30,
    150,
    int
)


spo2 = get_valid_number(
    "SpO2 (%): ",
    0,
    100,
    float
)


# ============================================================
# 9. MEDICAL HISTORY
# ============================================================

print("\n" + "=" * 70)
print("MEDICAL HISTORY")
print("=" * 70)

medical_history = input(
    "\nKnown medical conditions "
    "(enter 'None' if none): "
)


current_medications = input(
    "\nCurrent medications "
    "(enter 'None' if none): "
)
# ============================================================
# 10. MEDICATION INTERACTION CHECK
# ============================================================

if current_medications.strip().lower() in ["none", "no", "nil", ""]:
    medication_list = []
    medication_alerts = []

else:
    medication_list = [
        medication.strip()
        for medication in current_medications.split(",")
        if medication.strip()
    ]

    medication_list, medication_alerts = check_medication_interactions(
        medication_list
    )

# ============================================================
# 10. CREATE ML INPUT
# ============================================================

input_data = pd.DataFrame(
    0,
    index=[0],
    columns=feature_columns
)


for symptom in valid_symptoms:

    input_data.loc[
        0,
        symptom
    ] = 1


# ============================================================
# 11. RANDOM FOREST PREDICTION
# ============================================================

prediction = model.predict(
    input_data
)[0]


predicted_disease = (
    label_encoder.inverse_transform(
        [prediction]
    )[0]
)


probabilities = model.predict_proba(
    input_data
)[0]


top_indices = (
    probabilities
    .argsort()[-5:][::-1]
)


top_probability = probabilities[
    top_indices[0]
]


# ============================================================
# 12. CONFIDENCE
# ============================================================

if top_probability >= 0.70:

    confidence_level = "HIGH"

elif top_probability >= 0.40:

    confidence_level = "MODERATE"

else:

    confidence_level = "LOW"


# ============================================================
# 13. VITAL RISK ENGINE
# ============================================================

risk_flags = []


if temperature >= 39:

    risk_flags.append(
        "High temperature detected"
    )

elif temperature < 35:

    risk_flags.append(
        "Low temperature detected"
    )


if heart_rate > 100:

    risk_flags.append(
        "Elevated heart rate detected"
    )

elif heart_rate < 60:

    risk_flags.append(
        "Low heart rate detected"
    )


if systolic >= 140 or diastolic >= 90:

    risk_flags.append(
        "Elevated blood pressure detected"
    )

elif systolic < 90 or diastolic < 60:

    risk_flags.append(
        "Low blood pressure detected"
    )


if spo2 < 90:

    risk_flags.append(
        "Low oxygen saturation detected"
    )

elif spo2 < 94:

    risk_flags.append(
        "Reduced oxygen saturation detected"
    )


# ============================================================
# 14. RED-FLAG REVIEW
# ============================================================

red_flag_symptoms = {

    "sudden severe headache",

    "sudden weakness",

    "weakness",

    "numbness",

    "trouble speaking",

    "vision problems",

    "chest pain",

    "chest discomfort",

    "shortness of breath"
}


normalized_entered = {

    normalize_text(symptom)

    for symptom in entered_symptoms
}


red_flags = sorted(
    red_flag_symptoms
    .intersection(
        normalized_entered
    )
)


# ============================================================
# 15. INFORMATION SUFFICIENCY
# ============================================================

if len(valid_symptoms) < 3:

    information_status = "LIMITED"

else:

    information_status = "SUFFICIENT FOR FURTHER REVIEW"


# ============================================================
# 16. RETRIEVE TOP-5 KNOWLEDGE
# ============================================================

retrieved_information = []


for rank, index in enumerate(
    top_indices,
    start=1
):

    disease = (
        label_encoder.inverse_transform(
            [index]
        )[0]
    )

    probability = (
        probabilities[index] * 100
    )

    information = (
        retrieve_disease_information(
            disease
        )
    )

    if information:

        retrieved_information.append(
            (
                rank,
                disease,
                probability,
                information
            )
        )


# ============================================================
# 17. AGENTIC DECISION
# ============================================================

if red_flags:

    agent_decision = (
        "URGENT CLINICAL REVIEW RECOMMENDED"
    )

    decision_reason = (
        "Potential red-flag symptom(s) were reported."
    )

elif information_status == "LIMITED":

    agent_decision = (
        "COLLECT ADDITIONAL INFORMATION"
    )

    decision_reason = (
        "The current symptom information is limited."
    )

elif confidence_level == "LOW":

    agent_decision = (
        "REVIEW MULTIPLE POSSIBILITIES"
    )

    decision_reason = (
        "The ML model has low confidence in its top candidate."
    )

else:

    agent_decision = (
        "PROCEED TO CLINICAL INFORMATION REVIEW"
    )

    decision_reason = (
        "The available prototype information supports further review."
    )


# ============================================================
# 18. DISPLAY PATIENT ASSESSMENT
# ============================================================

print("\n\n" + "=" * 70)
print("UNIFIED PATIENT ASSESSMENT")
print("=" * 70)


print("\nPATIENT")
print("-" * 50)

print(
    "Patient ID:",
    patient_id
)

print(
    "Age:",
    age
)

print(
    "Sex:",
    sex
)


print("\nSYMPTOMS")
print("-" * 50)

for symptom in valid_symptoms:

    print(
        "[OK]",
        symptom
    )

print(
    "\nTotal recognized symptoms:",
    len(valid_symptoms)
)


print("\nVITAL SIGNS")
print("-" * 50)

print(
    "Temperature:",
    temperature,
    "C"
)

print(
    "Heart Rate:",
    heart_rate,
    "bpm"
)

print(
    "Blood Pressure:",
    f"{systolic}/{diastolic}",
    "mmHg"
)

print(
    "SpO2:",
    spo2,
    "%"
)


print("\nMEDICAL CONTEXT")
print("-" * 50)

print(
    "Medical History:",
    medical_history
)

print(
    "Current Medications:",
    current_medications
)


# ============================================================
# 19. ML RESULTS
# ============================================================

print("\n" + "=" * 70)
print("ML PREDICTION")
print("=" * 70)


print(
    "\nPredicted Disease:"
)

print(
    ">>>",
    predicted_disease
)


print(
    "\nPrediction Probability:",
    f"{top_probability * 100:.2f}%"
)


print(
    "Confidence Level:",
    confidence_level
)


print("\nTop 5 Predictions:")
print("-" * 55)


for rank, index in enumerate(
    top_indices,
    start=1
):

    disease = (
        label_encoder.inverse_transform(
            [index]
        )[0]
    )

    probability = (
        probabilities[index] * 100
    )

    print(
        f"{rank}. {disease:<40}"
        f"{probability:.2f}%"
    )


# ============================================================
# 20. KNOWLEDGE RETRIEVAL
# ============================================================

print("\n" + "=" * 70)
print("AGENT KNOWLEDGE RETRIEVAL")
print("=" * 70)


if retrieved_information:

    for (
        rank,
        disease,
        probability,
        information
    ) in retrieved_information:

        print(
            f"\n{rank}. {disease} "
            f"({probability:.2f}%)"
        )

        print(
            "\nDescription:"
        )

        print(
            information["description"]
        )

        print(
            "\nDiagnostic Context:"
        )

        for item in information.get(
            "diagnostic_context",
            []
        ):

            print(
                " -",
                item
            )

        print(
            "\nImportant Context:"
        )

        print(
            information.get(
                "important_context",
                "Not available."
            )
        )

        print(
            "\nSource:"
        )

        print(
            information["source"][
                "organization"
            ]
        )

        print(
            information["source"]["url"]
        )

else:

    print(
        "\nNo matching knowledge-base "
        "entries were found for the top-5 candidates."
    )


# ============================================================
# 21. VITAL RISK ASSESSMENT
# ============================================================

print("\n" + "=" * 70)
print("VITAL-SIGN RISK ASSESSMENT")
print("=" * 70)


if risk_flags:

    for flag in risk_flags:

        print(
            "->",
            flag
        )

else:

    print(
        "[OK] No basic vital-sign risk flags detected."
    )

# ============================================================
# MEDICATION INTERACTION ASSESSMENT
# ============================================================

print("\n" + "=" * 70)
print("MEDICATION INTERACTION ASSESSMENT")
print("=" * 70)

if not medication_list:

    print("\nNo current medications reported.")

elif not medication_alerts:

    print("\n✓ No interactions found in the current")
    print("  medication knowledge base.")

else:

    print("\n⚠ POTENTIAL MEDICATION INTERACTIONS FOUND")

    for alert in medication_alerts:

        print("\n" + "-" * 55)

        print(
            "Medications:",
            f"{alert['medication_1'].title()} + "
            f"{alert['medication_2'].title()}"
        )

        print(
            "Severity:",
            alert["severity"]
        )

        print(
            "Concern:",
            alert["message"]
        )

        print(
            "Action:",
            alert["action"]
        )
# ============================================================
# # ============================================================
# 22. RED-FLAG REVIEW
# ============================================================

print("\n" + "=" * 70)
print("RED-FLAG REVIEW")
print("=" * 70)

if red_flags:

    print("\n[WARNING] Potential red-flag symptoms detected:")

    for flag in red_flags:
        print("->", flag)

else:

    print(
        "[OK] No configured red-flag symptom was reported."
    )


# ============================================================
# 23. INFORMATION SUFFICIENCY
# ============================================================

print("\n" + "=" * 70)
print("INFORMATION SUFFICIENCY")
print("=" * 70)

if information_status == "LIMITED":

    print(
        "[WARNING] Limited symptom information."
    )

    print(
        "The system recommends collecting "
        "additional patient information."
    )

else:

    print(
        "[OK] Multiple symptoms were provided."
    )


# ============================================================
# 24. AGENTIC DECISION ENGINE
# ============================================================

print("\n" + "=" * 70)
print("AGENTIC DECISION")
print("=" * 70)


# Priority 1: Red-flag symptoms
if red_flags:

    agent_decision = (
        "URGENT CLINICAL REVIEW RECOMMENDED"
    )

    decision_reason = (
        "Potential red-flag symptom(s) were reported. "
        "These findings should be reviewed promptly "
        "by a qualified healthcare professional."
    )


# Priority 2: Significant vital-sign risk
elif risk_flags:

    agent_decision = (
        "PRIORITIZE CLINICAL RISK REVIEW"
    )

    decision_reason = (
        "One or more vital-sign risk findings were detected. "
        "The agent prioritizes review of these findings "
        "before relying on the ML prediction."
    )


# Priority 3: Medication interaction
elif medication_alerts:

    agent_decision = (
        "REVIEW MEDICATION SAFETY"
    )

    decision_reason = (
        "A potential medication interaction was detected. "
        "Professional clinical review is recommended."
    )


# Priority 4: Insufficient information
elif information_status == "LIMITED":

    agent_decision = (
        "COLLECT ADDITIONAL INFORMATION"
    )

    decision_reason = (
        "The current symptom information is limited. "
        "Additional symptoms and clinical context "
        "should be collected."
    )


# Priority 5: Low ML confidence
elif confidence_level == "LOW":

    agent_decision = (
        "REVIEW MULTIPLE POSSIBILITIES"
    )

    decision_reason = (
        "The ML model has low confidence in its top candidate. "
        "Multiple possible conditions should be considered "
        "during clinical review."
    )


# Priority 6: Sufficient information
else:

    agent_decision = (
        "PROCEED TO CLINICAL INFORMATION REVIEW"
    )

    decision_reason = (
        "The available prototype information can be reviewed "
        "together with the ML candidates and medical knowledge."
    )


print("\nDecision:")
print(
    ">>>",
    agent_decision
)

print("\nReason:")
print(
    decision_reason
)
# ============================================================
# 25. APOLLO ARAGONDA HOSPITAL ROUTING
# ============================================================

# Use the patient's reported/recognized symptoms as the primary
# routing input. ML predictions are passed as additional context.
predicted_conditions = []

for index in top_indices:

    disease = (
        label_encoder.inverse_transform(
            [index]
        )[0]
    )

    predicted_conditions.append(disease)


hospital_routing = route_patient_to_hospital(
    symptoms=valid_symptoms,
    predicted_conditions=predicted_conditions,
    hospital_code="AH-ARAGONDA"
)


print("\n" + "=" * 70)
print("APOLLO ARAGONDA HOSPITAL ROUTING")
print("=" * 70)


if hospital_routing.get("success"):

    hospital = hospital_routing.get("hospital")
    speciality = hospital_routing.get("speciality")
    routing_doctors = hospital_routing.get("doctors", [])

    if hospital:

        print(
            "\nHospital:",
            hospital.get("name")
        )

        print(
            "Hospital Type:",
            hospital.get("hospital_type")
        )

    if speciality:

        print(
            "\nSuggested Speciality:",
            speciality
        )

        if routing_doctors:

            print(
                "\nRelevant Listed Doctor(s):"
            )

            for doctor in routing_doctors:

                print(
                    f" - {doctor.get('name')} "
                    f"({doctor.get('speciality')})"
                )

                if doctor.get("experience_years") is not None:

                    print(
                        f"   Experience: "
                        f"{doctor.get('experience_years')} years"
                    )

        else:

            print(
                "\nRelevant Listed Doctor(s):"
            )

            print(
                " - No matching listed doctor found."
            )

    else:

        print(
            "\nSuggested Speciality:"
        )

        print(
            " - No specific speciality identified "
            "from the available hospital routing rules."
        )

    print(
        "\nRouting Reason:"
    )

    print(
        " -",
        hospital_routing.get(
            "message",
            "No routing reason available."
        )
    )

else:

    print(
        "\n[WARNING] Hospital routing could not be completed."
    )

   


print(
    "\nClinical routing note:"
)

print(
    " - Hospital routing is decision support based on "
    "reported symptoms and available hospital data."
)

print(
    " - It does not confirm a diagnosis or replace "
    "clinical judgement."
)


# ============================================================
# 25. DOCTOR BRIEFING
# ============================================================

# ============================================================
# 25. DOCTOR BRIEFING
# ============================================================

print("\n" + "=" * 70)
print("DOCTOR BRIEFING")
print("=" * 70)


# ------------------------------------------------------------
# Patient Summary
# ------------------------------------------------------------

print(
    "\nPatient:",
    patient_id,
    "| Age:",
    age,
    "| Sex:",
    sex
)


# ------------------------------------------------------------
# Symptoms
# ------------------------------------------------------------

print("\nReported symptoms:")

for symptom in valid_symptoms:
    print(" -", symptom)


# ------------------------------------------------------------
# Vital Signs
# ------------------------------------------------------------

print("\nVital signs:")

print(
    f" - Temperature: {temperature} C"
)

print(
    f" - Heart Rate: {heart_rate} bpm"
)

print(
    f" - Blood Pressure: "
    f"{systolic}/{diastolic} mmHg"
)

print(
    f" - SpO2: {spo2}%"
)


# ------------------------------------------------------------
# Medical History
# ------------------------------------------------------------

print("\nMedical history:")

if medical_history.strip().lower() in [
    "none",
    "no",
    "nil"
]:

    print(" - None reported")

else:

    print(
        " -",
        medical_history
    )


# ------------------------------------------------------------
# ML Candidate Assessment
# ------------------------------------------------------------

print("\nML candidate assessment:")

for rank, index in enumerate(
    top_indices,
    start=1
):

    disease = (
        label_encoder.inverse_transform(
            [index]
        )[0]
    )

    probability = (
        probabilities[index] * 100
    )

    print(
        f" {rank}. {disease} "
        f"({probability:.2f}%)"
    )


print(
    "\nTop ML candidate:",
    predicted_disease
)

print(
    "ML confidence:",
    confidence_level
)


# ------------------------------------------------------------
# Vital Risk Findings
# ------------------------------------------------------------

print("\nVital-risk findings:")

if risk_flags:

    for flag in risk_flags:

        print(
            " -",
            flag
        )

else:

    print(
        " - No basic vital-sign risk flags detected"
    )


# ------------------------------------------------------------
# Medication Safety
# ------------------------------------------------------------

print("\nMedication safety:")

if not medication_list:

    print(
        " - No current medications reported"
    )

elif not medication_alerts:

    print(
        " - No interactions found in the current "
        "knowledge base"
    )

else:

    for alert in medication_alerts:

        print(
            f" - {alert['medication_1'].title()} + "
            f"{alert['medication_2'].title()}"
        )

        print(
            f"   Severity: {alert['severity']}"
        )

        print(
            f"   Concern: {alert['message']}"
        )

        print(
            f"   Action: {alert['action']}"
        )


# ------------------------------------------------------------
# Red Flags
# ------------------------------------------------------------

print("\nRed-flag findings:")

if red_flags:

    for flag in red_flags:

        print(
            " -",
            flag
        )

else:

    print(
        " - No configured red-flag symptoms reported"
    )


# ------------------------------------------------------------
# Information Sufficiency
# ------------------------------------------------------------

print("\nInformation status:")

print(
    " -",
    information_status
)

if information_status == "LIMITED":

    print(
        " - Additional patient information is recommended"
    )


# ------------------------------------------------------------
# Agentic Recommendation
# ------------------------------------------------------------

print("\nAgentic recommendation:")

print(
    " >>>",
    agent_decision
)

print(
    "\nReason:"
)

print(
    decision_reason
)


# ------------------------------------------------------------
# Final Safety Statement
# ------------------------------------------------------------

print("\nClinical review note:")

print(
    " - ML predictions are candidate conditions, "
    "not confirmed diagnoses."
)

print(
    " - Medication alerts are screening results "
    "requiring professional verification."
)

print(
    " - Final clinical decisions remain with "
    "a qualified healthcare professional."
)

# ============================================================
# 26. SAFETY
# ============================================================

print("\n" + "=" * 70)
print("IMPORTANT")
print("=" * 70)


print(
    "\nThis system is a decision-support prototype."
)


print(
    "ML probabilities are dataset-level outputs "
    "and are not clinical diagnostic probabilities."
)


print(
    "The system does not replace evaluation by "
    "a qualified healthcare professional."
)


print("=" * 70)