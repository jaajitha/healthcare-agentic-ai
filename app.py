import json
import pandas as pd
import joblib
import streamlit as st
from fhir.parser import load_fhir_patient

from knowledge.medication_checker import check_medication_interactions


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Agentic AI Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 38px;
    font-weight: 750;
    text-align: center;
    margin-bottom: 4px;
}

.main-subtitle {
    text-align: center;
    font-size: 17px;
    opacity: 0.75;
    margin-bottom: 25px;
}

.section-header {
    font-size: 24px;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 15px;
}

.result-card {
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.25);
    min-height: 180px;
}

.result-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 15px;
}

.big-result {
    font-size: 23px;
    font-weight: 700;
    margin: 10px 0;
}

.small-label {
    font-size: 13px;
    opacity: 0.7;
}

.agent-box {
    padding: 24px;
    border-radius: 14px;
    border: 2px solid rgba(128,128,128,0.3);
    margin-top: 10px;
    margin-bottom: 20px;
}

.agent-title {
    font-size: 25px;
    font-weight: 750;
}

.briefing-box {
    padding: 25px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.3);
}

.status-ok {
    font-size: 14px;
    margin: 7px 0;
}

.warning-note {
    font-size: 13px;
    opacity: 0.75;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    model = joblib.load(
        "data/processed/random_forest_model.pkl"
    )

    label_encoder = joblib.load(
        "data/processed/label_encoder.pkl"
    )

    feature_columns = joblib.load(
        "data/processed/feature_columns.pkl"
    )

    return model, label_encoder, feature_columns


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

@st.cache_data
def load_knowledge():

    with open(
        "knowledge/medical_knowledge.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


model, label_encoder, feature_columns = load_model()
knowledge_base = load_knowledge()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(text):

    return (
        text.lower()
        .strip()
        .replace("_", " ")
        .replace("-", " ")
    )


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

    target = mappings.get(
        target,
        target
    )

    for disease in knowledge_base["diseases"]:

        names = [disease["name"]]

        names.extend(
            disease.get("aliases", [])
        )

        for name in names:

            if normalize_text(name) == target:

                return disease

    return None


def calculate_risk_flags(
    temperature,
    heart_rate,
    systolic,
    diastolic,
    spo2
):

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

    return risk_flags


# ============================================================
# SYMPTOM ALIASES
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
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🏥 Agentic AI"
    )

    st.caption(
        "Healthcare Decision-Support Prototype"
    )

    st.divider()

    st.markdown("### ⚙️ System Status")

    st.markdown(
        '<div class="status-ok">🟢 ML Model — Ready</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="status-ok">🟢 Knowledge Base — Ready</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="status-ok">🟢 Risk Engine — Ready</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="status-ok">🟢 Medication Checker — Ready</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="status-ok">🟢 Agentic Reasoning — Ready</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 🤖 ML Model")

    st.write("Random Forest")

    st.markdown("### 📚 Knowledge")

    st.write("Medical Knowledge Base")

    st.markdown("### 🧠 Architecture")

    st.write(
        "ML → Retrieval → Risk Analysis → "
        "Agentic Decision → Doctor Briefing"
    )

    st.divider()

    st.caption(
        "Decision-support prototype"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🏥 AGENTIC AI HEALTHCARE ASSISTANT'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Intelligent Autonomous Diagnostic Assistant'
    '<br>'
    'AI-powered clinical decision-support prototype'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# ============================================================
# FHIR / EHR INTEGRATION
# ============================================================

st.subheader("FHIR / EHR Integration")

# Initialize FHIR patient from session state
fhir_patient = st.session_state.get("fhir_patient", None)

# Load FHIR patient
if st.button("Load FHIR Patient", use_container_width=True):

    try:
        fhir_patient = load_fhir_patient()

        # Save patient profile in session state
        st.session_state["fhir_patient"] = fhir_patient

        st.success(
            f"FHIR patient {fhir_patient['patient_id']} loaded successfully."
        )

    except Exception as e:
        st.error(f"Unable to load FHIR patient: {e}")

# Get latest FHIR patient after button click
fhir_patient = st.session_state.get("fhir_patient", None)

# Display loaded patient information
if fhir_patient:

    st.info("Patient information loaded from local FHIR/EHR record.")

    # Patient information
    fhir_patient_id = fhir_patient.get("patient_id", "")
    fhir_age = fhir_patient.get("age", "")
    fhir_gender = fhir_patient.get("gender", "")

    # Medical history
    fhir_history = ", ".join(
        fhir_patient.get("medical_history", [])
    )

    # Vitals
    fhir_vitals = fhir_patient.get("vitals", {})

    fhir_temperature = fhir_vitals.get("temperature", "")
    fhir_heart_rate = fhir_vitals.get("heart_rate", "")
    fhir_systolic = fhir_vitals.get("systolic_bp", "")
    fhir_diastolic = fhir_vitals.get("diastolic_bp", "")
    fhir_spo2 = fhir_vitals.get("spo2", "")

    # Medications
    fhir_medications = ", ".join(
        fhir_patient.get("medications", [])
    )

else:

    fhir_patient_id = ""
    fhir_age = ""
    fhir_gender = ""
    fhir_history = ""

    fhir_temperature = ""
    fhir_heart_rate = ""
    fhir_systolic = ""
    fhir_diastolic = ""
    fhir_spo2 = ""

    fhir_medications = ""
# ============================================================
# PATIENT ASSESSMENT
# ============================================================

st.markdown(
    '<div class="section-header">'
    '👤 Patient Assessment'
    '</div>',
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)

with col1:

    patient_id = st.text_input(
        "Patient ID",
        placeholder="P001"
    )

with col2:

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=25
    )

with col3:

    sex = st.selectbox(
        "Sex",
        ["Male", "Female", "Other"]
    )


# ============================================================
# SYMPTOMS
# ============================================================

st.markdown("### 🩺 Symptoms")

symptoms_input = st.text_area(
    "Enter symptoms separated by commas",
    placeholder="fatigue, vomiting, headache",
    height=100
)


# ============================================================
# VITAL SIGNS
# ============================================================

st.markdown("### ❤️ Vital Signs")

col1, col2, col3, col4 = st.columns(4)

with col1:

    temperature = st.number_input(
        "Temperature (°C)",
        min_value=25.0,
        max_value=45.0,
        value=37.0,
        step=0.1
    )

with col2:

    heart_rate = st.number_input(
        "Heart Rate (bpm)",
        min_value=20,
        max_value=250,
        value=80
    )

with col3:

    systolic = st.number_input(
        "Systolic BP",
        min_value=50,
        max_value=250,
        value=120
    )

with col4:

    diastolic = st.number_input(
        "Diastolic BP",
        min_value=30,
        max_value=150,
        value=80
    )


spo2 = st.slider(
    "SpO₂ (%)",
    min_value=0.0,
    max_value=100.0,
    value=98.0,
    step=0.5
)


# ============================================================
# MEDICAL INFORMATION
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 📋 Medical History")

    medical_history = st.text_area(
        "Known medical conditions",
        placeholder="diabetes, hypertension, none",
        height=100
    )

with col2:

    st.markdown("### 💊 Current Medications")

    medications_input = st.text_area(
        "Enter medications separated by commas",
        placeholder="aspirin, warfarin",
        height=100
    )


st.divider()


# ============================================================
# ASSESS BUTTON
# ============================================================

assess = st.button(
    "🔍  ASSESS PATIENT",
    use_container_width=True,
    type="primary"
)


# ============================================================
# ASSESSMENT ENGINE
# ============================================================

if assess:

    if not patient_id.strip():

        st.error(
            "Please enter a Patient ID."
        )

        st.stop()


    if not symptoms_input.strip():

        st.error(
            "Please enter at least one symptom."
        )

        st.stop()


    # --------------------------------------------------------
    # Symptoms
    # --------------------------------------------------------

    entered_symptoms = [

        symptom.strip().lower()

        for symptom in symptoms_input.split(",")

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

        st.warning(
            "Unrecognized symptoms: "
            + ", ".join(invalid_symptoms)
        )


    if not valid_symptoms:

        st.error(
            "No recognized symptoms were entered."
        )

        st.stop()


    # --------------------------------------------------------
    # ML Input
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

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


    if top_probability >= 0.70:

        confidence_level = "HIGH"

    elif top_probability >= 0.40:

        confidence_level = "MODERATE"

    else:

        confidence_level = "LOW"


    # --------------------------------------------------------
    # Vital Risk
    # --------------------------------------------------------

    risk_flags = calculate_risk_flags(
        temperature,
        heart_rate,
        systolic,
        diastolic,
        spo2
    )


    # --------------------------------------------------------
    # Medication Check
    # --------------------------------------------------------

    if medications_input.strip().lower() in [
        "none",
        "no",
        "nil",
        ""
    ]:

        medication_list = []
        medication_alerts = []

    else:

        medication_list = [

            medication.strip()

            for medication
            in medications_input.split(",")

            if medication.strip()
        ]

        (
            medication_list,
            medication_alerts
        ) = check_medication_interactions(
            medication_list
        )


    # --------------------------------------------------------
    # Red Flags
    # --------------------------------------------------------

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
        red_flag_symptoms.intersection(
            normalized_entered
        )
    )


    # --------------------------------------------------------
    # Information Sufficiency
    # --------------------------------------------------------

    if len(valid_symptoms) < 3:

        information_status = "LIMITED"

    else:

        information_status = (
            "SUFFICIENT FOR FURTHER REVIEW"
        )


    # --------------------------------------------------------
    # Knowledge Retrieval
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Agentic Decision
    # --------------------------------------------------------

    if red_flags:

        agent_decision = (
            "URGENT CLINICAL REVIEW RECOMMENDED"
        )

        decision_reason = (
            "Potential red-flag symptom(s) were "
            "reported. These findings should be "
            "reviewed promptly by a qualified "
            "healthcare professional."
        )


    elif risk_flags:

        agent_decision = (
            "PRIORITIZE CLINICAL RISK REVIEW"
        )

        decision_reason = (
            "One or more vital-sign risk findings "
            "were detected. The agent prioritizes "
            "review of these findings before relying "
            "on the ML prediction."
        )


    elif medication_alerts:

        agent_decision = (
            "REVIEW MEDICATION SAFETY"
        )

        decision_reason = (
            "A potential medication interaction "
            "was detected. Professional clinical "
            "review is recommended."
        )


    elif information_status == "LIMITED":

        agent_decision = (
            "COLLECT ADDITIONAL INFORMATION"
        )

        decision_reason = (
            "The current symptom information is "
            "limited. Additional symptoms and "
            "clinical context should be collected."
        )


    elif confidence_level == "LOW":

        agent_decision = (
            "REVIEW MULTIPLE POSSIBILITIES"
        )

        decision_reason = (
            "The ML model has low confidence in "
            "its top candidate. Multiple possible "
            "conditions should be considered."
        )


    else:

        agent_decision = (
            "PROCEED TO CLINICAL INFORMATION REVIEW"
        )

        decision_reason = (
            "The available prototype information "
            "can be reviewed together with the ML "
            "candidates and medical knowledge."
        )


    # ========================================================
    # RESULTS
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-header">'
        '📊 Assessment Results'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # RESULT CARDS
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            '<div class="result-card">'
            '<div class="result-title">'
            '🤖 ML Prediction'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="small-label">'
            'Top Candidate'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="big-result">'
            f'{predicted_disease}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.metric(
            "Probability",
            f"{top_probability * 100:.2f}%"
        )

        st.caption(
            f"Confidence: {confidence_level}"
        )

        st.markdown(
            '<div class="warning-note">'
            'ML candidate — not a confirmed diagnosis.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            '<div class="result-card">'
            '<div class="result-title">'
            '❤️ Vital Risk'
            '</div>',
            unsafe_allow_html=True
        )

        if risk_flags:

            for flag in risk_flags:

                st.warning(
                    f"⚠ {flag}"
                )

        else:

            st.success(
                "✓ No basic vital-sign risk flags detected"
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            '<div class="result-card">'
            '<div class="result-title">'
            '💊 Medication Safety'
            '</div>',
            unsafe_allow_html=True
        )

        if not medication_list:

            st.info(
                "No current medications reported."
            )

        elif not medication_alerts:

            st.success(
                "✓ No interactions found in "
                "the current knowledge base."
            )

        else:

            for alert in medication_alerts:

                st.error(
                    f"⚠ {alert['medication_1'].title()} + "
                    f"{alert['medication_2'].title()}\n\n"
                    f"Severity: {alert['severity']}\n\n"
                    f"{alert['message']}"
                )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # ========================================================
    # TOP 5
    # ========================================================

    st.markdown("### 📈 Top 5 ML Candidates")

    prediction_data = []


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

        prediction_data.append({

            "Rank": rank,

            "Candidate": disease,

            "Probability": f"{probability:.2f}%"
        })


    st.dataframe(
        pd.DataFrame(prediction_data),
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # KNOWLEDGE
    # ========================================================

    st.markdown(
        "### 📚 Medical Knowledge Retrieved"
    )


    if retrieved_information:

        for (
            rank,
            disease,
            probability,
            information
        ) in retrieved_information:

            with st.expander(
                f"{rank}. {disease} "
                f"— {probability:.2f}%"
            ):

                st.markdown(
                    "**Description**"
                )

                st.write(
                    information["description"]
                )

                st.markdown(
                    "**Diagnostic Context**"
                )

                for item in information.get(
                    "diagnostic_context",
                    []
                ):

                    st.write(
                        f"• {item}"
                    )

                st.markdown(
                    "**Important Context**"
                )

                st.write(
                    information.get(
                        "important_context",
                        "Not available."
                    )
                )

                st.caption(
                    "Source: "
                    + information["source"][
                        "organization"
                    ]
                )


    else:

        st.info(
            "No matching knowledge-base entries "
            "were found."
        )


    # ========================================================
    # RED FLAGS
    # ========================================================

    st.markdown(
        "### 🚨 Red-Flag Review"
    )


    if red_flags:

        for flag in red_flags:

            st.error(
                f"Potential red flag: {flag}"
            )

    else:

        st.success(
            "✓ No configured red-flag symptoms reported"
        )


    # ========================================================
    # INFORMATION STATUS
    # ========================================================

    st.markdown(
        "### 📋 Information Sufficiency"
    )


    if information_status == "LIMITED":

        st.warning(
            "Limited symptom information. "
            "Additional patient information is recommended."
        )

    else:

        st.success(
            "Multiple symptoms were provided "
            "for further review."
        )


    # ========================================================
    # AGENTIC DECISION
    # ========================================================

    st.markdown(
        "### 🧠 Agentic Decision"
    )


    if agent_decision == (
        "URGENT CLINICAL REVIEW RECOMMENDED"
    ):

        st.error(
            f"### {agent_decision}\n\n"
            f"{decision_reason}"
        )

    elif agent_decision == (
        "PRIORITIZE CLINICAL RISK REVIEW"
    ):

        st.warning(
            f"### {agent_decision}\n\n"
            f"{decision_reason}"
        )

    elif agent_decision == (
        "REVIEW MEDICATION SAFETY"
    ):

        st.warning(
            f"### {agent_decision}\n\n"
            f"{decision_reason}"
        )

    else:

        st.info(
            f"### {agent_decision}\n\n"
            f"{decision_reason}"
        )


    # ========================================================
    # DOCTOR BRIEFING
    # ========================================================

    st.markdown(
        "### 👨‍⚕️ Doctor Briefing"
    )


    with st.container(border=True):

        st.markdown(
            f"**Patient:** {patient_id}  \n"
            f"**Age:** {age}  \n"
            f"**Sex:** {sex}"
        )


        st.markdown("#### Reported Symptoms")

        for symptom in valid_symptoms:

            st.write(
                f"• {symptom.replace('_', ' ')}"
            )


        st.markdown("#### Vital Signs")

        st.write(
            f"• Temperature: {temperature} °C"
        )

        st.write(
            f"• Heart Rate: {heart_rate} bpm"
        )

        st.write(
            f"• Blood Pressure: "
            f"{systolic}/{diastolic} mmHg"
        )

        st.write(
            f"• SpO₂: {spo2}%"
        )


        st.markdown("#### Medical History")

        if medical_history.strip():

            st.write(
                medical_history
            )

        else:

            st.write(
                "None reported"
            )


        st.markdown(
            "#### ML Candidate Assessment"
        )

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

            st.write(
                f"{rank}. {disease} "
                f"({probability:.2f}%)"
            )


        st.markdown(
            "#### Vital-Risk Findings"
        )

        if risk_flags:

            for flag in risk_flags:

                st.write(
                    f"⚠ {flag}"
                )

        else:

            st.write(
                "No basic vital-sign risk flags detected."
            )


        st.markdown(
            "#### Medication Safety"
        )

        if medication_alerts:

            for alert in medication_alerts:

                st.write(
                    f"⚠ {alert['medication_1'].title()} + "
                    f"{alert['medication_2'].title()}"
                )

                st.write(
                    f"Severity: {alert['severity']}"
                )

                st.write(
                    f"Concern: {alert['message']}"
                )

                st.write(
                    f"Action: {alert['action']}"
                )

        elif medication_list:

            st.write(
                "No interactions found in the "
                "current knowledge base."
            )

        else:

            st.write(
                "No current medications reported."
            )


        st.markdown(
            "#### Red-Flag Findings"
        )

        if red_flags:

            for flag in red_flags:

                st.write(
                    f"⚠ {flag}"
                )

        else:

            st.write(
                "No configured red-flag symptoms reported."
            )


        st.markdown(
            "#### Information Status"
        )

        st.write(
            information_status
        )


        st.markdown(
            "#### Agentic Recommendation"
        )

        st.write(
            f"**{agent_decision}**"
        )

        st.write(
            decision_reason
        )


    # ========================================================
    # SAFETY
    # ========================================================

    st.divider()

    st.warning(
        "⚠️ **Important:** This is a decision-support "
        "prototype. ML probabilities are dataset-level "
        "outputs and are not clinical diagnostic probabilities. "
        "Medication alerts are screening results requiring "
        "professional verification. The system does not replace "
        "evaluation by a qualified healthcare professional."
    )