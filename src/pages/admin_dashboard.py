import json
import pandas as pd
import joblib

import streamlit as st
import functools

def session_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a unique key for session state
        key = f"sess_cache_{func.__name__}_{args}_{kwargs}"
        if key not in st.session_state:
            st.session_state[key] = func(*args, **kwargs)
        return st.session_state[key]
    return wrapper

import datetime
import sys

MENU_OVERVIEW_DASHBOARD = "Overview Dashboard"
LABEL_SELECT_SEX = "Select sex"

if "supabase_client" in sys.modules:
    del sys.modules["supabase_client"]

from src.services.supabase_client import (
    get_supabase_client,
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
    st.session_state["sex"] = LABEL_SELECT_SEX
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
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0" rel="stylesheet" />
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, div, p, a, h1, h2, h3, h4, h5, h6, label, button, input, select, textarea, table, th, td {
        font-family: 'Inter', sans-serif !important;
    }
    
    [data-testid*="Icon"], [data-testid*="icon"], [class*="icon"], [class*="Icon"], .stIcon, svg, i, .material-symbols-rounded {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }
    
    .stApp { background-color: #f8fafc; }
    
    /* Clean Top Spacing */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebarHeader"] { display: none !important; }
    .block-container { padding-top: 2.5rem !important; padding-bottom: 2rem !important; max-width: 1400px !important; }
    [data-testid="stSidebarUserContent"], [data-testid="stSidebar"] > div:first-child { padding-top: 2.5rem !important; margin-top: 0 !important; }
    
    /* Clean headers */
    .main-title {
        color: #0f172a;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }
    .main-subtitle {
        color: #64748b;
        font-size: 16px;
        font-weight: 400;
        margin-bottom: 30px;
    }
    
    .patient-header, .section-title {
        color: #0f172a !important;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 10px;
        margin-bottom: 25px;
        font-weight: 700;
    }
    
    .patient-header {
        background-color: #ffffff;
        padding: 25px 30px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #0284c7;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    .patient-header h1 { font-size: 28px; margin: 0; font-weight: 800; color: #0f172a; border: none; }
    .patient-header p { font-size: 15px; color: #64748b; margin-top: 5px; }
    
    .section-header { font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 20px; margin-bottom: 15px; }
    
    /* Clean Cards */
    .card-container, .metric-card, .workspace-section, .result-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .metric-card {
        border-top: 4px solid #0284c7;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    
    .metric-title, .small-label { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
    .metric-value, .big-result { font-size: 28px; font-weight: 800; color: #0f172a; margin-bottom: 0px; }
    .result-title { font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 15px; }
    
    /* Native Streamlit Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }
    div[data-testid="metric-container"] label {
        color: #64748b !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 32px !important;
        font-weight: 800 !important;
    }
    
    /* Medical Alert/Info Boxes */
    .disclaimer-box { background-color: #fefce8; border-left: 4px solid #eab308; padding: 15px; border-radius: 8px; color: #854d0e; font-size: 14px; margin-bottom: 15px; }
    .briefing-box, .doctor-box { background-color: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 15px; border-radius: 8px; color: #0369a1; font-size: 14px; margin-bottom: 15px; }
    .agent-box, .ai-box { background-color: #f8fafc; border-left: 4px solid #475569; padding: 15px; border-radius: 8px; color: #334155; font-size: 14px; margin-bottom: 15px; }
    
    .warning-note { font-size: 13px; color: #b45309; }
    .workspace-title { font-size: 18px; font-weight: 700; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 15px; }
    
    /* ---------------- DARK SIDEBAR ---------------- */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* Deep Slate */
        border-right: 1px solid #1e293b !important;
    }
    .sidebar-title { color: #64748b !important; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0 !important; margin-bottom: 12px !important; padding-left: 28px !important; margin-left: 0 !important; }
    .status-ok { display: flex; align-items: center; font-size: 13px; color: #94a3b8; font-weight: 500; margin-bottom: 8px; }
    .status-dot { width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; margin-right: 10px; }
    
    /* Sidebar Radio to Premium Dark Pills */
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px !important; padding: 0 !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label div:first-child { display: none !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 12px 12px !important;
        margin-left: 16px !important;
        margin-right: 16px !important;
        width: calc(100% - 32px) !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%) !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(2, 132, 199, 0.2) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #94a3b8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] p,
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Badges */
    .badge-waiting { background-color: #fefce8; color: #854d0e; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; border: 1px solid #fde047; }
    .badge-completed { background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; border: 1px solid #86efac; }
    .badge-in-consult { background-color: #e0f2fe; color: #075985; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; border: 1px solid #7dd3fc; }
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

@session_cache
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


def _check_temperature(temperature, risk_flags):
    if temperature is not None:
        if temperature >= 39:
            risk_flags.append("High temperature detected")
        elif temperature < 35:
            risk_flags.append("Low temperature detected")

def _check_heart_rate(heart_rate, risk_flags):
    if heart_rate is not None:
        if heart_rate > 100:
            risk_flags.append("Elevated heart rate detected")
        elif heart_rate < 60:
            risk_flags.append("Low heart rate detected")

def _check_blood_pressure(systolic, diastolic, risk_flags):
    if systolic is not None and diastolic is not None:
        if systolic >= 140 or diastolic >= 90:
            risk_flags.append("Elevated blood pressure detected")
        elif systolic < 90 or diastolic < 60:
            risk_flags.append("Low blood pressure detected")

def _check_spo2(spo2, risk_flags):
    if spo2 is not None:
        if spo2 < 90:
            risk_flags.append("Low oxygen saturation detected")
        elif spo2 < 94:
            risk_flags.append("Reduced oxygen saturation detected")

def calculate_risk_flags(temperature, heart_rate, systolic, diastolic, spo2):
    risk_flags = []
    _check_temperature(temperature, risk_flags)
    _check_heart_rate(heart_rate, risk_flags)
    _check_blood_pressure(systolic, diastolic, risk_flags)
    _check_spo2(spo2, risk_flags)
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


with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 24px; margin-top: 0; padding-left: 16px;">
            <div style="background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%); min-width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 15px; box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
            </div>
            <div>
                <div style="font-size: 18px; font-weight: 800; color: #ffffff; line-height: 1.1;">Admin Console</div>
                <div style="font-size: 13px; font-weight: 500; color: #94a3b8;">Agentic AI Systems</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    'Apollo Aragonda AI Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Intelligent clinical decision-support and autonomous routing system.'
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
st.sidebar.markdown('<div class="sidebar-title" style="margin-bottom: 0;">Main Menu</div>', unsafe_allow_html=True)

menu_options = [MENU_OVERVIEW_DASHBOARD, "AI Assessment Workspace", "System Logout"]

if "app_menu_selection" not in st.session_state:
    st.session_state["app_menu_selection"] = MENU_OVERVIEW_DASHBOARD

def handle_menu_change():
    if st.session_state.get("app_menu_selection") == "System Logout":
        st.session_state["app_menu_selection"] = MENU_OVERVIEW_DASHBOARD
        st.session_state["authenticated"] = False
        st.session_state["user_role"] = None
        st.query_params.clear()

# Use radio instead of buttons for a cleaner menu feel
st.sidebar.radio(
    "Navigation",
    menu_options,
    key="app_menu_selection",
    on_change=handle_menu_change,
    label_visibility="collapsed"
)

# If the callback logged us out, force a rerun to go back to the login page
if not st.session_state.get("authenticated", False):
    st.rerun()

menu = st.session_state.get("app_menu_selection", MENU_OVERVIEW_DASHBOARD)

ca = st.session_state.get("current_assessment")

if menu == MENU_OVERVIEW_DASHBOARD:
    # Complete Custom HTML Admin Dashboard
    # CRITICAL: Do not use empty lines in this string, or Streamlit's Markdown parser will break the HTML!
    dashboard_html = """
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px;">
        <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Total Patients Registered</div>
            <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1;">1,248</div>
            <div style="color: #10b981; font-size: 13px; font-weight: 600; margin-top: 12px;">↑ 12% this month</div>
        </div>
        <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">AI Assessments</div>
            <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1;">432</div>
            <div style="color: #10b981; font-size: 13px; font-weight: 600; margin-top: 12px;">↑ 5% this week</div>
        </div>
        <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Critical Alerts</div>
            <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1;">18</div>
            <div style="color: #ef4444; font-size: 13px; font-weight: 600; margin-top: 12px;">Immediate review required</div>
        </div>
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 24px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
            <div style="color: #94a3b8; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">System Core Status</div>
            <div style="color: white; font-size: 28px; font-weight: 800; line-height: 1.2;">All Agents<br>Operational</div>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
        <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <h3 style="color: #0f172a; font-size: 18px; margin-top: 0; margin-bottom: 20px; font-weight: 800;">Recent AI Routing Activity</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr style="border-bottom: 1px solid #e2e8f0; color: #64748b; text-align: left;">
                    <th style="padding: 12px 10px; font-weight: 600;">Patient ID</th>
                    <th style="padding: 12px 10px; font-weight: 600;">Primary Symptom</th>
                    <th style="padding: 12px 10px; font-weight: 600;">AI Decision</th>
                    <th style="padding: 12px 10px; font-weight: 600; text-align: right;">Time</th>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 14px 10px; color: #0f172a; font-weight: 600;">P-8472</td>
                    <td style="padding: 14px 10px; color: #475569;">Severe Chest Pain</td>
                    <td style="padding: 14px 10px;"><span style="background: #fee2e2; color: #ef4444; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">ER ROUTING</span></td>
                    <td style="padding: 14px 10px; color: #64748b; text-align: right;">2 mins ago</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 14px 10px; color: #0f172a; font-weight: 600;">P-3921</td>
                    <td style="padding: 14px 10px; color: #475569;">Mild Fever, Cough</td>
                    <td style="padding: 14px 10px;"><span style="background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">GENERAL WARD</span></td>
                    <td style="padding: 14px 10px; color: #64748b; text-align: right;">15 mins ago</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 14px 10px; color: #0f172a; font-weight: 600;">P-1049</td>
                    <td style="padding: 14px 10px; color: #475569;">Chronic Back Pain</td>
                    <td style="padding: 14px 10px;"><span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">OPD APPOINTMENT</span></td>
                    <td style="padding: 14px 10px; color: #64748b; text-align: right;">1 hour ago</td>
                </tr>
                <tr>
                    <td style="padding: 14px 10px; color: #0f172a; font-weight: 600;">P-5582</td>
                    <td style="padding: 14px 10px; color: #475569;">Dizziness, High BP</td>
                    <td style="padding: 14px 10px;"><span style="background: #fef3c7; color: #b45309; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">URGENT CARE</span></td>
                    <td style="padding: 14px 10px; color: #64748b; text-align: right;">2 hours ago</td>
                </tr>
            </table>
        </div>
        <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <h3 style="color: #0f172a; font-size: 18px; margin-top: 0; margin-bottom: 25px; font-weight: 800;">Agentic Operations</h3>
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #475569; font-size: 13px; font-weight: 600;">Diagnostic Accuracy</span>
                    <span style="color: #0f172a; font-size: 13px; font-weight: 800;">94.2%</span>
                </div>
                <div style="width: 100%; background: #f1f5f9; border-radius: 6px; height: 10px; overflow: hidden;">
                    <div style="width: 94.2%; background: #0ea5e9; height: 100%;"></div>
                </div>
            </div>
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #475569; font-size: 13px; font-weight: 600;">Routing Efficiency</span>
                    <span style="color: #0f172a; font-size: 13px; font-weight: 800;">98.5%</span>
                </div>
                <div style="width: 100%; background: #f1f5f9; border-radius: 6px; height: 10px; overflow: hidden;">
                    <div style="width: 98.5%; background: #10b981; height: 100%;"></div>
                </div>
            </div>
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #475569; font-size: 13px; font-weight: 600;">Model Latency</span>
                    <span style="color: #0f172a; font-size: 13px; font-weight: 800;">120ms</span>
                </div>
                <div style="width: 100%; background: #f1f5f9; border-radius: 6px; height: 10px; overflow: hidden;">
                    <div style="width: 15%; background: #f59e0b; height: 100%;"></div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(dashboard_html, unsafe_allow_html=True)
    st.stop()
    
# If menu == "AI Assessment Workspace", it falls through to the rest of the file

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


    # Modern, sleek patient profile grid
    st.markdown(f"""
<div class="patient-header" style="margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
<h1 style="font-size: 24px; display: flex; align-items: center; margin: 0; color: #0f172a;"><span class="material-symbols-rounded" style="color: #0ea5e9; margin-right: 12px; font-size: 32px;">account_circle</span> {fhir_patient.get('patient_name', 'N/A')}</h1>
<div style="background: #f1f5f9; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 700; color: #475569; border: 1px solid #cbd5e1;">ID: {fhir_patient.get('patient_id', 'N/A')}</div>
</div>
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #e2e8f0;">
<div>
<div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">Age</div>
<div style="color: #0f172a; font-size: 16px; font-weight: 600;">{fhir_patient.get('age', 'N/A')} yrs</div>
</div>
<div>
<div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">Sex</div>
<div style="color: #0f172a; font-size: 16px; font-weight: 600;">{str(fhir_patient.get('gender', 'N/A')).title()}</div>
</div>
<div style="grid-column: span 2;">
<div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">Vitals Overview</div>
<div style="color: #0f172a; font-size: 13px; font-weight: 500; background: #f8fafc; padding: 6px 12px; border-radius: 6px; border: 1px solid #e2e8f0; display: inline-block;">
Temp: <b>{vitals.get('temperature', 'N/A')}°C</b> &nbsp;|&nbsp; HR: <b>{vitals.get('heart_rate', 'N/A')}</b> &nbsp;|&nbsp; BP: <b>{vitals.get('systolic_bp', 'N/A')}/{vitals.get('diastolic_bp', 'N/A')}</b> &nbsp;|&nbsp; SpO₂: <b>{vitals.get('spo2', 'N/A')}%</b>
</div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
<div style="background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
<div style="color: #0284c7; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center;"><span class="material-symbols-rounded" style="font-size: 16px; margin-right: 6px;">history</span> Medical History</div>
<div style="color: #334155; font-size: 14px; font-weight: 500; line-height: 1.5;">{", ".join(fhir_patient.get('medical_history', [])) or 'None reported'}</div>
</div>
<div style="background: #fef2f2; padding: 15px; border-radius: 8px; border: 1px solid #fee2e2;">
<div style="color: #ef4444; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center;"><span class="material-symbols-rounded" style="font-size: 16px; margin-right: 6px;">sick</span> Current Symptoms</div>
<div style="color: #7f1d1d; font-size: 14px; font-weight: 500; line-height: 1.5;">{", ".join(fhir_patient.get('symptoms', [])) or 'None reported'}</div>
</div>
<div style="background: #f0fdf4; padding: 15px; border-radius: 8px; border: 1px solid #dcfce3;">
<div style="color: #166534; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center;"><span class="material-symbols-rounded" style="font-size: 16px; margin-right: 6px;">prescriptions</span> Medications</div>
<div style="color: #14532d; font-size: 14px; font-weight: 500; line-height: 1.5;">{", ".join(fhir_patient.get('medications', [])) or 'None reported'}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


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
            else LABEL_SELECT_SEX
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

    sex_options = [LABEL_SELECT_SEX, "Male", "Female", "Other"]
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
        st.markdown(f"""
<div class="result-card" style="height: 100%;">
<div class="result-title">🤖 ML Prediction</div>
<div class="small-label" style="margin-top: 15px;">Top Candidate</div>
<div class="big-result" style="font-size: 24px;">{predicted_disease}</div>
<div style="margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 15px;">
<div style="font-size: 13px; color: #64748b; text-transform: uppercase; font-weight: 600;">Probability</div>
<div style="font-size: 22px; font-weight: 700; color: #0f172a;">{top_probability * 100:.2f}%</div>
</div>
<div style="margin-top: 8px; font-size: 13px; color: #64748b;">
Confidence: <span style="font-weight: 600; color: #0ea5e9;">{confidence_level}</span>
</div>
<div class="warning-note" style="margin-top: 15px; background: #fffbeb; padding: 10px; border-radius: 6px; border-left: 3px solid #f59e0b;">
ML candidate — not a confirmed diagnosis.
</div>
</div>
""", unsafe_allow_html=True)

    with col2:
        risk_html = ""
        if risk_flags:
            for flag in risk_flags:
                risk_html += f'<div style="background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 15px; border-radius: 10px; margin-bottom: 12px; display: flex; align-items: flex-start; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><span class="material-symbols-rounded" style="color: #dc2626; margin-right: 12px; font-size: 22px; margin-top: -2px;">warning</span><div style="font-size: 14px; font-weight: 600; line-height: 1.4;">{flag}</div></div>'
        else:
            risk_html = '<div style="background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 20px 15px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><span class="material-symbols-rounded" style="color: #22c55e; font-size: 48px; margin-bottom: 12px;">check_circle</span><div style="font-size: 15px; font-weight: 700;">All Vitals Stable</div><div style="font-size: 13px; color: #15803d; margin-top: 4px; font-weight: 500;">No basic vital-sign risk flags detected</div></div>'
            
        st.markdown(f"""
<div class="result-card" style="height: 100%;">
<div class="result-title">❤️ Vital Risk</div>
<div style="margin-top: 15px;">
{risk_html}
</div>
</div>
""", unsafe_allow_html=True)

    with col3:
        med_html = ""
        if not medication_list:
            med_html = '<div style="background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; padding: 20px 15px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><span class="material-symbols-rounded" style="color: #94a3b8; font-size: 48px; margin-bottom: 12px;">info</span><div style="font-size: 15px; font-weight: 700;">No Medications</div><div style="font-size: 13px; color: #64748b; margin-top: 4px; font-weight: 500;">No current medications reported.</div></div>'
        elif not medication_alerts:
            med_html = '<div style="background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 20px 15px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><span class="material-symbols-rounded" style="color: #22c55e; font-size: 48px; margin-bottom: 12px;">verified_user</span><div style="font-size: 15px; font-weight: 700;">Safe to Proceed</div><div style="font-size: 13px; color: #15803d; margin-top: 4px; font-weight: 500;">No interactions found in knowledge base.</div></div>'
        else:
            for alert in medication_alerts:
                med_html += f'<div style="background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 15px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);"><div style="display: flex; align-items: center; margin-bottom: 6px;"><span class="material-symbols-rounded" style="color: #dc2626; margin-right: 10px; font-size: 20px;">dangerous</span> <span style="font-size: 14px; font-weight: 700;">{alert["medication_1"].title()} + {alert["medication_2"].title()}</span></div><div style="font-size: 12px; font-weight: 800; text-transform: uppercase; color: #dc2626; margin-left: 30px; margin-bottom: 4px;">Severity: {alert["severity"]}</div><div style="font-size: 13px; color: #7f1d1d; line-height: 1.4; margin-left: 30px;">{alert["message"]}</div></div>'

        st.markdown(f"""
<div class="result-card" style="height: 100%;">
<div class="result-title">💊 Medication Safety</div>
<div style="margin-top: 15px;">
{med_html}
</div>
</div>
""", unsafe_allow_html=True)


    # ========================================================
    # TOP 5
    # ========================================================

    st.markdown('<h3 style="margin-top: 30px; margin-bottom: 20px; font-size: 20px; font-weight: 800; color: #0f172a; display: flex; align-items: center;"><span class="material-symbols-rounded" style="color: #ef4444; margin-right: 10px; font-size: 26px;">monitoring</span> Top 5 ML Candidates</h3>', unsafe_allow_html=True)

    top5_html = '<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">'
    
    for rank, index in enumerate(top_indices, start=1):
        disease = label_encoder.inverse_transform([index])[0]
        probability = probabilities[index] * 100
        
        if rank == 1:
            color = "#0ea5e9"
            bg_color = "#e0f2fe"
        elif rank == 2:
            color = "#3b82f6"
            bg_color = "#eff6ff"
        else:
            color = "#94a3b8"
            bg_color = "#f1f5f9" 
        
        border_bottom = 'border-bottom: 1px solid #f1f5f9;' if rank < 5 else ''
        margin_bottom = 'margin-bottom: 15px;' if rank < 5 else ''
        padding_bottom = 'padding-bottom: 15px;' if rank < 5 else ''
        
        font_weight = "800" if rank == 1 else "600"
        font_size = "16px" if rank == 1 else "15px"
        
        top5_html += f'''
<div style="display: flex; align-items: center; {margin_bottom} {padding_bottom} {border_bottom}">
<div style="width: 32px; height: 32px; border-radius: 50%; background: {bg_color}; color: {color}; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px; margin-right: 15px; flex-shrink: 0;">{rank}</div>
<div style="flex-grow: 1;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
<span style="font-weight: {font_weight}; font-size: {font_size}; color: #0f172a;">{disease}</span>
<span style="font-weight: 800; color: {color}; font-size: 14px;">{probability:.2f}%</span>
</div>
<div style="width: 100%; background: #f1f5f9; border-radius: 6px; height: 8px; overflow: hidden;">
<div style="width: {probability}%; background: {color}; height: 100%; border-radius: 6px;"></div>
</div>
</div>
</div>
'''

    top5_html += '</div>'
    st.markdown(top5_html, unsafe_allow_html=True)


    # ========================================================
    # ROUTING
    # ========================================================
    st.markdown("### 🏥 Apollo Aragonda Hospital Routing")
    
    routing_info = ca.get("hospital_routing_info", {})
    if routing_info and routing_info.get("success"):
        
        # Build doctor list HTML
        doctors = routing_info.get("doctors", [])
        if doctors:
            docs_html = '<div style="display: flex; flex-direction: column; gap: 8px;">'
            for doc in doctors:
                docs_html += f'<div style="display: flex; align-items: center; font-size: 14px;"><span class="material-symbols-rounded" style="color: #64748b; font-size: 16px; margin-right: 8px;">stethoscope</span> <b>{doc.get("name")}</b> &nbsp;<span style="color: #64748b;">({doc.get("speciality")})</span></div>'
            docs_html += '</div>'
        else:
            docs_html = '<div style="color: #64748b; font-size: 14px;">No relevant listed doctors found.</div>'
            
        st.markdown(f"""
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #0284c7; padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="display: flex; align-items: center; margin-bottom: 20px;">
<span class="material-symbols-rounded" style="color: #0284c7; font-size: 32px; margin-right: 15px;">local_hospital</span>
<div>
<div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">Selected Facility</div>
<div style="color: #0f172a; font-size: 20px; font-weight: 800;">{routing_info.get('hospital', {}).get('name', 'Apollo Hospitals')}</div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 2fr; gap: 30px; background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #f1f5f9; margin-bottom: 20px;">
<div>
<div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Suggested Speciality</div>
<div style="color: #0ea5e9; font-size: 18px; font-weight: 700;">{routing_info.get('speciality', 'N/A')}</div>
</div>
<div>
<div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Relevant Listed Doctor(s)</div>
{docs_html}
</div>
</div>
<div style="background: #eff6ff; color: #1e3a8a; padding: 15px; border-radius: 8px; font-size: 14px; border: 1px solid #bfdbfe; display: flex; align-items: flex-start;">
<span class="material-symbols-rounded" style="font-size: 20px; margin-right: 10px; margin-top: 2px;">info</span>
<div>
<b style="font-weight: 700;">Routing Rationale:</b> {routing_info.get('message', '')}
<div style="margin-top: 8px; font-size: 12px; opacity: 0.8;">Note: This is hospital routing decision support and does not constitute a medical diagnosis.</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No routing information available.")

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

    elif agent_decision in (
        "PRIORITIZE CLINICAL RISK REVIEW",
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

    # HTML Template for Premium Doctor Briefing
    briefing_html = f'''
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 30px;">
<!-- Header -->
<div style="background: #0f172a; color: #ffffff; padding: 25px 30px; display: flex; align-items: center; justify-content: space-between;">
<div>
<div style="font-size: 13px; font-weight: 600; text-transform: uppercase; color: #94a3b8; letter-spacing: 1px; margin-bottom: 4px;">Clinical Support Document</div>
<div style="font-size: 24px; font-weight: 800; display: flex; align-items: center;"><span class="material-symbols-rounded" style="color: #38bdf8; margin-right: 12px; font-size: 28px;">clinical_notes</span> Doctor Briefing</div>
</div>
<div style="text-align: right;">
<div style="font-size: 13px; color: #94a3b8;">Patient ID</div>
<div style="font-size: 18px; font-weight: 700; color: #e2e8f0;">{patient_id if patient_id else 'N/A'}</div>
</div>
</div>
<!-- Patient Context Strip -->
<div style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; padding: 15px 30px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
<div><div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Name</div><div style="font-size: 14px; font-weight: 600; color: #0f172a;">{patient_name if patient_name else 'N/A'}</div></div>
<div><div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Age</div><div style="font-size: 14px; font-weight: 600; color: #0f172a;">{age if age is not None else 'N/A'}</div></div>
<div><div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Sex</div><div style="font-size: 14px; font-weight: 600; color: #0f172a;">{sex if sex != 'Select sex' else 'N/A'}</div></div>
<div><div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Status</div><div style="font-size: 14px; font-weight: 600; color: #0284c7;">Evaluated</div></div>
</div>
<div style="padding: 30px;">
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
<!-- Symptoms & Vitals -->
<div>
<div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Reported Symptoms</div>
<ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px; margin-bottom: 25px;">
{"".join([f"<li style='margin-bottom: 6px;'>{symptom.replace('_', ' ').title()}</li>" for symptom in valid_symptoms]) if valid_symptoms else "<li>None reported</li>"}
</ul>
<div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Vital Signs</div>
<div style="background: #f1f5f9; padding: 15px; border-radius: 8px; font-size: 14px; color: #0f172a; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
<div><b>Temp:</b> {temperature if temperature is not None else 'N/A'} °C</div>
<div><b>HR:</b> {heart_rate if heart_rate is not None else 'N/A'} bpm</div>
<div><b>BP:</b> {systolic if systolic is not None else 'N/A'}/{diastolic if diastolic is not None else 'N/A'} mmHg</div>
<div><b>SpO₂:</b> {spo2 if spo2 is not None else 'N/A'}%</div>
</div>
</div>
<!-- History & Alerts -->
<div>
<div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Medical History</div>
<div style="color: #334155; font-size: 14px; line-height: 1.6; margin-bottom: 25px; padding: 12px; background: #f8fafc; border-radius: 8px; border: 1px solid #f1f5f9;">
{medical_history if medical_history.strip() else 'None reported'}
</div>
<div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Critical Alerts</div>
<div style="display: flex; flex-direction: column; gap: 10px;">
{"".join([f'<div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 10px 15px; font-size: 13px; color: #991b1b;"><b style="color: #dc2626;">⚠ VITAL RISK:</b> {flag}</div>' for flag in risk_flags]) if risk_flags else ""}
{"".join([f'<div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 10px 15px; font-size: 13px; color: #991b1b;"><b style="color: #dc2626;">⚠ MEDICATION:</b> {alert["medication_1"].title()} + {alert["medication_2"].title()} ({alert["severity"]})</div>' for alert in medication_alerts]) if medication_alerts else ""}
{"".join([f'<div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 10px 15px; font-size: 13px; color: #991b1b;"><b style="color: #dc2626;">⚠ RED FLAG:</b> {flag}</div>' for flag in red_flags]) if red_flags else ""}
{"" if risk_flags or medication_alerts or red_flags else '<div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 10px 15px; font-size: 13px; color: #166534;"><span class="material-symbols-rounded" style="font-size: 16px; vertical-align: text-bottom;">check_circle</span> No critical alerts detected.</div>'}
</div>
</div>
</div>
<!-- Agentic Recommendation -->
<div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 25px;">
<div style="display: flex; align-items: center; margin-bottom: 15px;">
<span class="material-symbols-rounded" style="color: #0284c7; font-size: 28px; margin-right: 12px;">smart_toy</span>
<div style="font-size: 18px; font-weight: 800; color: #0369a1;">Agentic Recommendation</div>
</div>
<div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 10px;">{agent_decision}</div>
<div style="font-size: 14px; color: #334155; line-height: 1.6;">{decision_reason}</div>
</div>
</div>
</div>
'''

    st.markdown(briefing_html, unsafe_allow_html=True)

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
                        briefing_summary=briefing_html,
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