import json
import pandas as pd
import joblib
import streamlit as st
import datetime
import sys
if "supabase_client" in sys.modules:
    del sys.modules["supabase_client"]

from src.services.supabase_client import (
    get_patients, 
    get_patient_profile, 
    save_assessment, 
    get_assessment_history_by_uuid,
    get_patient_observations,
    get_patient_risk_flags,
    get_patient_medication_alerts,
    get_patient_doctor_briefings
)

from src.knowledge.medication_checker import check_medication_interactions
from src.agents.hospital_routing_agent import route_patient_to_hospital, format_routing_result

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
# INITIALIZE SESSION STATE
# ============================================================
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = None
if "patient_name" not in st.session_state:
    st.session_state["patient_name"] = None
if "age" not in st.session_state:
    st.session_state["age"] = None
if "sex" not in st.session_state:
    st.session_state["sex"] = "Select sex"
if "symptoms_input" not in st.session_state:
    st.session_state["symptoms_input"] = ""
if "temperature" not in st.session_state:
    st.session_state["temperature"] = None
if "heart_rate" not in st.session_state:
    st.session_state["heart_rate"] = None
if "systolic_bp" not in st.session_state:
    st.session_state["systolic_bp"] = None
if "diastolic_bp" not in st.session_state:
    st.session_state["diastolic_bp"] = None
if "spo2" not in st.session_state:
    st.session_state["spo2"] = None
if "medical_history" not in st.session_state:
    st.session_state["medical_history"] = ""
if "current_medications" not in st.session_state:
    st.session_state["current_medications"] = ""


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.main-title { font-size: 38px; font-weight: 800; text-align: center; margin-bottom: 4px; font-family: 'Inter', sans-serif; color: var(--text-color); }
.main-subtitle { text-align: center; font-size: 17px; opacity: 0.8; margin-bottom: 25px; font-family: 'Inter', sans-serif; color: var(--text-color); }
.section-header { font-size: 24px; font-weight: 800; margin-top: 25px; margin-bottom: 15px; color: var(--text-color); }
.result-card { padding: 30px; border-radius: 16px; border: 1px solid rgba(128,128,128,0.2); min-height: 180px; background-color: var(--secondary-background-color); }
.result-title { font-size: 18px; font-weight: 700; margin-bottom: 15px; color: var(--text-color); opacity: 0.8; }
.big-result { font-size: 26px; font-weight: 800; margin: 10px 0; color: var(--text-color); }
.small-label { font-size: 13px; opacity: 0.7; color: var(--text-color); }
.agent-box { padding: 25px; border-radius: 16px; border-left: 5px solid #9c27b0; margin-top: 10px; margin-bottom: 20px; background: linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(103, 58, 183, 0.1) 100%); color: var(--text-color); }
.agent-title { font-size: 25px; font-weight: 800; color: var(--text-color); }
.briefing-box { padding: 25px; border-radius: 16px; border-left: 5px solid #00bcd4; background-color: rgba(0, 188, 212, 0.15); color: var(--text-color); }
.status-ok { font-size: 14px; margin: 7px 0; font-weight: 600; color: #28a745; }
.warning-note { font-size: 13px; opacity: 0.75; color: var(--text-color); }

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

    if temperature is not None:
        if temperature >= 39:
            risk_flags.append("High temperature detected")
        elif temperature < 35:
            risk_flags.append("Low temperature detected")

    if heart_rate is not None:
        if heart_rate > 100:
            risk_flags.append("Elevated heart rate detected")
        elif heart_rate < 60:
            risk_flags.append("Low heart rate detected")

    if systolic is not None and diastolic is not None:
        if systolic >= 140 or diastolic >= 90:
            risk_flags.append("Elevated blood pressure detected")
        elif systolic < 90 or diastolic < 60:
            risk_flags.append("Low blood pressure detected")

    if spo2 is not None:
        if spo2 < 90:
            risk_flags.append("Low oxygen saturation detected")
        elif spo2 < 94:
            risk_flags.append("Reduced oxygen saturation detected")

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
# CHECK AUTHENTICATION
# ============================================================
if not st.session_state.get("authenticated") or st.session_state.get("user_role") != "admin":
    st.error("Unauthorized. Please login from the main page.")
    st.stop()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown("### Navigation")
if "app_menu_selection" not in st.session_state:
    st.session_state["app_menu_selection"] = "🏠 Overview"

nav_items = [
    "🏠 Overview",
    "🩺 AI Assessment Dashboard",
    "🚪 Logout"
]

for item in nav_items:
    if st.sidebar.button(item, use_container_width=True, type="primary" if st.session_state["app_menu_selection"] == item else "secondary"):
        st.session_state["app_menu_selection"] = item
        st.rerun()

menu = st.session_state["app_menu_selection"]

if menu == "🚪 Logout":
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["patient_id"] = None
    st.session_state["patient_uuid"] = None
    st.rerun()

ca = st.session_state.get("current_assessment")

if menu == "🏠 Overview":
    st.markdown("## 🧠 Main AI Dashboard")
    st.write("### Hospital: Apollo Hospitals, Aragonda")
    st.info("Use the sidebar to navigate the AI assessment workflows.")
    col1, col2 = st.columns(2)
    col1.metric("Emergency", "24×7")
    col2.metric("Telemedicine", "Available")
    st.stop()
    
# We removed Doctor Dashboard block entirely, so we just fall through to the rest of the file 
# if menu == "🩺 AI Assessment Dashboard"!

# ============================================================
# FHIR / EHR / SUPABASE INTEGRATION
# ============================================================

st.subheader("FHIR / EHR Integration")

def handle_patient_change():
    if "current_assessment" in st.session_state:
        del st.session_state["current_assessment"]
    if "saved_assessment_hash" in st.session_state:
        del st.session_state["saved_assessment_hash"]
    if "fhir_patient" in st.session_state:
        del st.session_state["fhir_patient"]
    # Clear manual assessment form data
    for key in ["patient_id", "patient_name", "age", "sex", "symptoms_input", "temperature", "heart_rate", "systolic_bp", "diastolic_bp", "spo2", "medical_history", "current_medications"]:
        if key in st.session_state:
            del st.session_state[key]

patient_mode = st.radio(
    "Patient Workflow",
    ["Existing Patient (FHIR/EHR)", "Register New Patient"],
    horizontal=True,
    on_change=handle_patient_change,
    key="patient_workflow"
)

st.write("")

if patient_mode == "Existing Patient (FHIR/EHR)":

    # ------------------------------------------------------------
    # Initialize loaded patient
    # ------------------------------------------------------------

    fhir_patient = st.session_state.get(
        "fhir_patient",
        None
    )


    # ------------------------------------------------------------
    # Load patients from Supabase
    # ------------------------------------------------------------

    try:

        available_patients = get_patients()

        if available_patients:

            patient_options = {
                f"{patient['patient_id']} - {patient['name']}":
                    patient["patient_id"]

                for patient in available_patients
            }


            col_sel, col_btn = st.columns([3, 1])


            with col_sel:

                selected_option = st.selectbox(
                    "Select or Search Patient",
                    options=list(
                        patient_options.keys()
                    ),
                    key="patient_selector",
                    on_change=handle_patient_change
                )


            with col_btn:

                st.write("")
                st.write("")

                load_clicked = st.button(
                    "Load FHIR Patient"
                )


            # ----------------------------------------------------
            # Load selected patient
            # ----------------------------------------------------

            if load_clicked:

                selected_id = patient_options[
                    selected_option
                ]

                # PATIENT SWITCHING: Clear old current assessment if patient changed
                old_patient_id = st.session_state.get("selected_patient_id")
                if old_patient_id != selected_id:
                    for key in ["current_assessment", "saved_assessment_hash"]:
                        if key in st.session_state:
                            del st.session_state[key]

                loaded_patient = (
                    get_patient_profile(
                        selected_id
                    )
                )


                if loaded_patient:

                    st.session_state["fhir_patient"] = loaded_patient
                    st.session_state["selected_patient_id"] = selected_id
                    st.session_state["selected_patient_uuid"] = loaded_patient.get("patient_uuid")
                    
                    # Ensure manual form is synchronized
                    st.session_state["patient_id"] = selected_id
                    st.session_state["patient_name"] = loaded_patient.get("patient_name")
                    st.session_state["age"] = loaded_patient.get("age")
                    st.session_state["sex"] = loaded_patient.get("gender")

                    st.success(
                        f"FHIR/EHR patient "
                        f"{selected_id} loaded successfully."
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Patient {selected_id} "
                        "was not found."
                    )


        else:

            st.warning(
                "No patients found in Supabase."
            )


    except Exception as e:

        st.error(
            f"Unable to load patient database: {e}"
        )

else:
    st.markdown("### 📝 Register New Patient")
    # Calculate age automatically if DOB is selected
    # We remove st.form so that Streamlit can re-run and calculate age immediately when DOB changes
    
    reg_name = st.text_input("Patient Name", placeholder="e.g., Suresh Kumar")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        reg_dob = st.date_input("Date of Birth", value=datetime.date(1990, 1, 1), min_value=datetime.date(1990, 1, 1), max_value=datetime.date(2027, 12, 31))
    
    # Auto-calculate age
    today = datetime.date.today()
    calculated_age = today.year - reg_dob.year - ((today.month, today.day) < (reg_dob.month, reg_dob.day))
    
    with col2:
        reg_age = st.number_input("Age (Auto-calculated)", min_value=0, max_value=120, step=1, value=calculated_age, disabled=True)
        
    with col3:
        reg_sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    
    reg_history = st.text_area("Medical History (comma separated)", placeholder="e.g., Asthma, Hypertension")
    reg_meds = st.text_area("Current Medications (comma separated)", placeholder="e.g., Albuterol, Lisinopril")
    
    submitted = st.button("Register Patient", type="primary")
    
    if submitted:
        if not reg_name.strip():
            st.error("Patient Name is required.")
        else:
            try:
                from src.services.supabase_client import register_patient, get_patient_profile
                new_id = register_patient(
                    name=reg_name.strip(),
                    age=reg_age,
                    gender=reg_sex,
                    dob=str(reg_dob) if reg_dob else None,
                    medical_history=reg_history,
                    medications=reg_meds
                )
                
                # Clear old current assessment if patient changed
                old_patient_id = st.session_state.get("selected_patient_id")
                if old_patient_id != new_id:
                    for key in ["current_assessment", "saved_assessment_hash"]:
                        if key in st.session_state:
                            del st.session_state[key]
                            
                st.success(f"Patient registered successfully! Generated ID: {new_id}")
                loaded_patient = get_patient_profile(new_id)
                if loaded_patient:
                    st.session_state["fhir_patient"] = loaded_patient
                    st.session_state["selected_patient_id"] = new_id
                    st.session_state["selected_patient_uuid"] = loaded_patient.get("patient_uuid")
            except Exception as e:
                st.error(f"Failed to register patient: {e}")
                if "row-level security" in str(e).lower():
                    st.error("🔒 SUPABASE RLS ERROR: You need to enable INSERT access for the 'patients', 'conditions', and 'medications' tables in your Supabase Dashboard!")



# ------------------------------------------------------------
# Get loaded patient
# ------------------------------------------------------------

fhir_patient = st.session_state.get(
    "fhir_patient",
    None
)


# ============================================================
# DISPLAY LOADED PATIENT
# ============================================================

if fhir_patient:

    st.info(
        "Patient information loaded from "
        "FHIR/EHR data stored in Supabase."
    )


    vitals = fhir_patient.get(
        "vitals",
        {}
    )


    st.markdown(
        f"""
        <div style="
            padding: 15px;
            border-radius: 10px;
            background-color: rgba(128,128,128,0.1);
            border: 1px solid rgba(128,128,128,0.3);
            margin-bottom: 20px;
        ">

        <h4 style="margin-top: 0;">
            🏥 FHIR / EHR Patient Loaded
        </h4>

        <b>Patient ID:</b>
        {fhir_patient.get('patient_id', 'N/A')}
        &nbsp;|&nbsp;

        <b>Name:</b>
        {fhir_patient.get('patient_name', 'N/A')}
        &nbsp;|&nbsp;

        <b>Age:</b>
        {fhir_patient.get('age', 'N/A')}
        &nbsp;|&nbsp;

        <b>Sex:</b>
        {str(fhir_patient.get('gender', 'N/A')).title()}

        <br><br>

        <b>Medical History:</b>
        {", ".join(
            fhir_patient.get(
                'medical_history',
                []
            )
        ) or 'None'}

        <br><br>

        <b>Symptoms:</b>
        {", ".join(
            fhir_patient.get(
                'symptoms',
                []
            )
        ) or 'None'}

        <br><br>

        <b>Vitals:</b>
        Temp {vitals.get('temperature', 'N/A')} °C,
        HR {vitals.get('heart_rate', 'N/A')} bpm,
        BP {vitals.get('systolic_bp', 'N/A')}/
        {vitals.get('diastolic_bp', 'N/A')} mmHg,
        SpO₂ {vitals.get('spo2', 'N/A')}%

        <br><br>

        <b>Medications:</b>
        {", ".join(
            fhir_patient.get(
                'medications',
                []
            )
        ) or 'None'}

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # EXPLICITLY USE FHIR DATA FOR ASSESSMENT
    # ========================================================

    if st.button(
        "Use FHIR Data for Assessment"
    ):

        # Patient information

        st.session_state[
            "patient_id"
        ] = fhir_patient.get(
            "patient_id"
        )


        st.session_state[
            "patient_name"
        ] = fhir_patient.get(
            "patient_name"
        )


        age = fhir_patient.get(
            "age"
        )

        st.session_state[
            "age"
        ] = (
            int(age)
            if age is not None
            else None
        )


        gender = str(
            fhir_patient.get(
                "gender",
                ""
            )
        ).capitalize()


        st.session_state[
            "sex"
        ] = (
            gender
            if gender in [
                "Male",
                "Female",
                "Other"
            ]
            else "Select sex"
        )


        # ----------------------------------------------------
        # Symptoms
        # ----------------------------------------------------

        symptoms = fhir_patient.get(
            "symptoms",
            []
        )

        st.session_state[
            "symptoms_input"
        ] = ", ".join(
            symptoms
        )


        # ----------------------------------------------------
        # Vitals
        # ----------------------------------------------------

        vitals = fhir_patient.get(
            "vitals",
            {}
        )


        temperature = vitals.get(
            "temperature"
        )

        st.session_state[
            "temperature"
        ] = (
            float(temperature)
            if temperature is not None
            else None
        )


        heart_rate = vitals.get(
            "heart_rate"
        )

        st.session_state[
            "heart_rate"
        ] = (
            int(heart_rate)
            if heart_rate is not None
            else None
        )


        systolic = vitals.get(
            "systolic_bp"
        )

        st.session_state[
            "systolic_bp"
        ] = (
            int(systolic)
            if systolic is not None
            else None
        )


        diastolic = vitals.get(
            "diastolic_bp"
        )

        st.session_state[
            "diastolic_bp"
        ] = (
            int(diastolic)
            if diastolic is not None
            else None
        )


        spo2 = vitals.get(
            "spo2"
        )

        st.session_state[
            "spo2"
        ] = (
            float(spo2)
            if spo2 is not None
            else None
        )


        # ----------------------------------------------------
        # Medical history
        # ----------------------------------------------------

        history = fhir_patient.get(
            "medical_history",
            []
        )

        st.session_state[
            "medical_history"
        ] = ", ".join(
            history
        )


        # ----------------------------------------------------
        # Medications
        # ----------------------------------------------------

        medications = fhir_patient.get(
            "medications",
            []
        )

        st.session_state[
            "current_medications"
        ] = ", ".join(
            medications
        )


        st.rerun()

# ============================================================
# PATIENT ASSESSMENT
# ============================================================

st.markdown(
    '<div class="section-header">'
    '👤 Patient Assessment'
    '</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)

with col1:

    patient_id = st.text_input(
        "Patient ID",
        key="patient_id",
        placeholder="e.g., P001"
    )

with col2:

    patient_name = st.text_input(
        "Patient Name",
        key="patient_name",
        placeholder="e.g., John Doe"
    )

with col3:

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        key="age",
        placeholder="e.g., 25"
    )

with col4:

    sex_options = ["Select sex", "Male", "Female", "Other"]
    sex = st.selectbox(
        "Sex",
        sex_options,
        key="sex"
    )


# ============================================================
# SYMPTOMS
# ============================================================

st.markdown("### 🩺 Symptoms")

symptoms_input = st.text_area(
    "Enter symptoms separated by commas",
    key="symptoms_input",
    placeholder="e.g., fatigue, vomiting, headache",
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
        key="temperature",
        step=0.1,
        placeholder="e.g., 37.0"
    )

with col2:

    heart_rate = st.number_input(
        "Heart Rate (bpm)",
        min_value=20,
        max_value=250,
        key="heart_rate",
        placeholder="e.g., 80"
    )

with col3:

    systolic = st.number_input(
        "Systolic BP",
        min_value=50,
        max_value=250,
        key="systolic_bp",
        placeholder="e.g., 120"
    )

with col4:

    diastolic = st.number_input(
        "Diastolic BP",
        min_value=30,
        max_value=150,
        key="diastolic_bp",
        placeholder="e.g., 80"
    )


spo2 = st.number_input(
    "SpO₂ (%)",
    min_value=0.0,
    max_value=100.0,
    key="spo2",
    step=0.5,
    placeholder="e.g., 98"
)


# ============================================================
# MEDICAL INFORMATION
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 📋 Medical History")

    medical_history = st.text_area(
        "Known medical conditions",
        key="medical_history",
        placeholder="e.g., Hypertension, Diabetes",
        height=100
    )

with col2:

    st.markdown("### 💊 Current Medications")

    medications_input = st.text_area(
        "Enter medications separated by commas",
        key="current_medications",
        placeholder="e.g., Aspirin, Metformin",
        height=100
    )


st.divider()


# ============================================================
# ASSESS BUTTON
# ============================================================

assess = st.button(
    "🔍  ASSESS PATIENT",
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

    predicted_conditions = [label_encoder.inverse_transform([idx])[0] for idx in top_indices]
    hospital_routing_info = route_patient_to_hospital(valid_symptoms, predicted_conditions, "AH-ARAGONDA")


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
    # SAVE TO SESSION STATE
    # ========================================================

    st.session_state["current_assessment"] = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "age": age,
        "sex": sex,
        "valid_symptoms": valid_symptoms,
        "temperature": temperature,
        "heart_rate": heart_rate,
        "systolic_bp": systolic,
        "diastolic_bp": diastolic,
        "spo2": spo2,
        "medical_history": medical_history,
        "medication_list": medication_list,
        "predicted_disease": predicted_disease,
        "top_probability": top_probability,
        "confidence_level": confidence_level,
        "top_indices": top_indices,
        "probabilities": probabilities,
        "label_encoder": label_encoder,
        "hospital_routing_info": hospital_routing_info,
        "risk_flags": risk_flags,
        "medication_alerts": medication_alerts,
        "red_flags": red_flags,
        "information_status": information_status,
        "agent_decision": agent_decision,
        "decision_reason": decision_reason,
        "retrieved_information": retrieved_information
    }

# ============================================================
# RENDER ASSESSMENT RESULTS
# ============================================================

if "current_assessment" in st.session_state and st.session_state["current_assessment"]["patient_id"] == patient_id:

    ca = st.session_state["current_assessment"]
    patient_id = ca["patient_id"]
    patient_name = ca["patient_name"]
    age = ca["age"]
    sex = ca["sex"]
    valid_symptoms = ca["valid_symptoms"]
    temperature = ca["temperature"]
    heart_rate = ca["heart_rate"]
    systolic = ca["systolic_bp"]
    diastolic = ca["diastolic_bp"]
    spo2 = ca["spo2"]
    medical_history = ca["medical_history"]
    medication_list = ca["medication_list"]
    predicted_disease = ca["predicted_disease"]
    top_probability = ca["top_probability"]
    confidence_level = ca["confidence_level"]
    top_indices = ca["top_indices"]
    probabilities = ca["probabilities"]
    label_encoder = ca["label_encoder"]
    risk_flags = ca["risk_flags"]
    medication_alerts = ca["medication_alerts"]
    red_flags = ca["red_flags"]
    information_status = ca["information_status"]
    agent_decision = ca["agent_decision"]
    decision_reason = ca["decision_reason"]
    retrieved_information = ca["retrieved_information"]

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
        hide_index=True
    )


    # ========================================================
    # ROUTING
    # ========================================================
    st.markdown("### 🏥 Apollo Aragonda Hospital Routing")
    st.write(format_routing_result(ca["hospital_routing_info"]))

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

    st.markdown("### 👨‍⚕️ Doctor Briefing")

    st.info("🤖 **Agentic Orchestration Complete:** The Agentic AI has coordinated data from the Patient Context, ML Analysis, Risk Engine, Medication Checker, and Medical Knowledge modules to generate this clinical decision support briefing.")

    briefing_text = ""
    briefing_text += f"**Patient ID:** {patient_id if patient_id else 'N/A'}  \n"
    briefing_text += f"**Patient Name:** {patient_name if patient_name else 'N/A'}  \n"
    briefing_text += f"**Age:** {age if age is not None else 'N/A'}  \n"
    briefing_text += f"**Sex:** {sex if sex != 'Select sex' else 'N/A'}\n\n"

    briefing_text += "#### Reported Symptoms\n"
    for symptom in valid_symptoms:
        briefing_text += f"• {symptom.replace('_', ' ')}\n"

    briefing_text += "\n#### Vital Signs\n"
    briefing_text += f"• Temperature: {temperature if temperature is not None else 'N/A'} °C\n"
    briefing_text += f"• Heart Rate: {heart_rate if heart_rate is not None else 'N/A'} bpm\n"
    briefing_text += f"• Blood Pressure: {systolic if systolic is not None else 'N/A'}/{diastolic if diastolic is not None else 'N/A'} mmHg\n"
    briefing_text += f"• SpO₂: {spo2 if spo2 is not None else 'N/A'}%\n\n"

    briefing_text += "#### Medical History\n"
    if medical_history.strip():
        briefing_text += f"{medical_history}\n\n"
    else:
        briefing_text += "None reported\n\n"

    briefing_text += "#### ML Candidate Assessment\n"
    for rank, index in enumerate(top_indices, start=1):
        disease = label_encoder.inverse_transform([index])[0]
        prob = probabilities[index] * 100
        briefing_text += f"{rank}. {disease} ({prob:.2f}%)\n"

    briefing_text += "\n#### Vital-Risk Findings\n"
    if risk_flags:
        for flag in risk_flags:
            briefing_text += f"⚠ {flag}\n"
    else:
        briefing_text += "No basic vital-sign risk flags detected.\n"

    briefing_text += "\n#### Medication Safety\n"
    if medication_alerts:
        for alert in medication_alerts:
            briefing_text += f"⚠ {alert['medication_1'].title()} + {alert['medication_2'].title()}\n"
            briefing_text += f"Severity: {alert['severity']}\n"
            briefing_text += f"Concern: {alert['message']}\n"
            briefing_text += f"Action: {alert['action']}\n\n"
    elif medication_list:
        briefing_text += "No interactions found in the current knowledge base.\n"
    else:
        briefing_text += "No current medications reported.\n"

    briefing_text += "\n#### Red-Flag Findings\n"
    if red_flags:
        for flag in red_flags:
            briefing_text += f"⚠ {flag}\n"
    else:
        briefing_text += "No configured red-flag symptoms reported.\n"

    briefing_text += f"\n#### Information Status\n{information_status}\n"

    briefing_text += "\n#### Agentic Recommendation\n"
    briefing_text += f"**{agent_decision}**\n\n{decision_reason}\n"

    with st.container(border=True):
        st.markdown(briefing_text)

    # ========================================================
    # SAVE ASSESSMENT
    # ========================================================

    st.divider()
    
    col_save, _ = st.columns([1, 3])
    with col_save:
        # Generate a unique hash for this assessment based on patient inputs and ML results
        current_assessment_hash = hash(f"{patient_id}{predicted_disease}{top_probability}{agent_decision}")
        
        if st.button("💾 Save Assessment", use_container_width=True):
            if st.session_state["current_assessment"]["patient_id"] != patient_id:
                st.error("Assessment patient mismatch. Please reassess the selected patient.")
            elif st.session_state.get("saved_assessment_hash") == current_assessment_hash:
                st.info("This assessment has already been saved.")
            else:
                try:
                    # Save to Supabase
                    save_assessment(
                        patient_id=patient_id,
                        top_prediction=predicted_disease,
                        confidence=float(top_probability),
                        confidence_level=confidence_level,
                        agent_decision=agent_decision,
                        agent_reason=decision_reason,
                        risk_flags=risk_flags,
                        medication_alerts=medication_alerts,
                        briefing_summary=briefing_text,
                        temperature=temperature,
                        heart_rate=heart_rate,
                        systolic_bp=systolic,
                        diastolic_bp=diastolic,
                        spo2=spo2
                    )
                    
                    st.session_state["saved_assessment_hash"] = current_assessment_hash
                    st.success("✅ Assessment saved successfully.  \n🏥 Patient sent to Doctor Dashboard.  \nStatus: 🟡 Waiting for Doctor Consultation")
                except ValueError as ve:
                    st.error(str(ve))
                except Exception as e:
                    st.error("Failed to save assessment.")
                    if "row-level security" in str(e).lower() and "observations" in str(e).lower():
                        st.error("🔒 SUPABASE RLS ERROR: You need to enable INSERT access for the 'observations' table in your Supabase Dashboard!")
                    with st.expander("Technical error details"):
                        st.code(str(e))

# ========================================================
# ASSESSMENT HISTORY
# ========================================================

st.markdown("### 📜 Assessment History")

history_patient_uuid = st.session_state.get("selected_patient_uuid")

if history_patient_uuid:
    try:
        history = get_assessment_history_by_uuid(history_patient_uuid)
        
        if history:
            for past_assessment in history:
                # Format date
                created_at_str = past_assessment.get("created_at", "")
                date_display = created_at_str.split("T")[0] if "T" in created_at_str else created_at_str
                
                with st.expander(f"Assessment on {date_display} - ML: {past_assessment.get('top_prediction')}"):
                    st.markdown(f"**Date:** {created_at_str}")
                    st.markdown(f"**Top ML Candidate:** {past_assessment.get('top_prediction')}")
                    st.markdown(f"**Confidence:** {past_assessment.get('confidence', 0)*100:.2f}% ({past_assessment.get('confidence_level')})")
                    st.markdown(f"**Agentic Decision:** {past_assessment.get('agent_decision')}")
                    st.markdown(f"**Agent Reason:** {past_assessment.get('agent_reason')}")
        else:
            st.info("No previous assessments found for this patient.")
            
    except Exception as e:
        st.error(f"Could not load history: {e}")
else:
    st.warning("Please enter or load a Patient ID to view their assessment history.")

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