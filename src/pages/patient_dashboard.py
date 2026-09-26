import streamlit as st
import pandas as pd
import json

from src.services.supabase_client import (
    supabase,
    get_patient_profile,
    get_assessment_history_by_uuid,
    get_patient_risk_flags,
    get_patient_medication_alerts
)
from src.fhir.parser import _load_fhir_database

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
# CHECK AUTHENTICATION
# ============================================================
if not st.session_state.get("authenticated") or st.session_state.get("user_role") != "patient":
    st.error("Unauthorized. Please login from the main page.")
    st.stop()

selected_patient_code = st.session_state.get("patient_id")
selected_patient_uuid = st.session_state.get("patient_uuid")

if not selected_patient_code or not selected_patient_uuid:
    st.error("Patient session invalid. Please login again.")
    st.stop()

# ============================================================
# LOAD PATIENT DATA (ONCE)
# ============================================================
try:
    patient_profile = get_patient_profile(selected_patient_code)
except Exception as e:
    st.error("Unable to load your medical information. Please try again or contact the hospital.")
    st.stop()

if not patient_profile:
    st.error("Unable to load your medical information. Please try again or contact the hospital.")
    st.stop()

# 1. Doctor Visits
visits_response = (
    supabase
    .table("doctor_visits")
    .select("*, doctors(name)")
    .eq("patient_id", selected_patient_uuid)
    .order("visit_date", desc=True)
    .execute()
)
doctor_visits = visits_response.data if visits_response.data else []
latest_visit = doctor_visits[0] if doctor_visits else None

# 2. Doctor Medications
medications_response = (
    supabase
    .table("doctor_medications")
    .select("*")
    .eq("patient_id", selected_patient_uuid)
    .execute()
)
doctor_medications = medications_response.data if medications_response.data else []

# 3. AI Assessments & Risks
ai_assessments = get_assessment_history_by_uuid(selected_patient_uuid)
latest_assessment = ai_assessments[0] if ai_assessments else None

risk_flags = get_patient_risk_flags(selected_patient_uuid)
med_alerts = get_patient_medication_alerts(selected_patient_uuid)

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown(f'''
<div class="sidebar-profile">
    <h3>👤 {patient_profile.get('patient_name')}</h3>
    <p>Patient ID: {selected_patient_code}</p>
</div>
''', unsafe_allow_html=True)

if "pat_menu_selection" not in st.session_state:
    st.session_state["pat_menu_selection"] = "🏠 Dashboard"

nav_items = [
    "🏠 Dashboard",
    "📅 Medical History",
    "🏥 Hospital & AI",
    "👤 My Profile",
    "⚙️ Settings"
]

for item in nav_items:
    if st.sidebar.button(item, use_container_width=True, type="primary" if st.session_state["pat_menu_selection"] == item else "secondary"):
        st.session_state["pat_menu_selection"] = item
        st.rerun()

menu = st.session_state["pat_menu_selection"]

# ============================================================
# PAGE RENDERING
# ============================================================

# ------------------------------------------------------------
# 🏠 Dashboard
# ------------------------------------------------------------
if menu == "🏠 Dashboard":
    st.markdown(f'''
    <div class="patient-header" style="background: linear-gradient(135deg, rgba(128, 128, 128, 0.05) 0%, rgba(128, 128, 128, 0.02) 100%); backdrop-filter: blur(10px); padding: 30px; border-radius: 16px; margin-bottom: 30px; border: 1px solid rgba(128,128,128,0.2); box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <h1 style="margin: 0; font-size: 28px; font-weight: 800;">Welcome, {patient_profile.get('patient_name')}</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 16px;"><strong>Patient ID:</strong> {selected_patient_code} &nbsp;|&nbsp; <strong>Hospital:</strong> Apollo Hospitals, Aragonda</p>
    </div>
    ''', unsafe_allow_html=True)
    
    current_care = latest_visit.get("diagnosis") if latest_visit and latest_visit.get("diagnosis") else "No active diagnosis"
    last_visit_date = latest_visit.get("visit_date") if latest_visit else "No recent visits"
    
    follow_up = latest_visit.get("follow_up_date") if latest_visit else None
    if not follow_up or str(follow_up).strip().lower() == "none":
        follow_up_display = "No follow-up"
    else:
        follow_up_display = str(follow_up)
        
    med_count = str(len(doctor_medications))
    
    dashboard_html = f"""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px;">
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Current Care Status</div>
        <div style="color: #0f172a; font-size: 20px; font-weight: 800; line-height: 1.2;">{current_care}</div>
    </div>
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Last Doctor Visit</div>
        <div style="color: #0f172a; font-size: 24px; font-weight: 800; line-height: 1.2;">{last_visit_date}</div>
    </div>
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Next Follow-up</div>
        <div style="color: #0f172a; font-size: 24px; font-weight: 800; line-height: 1.2; color: #f59e0b;">{follow_up_display}</div>
    </div>
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Current Medicines</div>
        <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1.2; color: #0ea5e9;">{med_count}</div>
    </div>
</div>
"""
    st.markdown(dashboard_html, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    st.markdown("### A. Current Doctor-Recorded Conditions")
    if doctor_visits and any(v.get("diagnosis") for v in doctor_visits):
        with st.container():
            for v in doctor_visits:
                diag = v.get("diagnosis")
                if diag and str(diag).strip().lower() != "none":
                    st.markdown(f'<div class="doctor-box"><strong>{v.get("visit_date")}:</strong> {diag} <br><small><em>Diagnosed by Dr. {v.get("doctors", {}).get("name", "Unknown")}</em></small></div>', unsafe_allow_html=True)
    else:
        st.info("No doctor-recorded diagnosis available.")
        
    st.markdown("### B. Pre-existing Medical History")
    history = patient_profile.get("medical_history", [])
    if history:
        for item in history:
            st.markdown(f"- {item}")
    else:
        st.info("No recorded pre-existing conditions.")
        
    st.markdown("### C. Latest Vital Signs")
    vitals = patient_profile.get("vitals", {})
    if any(v is not None for v in vitals.values()):
        vc1, vc2, vc3, vc4, vc5 = st.columns(5)
        vc1.metric("Heart Rate", f"{vitals.get('heart_rate', 'N/A')} bpm")
        vc2.metric("SpO₂", f"{vitals.get('spo2', 'N/A')} %")
        vc3.metric("Temp", f"{vitals.get('temperature', 'N/A')} °C")
        vc4.metric("Systolic BP", f"{vitals.get('systolic_bp', 'N/A')} mmHg")
        vc5.metric("Diastolic BP", f"{vitals.get('diastolic_bp', 'N/A')} mmHg")
    else:
        st.info("No vital signs recorded recently.")
        
    st.markdown("### D. Reported Symptoms")
    symptoms = patient_profile.get("symptoms", [])
    if symptoms:
        for sym in symptoms:
            st.markdown(f"- {sym.replace('_', ' ').title()}")
    else:
        st.info("No current symptoms reported.")

# ------------------------------------------------------------
# 📅 Medical History
# ------------------------------------------------------------
elif menu == "📅 Medical History":
    st.markdown('<h2 class="section-title">📅 Medical History</h2>', unsafe_allow_html=True)
    
    tabs = st.tabs(["Visits & Notes", "Medicines", "Medical Records Download"])
    
    with tabs[0]:
        if not doctor_visits:
            st.info("No previous visits found.")
        else:
            for visit in doctor_visits:
                with st.expander(f"📅 {visit.get('visit_date')} - Dr. {visit.get('doctors', {}).get('name', 'Unknown')}"):
                    st.markdown(f"**Diagnosis:** {visit.get('diagnosis', 'None recorded')}")
                    st.markdown(f"**Doctor Notes:** {visit.get('doctor_notes', 'None recorded')}")
                    st.markdown(f"**Future Care Plan:** {visit.get('future_plan', 'None recorded')}")
                    fup = visit.get('follow_up_date')
                    fup_str = fup if fup and str(fup).strip().lower() != "none" else "No follow-up scheduled."
                    st.markdown(f"**Follow-up:** {fup_str}")

    with tabs[1]:
        if not doctor_medications:
            st.info("No prescriptions have been recorded.")
        else:
            for med in doctor_medications:
                st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
                st.markdown(f"### 💊 {med.get('medication_name').title()}")
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.markdown(f"**Dosage:** {med.get('dosage', 'N/A')}")
                    st.markdown(f"**Frequency:** {med.get('frequency', 'N/A')}")
                with mc2:
                    st.markdown(f"**Duration:** {med.get('duration', 'N/A')}")
                    st.markdown(f"**Prescribed by:** Dr. {med.get('doctor_name', 'Unknown')}")
                st.markdown(f"**Instructions:** {med.get('instructions', 'None')}")
                st.markdown('</div>', unsafe_allow_html=True)

    with tabs[2]:
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 📝 Detailed Medical Report")
            st.write("A beautifully formatted HTML report of your profile, visits, and medications.")
            
            visits_html = ""
            if not doctor_visits:
                visits_html = "<p>No recorded visits.</p>"
            else:
                for v in doctor_visits:
                    doc_name = v.get('doctors', {}).get('name', 'Unknown')
                    visits_html += f'''
                    <div class='visit-block'>
                        <h4>Date: {v.get('visit_date')} | Dr. {doc_name}</h4>
                        <p><strong>Diagnosis:</strong> {v.get('diagnosis', 'None')}</p>
                        <p><strong>Notes:</strong> {v.get('doctor_notes', 'None')}</p>
                        <p><strong>Plan:</strong> {v.get('future_plan', 'None')}</p>
                        <p><strong>Follow-up:</strong> {v.get('follow_up_date', 'None')}</p>
                    </div>
                    '''
                    
            meds_html = ""
            if not doctor_medications:
                meds_html = "<p>No recorded medications.</p>"
            else:
                meds_html = "<ul>"
                for m in doctor_medications:
                    meds_html += f"<li><strong>{m.get('medication_name')}</strong> - {m.get('dosage')} ({m.get('frequency')}) for {m.get('duration')}</li>"
                meds_html += "</ul>"
                
            import datetime
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                
            html_report = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Medical Report - {patient_profile.get('patient_name')}</title>
                <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    .stApp { background-color: #F8F9FA; }
    
    /* Clean headers */
    .patient-header, .main-title, .section-title {
        color: #0056b3 !important;
        border-bottom: 2px solid #E3F2FD;
        padding-bottom: 10px;
        margin-bottom: 25px;
        font-weight: 700;
    }
    
    .patient-header {
        background-color: #FFFFFF;
        padding: 25px 30px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        border-left: 6px solid #0056b3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .patient-header h1 { font-size: 32px; margin: 0; font-weight: 800; color: #212529; border: none; }
    .patient-header p { font-size: 15px; color: #6c757d; margin-top: 5px; }
    
    .main-subtitle { font-size: 16px; color: #6c757d; font-weight: 400; text-align: center; margin-bottom: 25px; }
    .section-header { font-size: 20px; font-weight: 700; color: #0056b3; margin-top: 20px; margin-bottom: 15px; }
    
    /* Clean Cards */
    .card-container, .metric-card, .workspace-section, .result-card {
        background-color: #FFFFFF;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    
    .metric-card {
        border-top: 4px solid #0056b3;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
    
    .metric-title, .small-label { font-size: 13px; color: #6c757d; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
    .metric-value, .big-result { font-size: 26px; font-weight: 700; color: #212529; margin-bottom: 0px; }
    .result-title { font-size: 16px; font-weight: 600; color: #495057; margin-bottom: 15px; }
    
    /* Medical Alert/Info Boxes */
    .disclaimer-box { background-color: #FFF3CD; border-left: 4px solid #FFC107; padding: 15px; border-radius: 6px; color: #856404; font-size: 14px; margin-bottom: 15px; }
    .briefing-box, .doctor-box { background-color: #E3F2FD; border-left: 4px solid #0D6EFD; padding: 15px; border-radius: 6px; color: #004085; font-size: 14px; margin-bottom: 15px; }
    .agent-box, .ai-box { background-color: #E2E3E5; border-left: 4px solid #383D41; padding: 15px; border-radius: 6px; color: #383D41; font-size: 14px; margin-bottom: 15px; }
    
    .status-ok { font-size: 14px; margin: 5px 0; font-weight: 600; color: #198754; }
    .warning-note { font-size: 13px; color: #856404; }
    .workspace-title { font-size: 18px; font-weight: 600; color: #212529; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; margin-bottom: 15px; }
    
    /* Sidebar / Menus */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label { padding: 10px 15px; border-radius: 6px; margin-bottom: 5px; border: 1px solid transparent; transition: 0.2s; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: #f8f9fa; border-color: #dee2e6; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] { background-color: #E3F2FD; border: 1px solid #90CAF9; color: #0056b3; font-weight: 600; }
    
    .sidebar-profile { background-color: #F8F9FA; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 20px; }
    .sidebar-profile h3 { margin: 0; font-size: 16px; color: #212529; font-weight: 600; }
    .sidebar-profile p { margin: 5px 0 0 0; font-size: 13px; color: #6c757d; }
    
    /* Inner nav styling (doctor_dashboard) */
    .inner-nav-container div[role="radiogroup"] > label > div:first-child { display: none; }
    .inner-nav-container div[role="radiogroup"] > label { padding: 10px 15px; border-radius: 6px; margin-bottom: 5px; background-color: #f8f9fa; border: 1px solid #dee2e6; cursor: pointer; }
    .inner-nav-container div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] { background-color: #D4EDDA; border-color: #198754; color: #155724; font-weight: 600; }
    
    /* Badges */
    .badge-waiting { background-color: #FFF3CD; color: #856404; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
    .badge-completed { background-color: #D4EDDA; color: #155724; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
    .badge-in-consult { background-color: #CCE5FF; color: #004085; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
</style>
            </head>
            <body>
                <div class="header">
                    <div class="header-left">
                        <h1>Apollo Hospitals, Aragonda</h1>
                        <p>India's First Modern Rural Hospital | 50-Bed Secondary Care</p>
                    </div>
                    <div class="header-right">
                        <p>Aragonda Village, Thavanampalle Mandal</p>
                        <p>Chittoor District, AP - 517129</p>
                        <p>Emergency: 1066 | Ph: 08573-283220</p>
                    </div>
                </div>
                
                <div class="patient-info">
                    <h2 style="margin-top:0; border:none; padding:0;">Patient Demographics</h2>
                    <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                        <div>
                            <p><strong>Name:</strong> {patient_profile.get('patient_name')}</p>
                            <p><strong>Patient ID:</strong> {patient_profile.get('patient_id')}</p>
                        </div>
                        <div>
                            <p><strong>Age:</strong> {patient_profile.get('age')}</p>
                            <p><strong>Gender:</strong> {patient_profile.get('gender')}</p>
                        </div>
                    </div>
                </div>
                
                <h2>Clinical Visits Summary</h2>
                {visits_html}
                
                <h2>Current Medications</h2>
                <div style="background: #fff; border: 1px solid #e9ecef; padding: 20px; border-radius: 8px;">
                    {meds_html}
                </div>
                
                <div class="footer">
                    <p>This is a computer-generated medical report provided by the Agentic AI Healthcare Assistant system.</p>
                    <p>Generated on: {now_str}</p>
                </div>
            </body>
            </html>
            '''
            
            st.download_button(
                "📄 Download Medical Report (HTML)",
                data=html_report,
                file_name=f"{selected_patient_code}_medical_report.html",
                mime="text/html",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_d2:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("### 🔗 FHIR Data")
            st.write("A structured JSON format for interoperability with other healthcare systems.")
            
            try:
                fhir_db = _load_fhir_database()
                patient_bundle = None
                for bundle in fhir_db:
                    for entry in bundle.get("entry", []):
                        resource = entry.get("resource", {})
                        if resource.get("resourceType") == "Patient" and resource.get("id") == selected_patient_code:
                            patient_bundle = bundle
                            break
                    if patient_bundle:
                        break
                        
                if patient_bundle:
                    fhir_json_str = json.dumps(patient_bundle, indent=2)
                    st.download_button(
                        "🔗 Download FHIR Data (JSON)",
                        data=fhir_json_str,
                        file_name=f"{selected_patient_code}_fhir.json",
                        mime="application/json",
                        use_container_width=True
                    )
                else:
                    st.warning("FHIR data not available in the hospital database.")
            except Exception as e:
                st.warning("Unable to load FHIR data.")
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 🏥 Hospital & AI
# ------------------------------------------------------------
elif menu == "🏥 Hospital & AI":
    st.markdown('<h2 class="section-title">🏥 Hospital & AI</h2>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🤖 AI Health Review", "🏥 Hospital Information"])
    
    with tabs[0]:
        st.markdown('<div class="disclaimer-box"><strong>IMPORTANT NOTICE:</strong> Information in this section is generated by an Artificial Intelligence decision-support system. It is strictly for informational and clinical decision-support purposes and is <strong>NOT a confirmed diagnosis</strong>. The doctor remains fully responsible for all clinical decisions and diagnoses.</div>', unsafe_allow_html=True)
        
        col_d, col_ai = st.columns(2)
        with col_d:
            st.markdown('<div class="doctor-box">', unsafe_allow_html=True)
            st.markdown("### 👨‍⚕️ Doctor's Clinical Assessment")
            if latest_visit and latest_visit.get("diagnosis") and str(latest_visit.get("diagnosis")).strip().lower() != "none":
                st.markdown(f"**{latest_visit.get('diagnosis')}**")
                st.write(f"Diagnosed by Dr. {latest_visit.get('doctors', {}).get('name', 'Unknown')} on {latest_visit.get('visit_date')}")
            else:
                st.write("No doctor-recorded diagnosis available.")
            st.markdown("<hr><small>This represents the treating doctor's recorded clinical assessment.</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_ai:
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.markdown("### 🤖 AI-Assisted Review")
            if latest_assessment:
                st.markdown(f"**Possible condition:** {latest_assessment.get('top_prediction', 'N/A')}")
                st.markdown(f"**Confidence:** {latest_assessment.get('confidence_level', 'N/A')}")
            else:
                st.write("No AI-assisted assessment is available.")
            st.markdown("<hr><small>This is an AI-generated decision-support output and is NOT a confirmed diagnosis.</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        
        st.markdown("### ⚠️ Risk Information")
        if risk_flags:
            st.warning("Your recent assessment contained information that your doctor may wish to review.")
        else:
            st.success("No stored risk concerns from the assessment.")
            
        st.markdown("### 💊 Medication Safety")
        if med_alerts:
            st.warning("Medication safety information is available from your recent assessment. Please discuss medication questions with your doctor.")
        else:
            st.success("No medication interaction alerts detected in the current records.")

    with tabs[1]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            ### Apollo Hospitals, Aragonda
            
            **Hospital Type:**  
            Secondary Care Hospital
            
            **Beds:**  
            50
            
            **Services:**  
            - Emergency: 24×7
            - Telemedicine: Available
            
            **Address:**  
            Chittoor Aragonda Rd,  
            Aragonda,  
            Andhra Pradesh 517129
            ''')
        
        with col2:
            st.markdown("### Associated Doctors")
            doctors = set()
            for v in doctor_visits:
                if v.get("doctors", {}).get("name") and str(v.get("doctors", {}).get("name")).strip().lower() != "none":
                    doctors.add(v.get("doctors", {}).get("name"))
            for m in doctor_medications:
                if m.get("doctor_name") and str(m.get("doctor_name")).strip().lower() != "none":
                    doctors.add(m.get("doctor_name"))
                    
            if not doctors:
                st.info("No doctors are currently associated with your records.")
            else:
                for d in doctors:
                    st.markdown(f'<div class="card-container"><strong>Dr. {d}</strong><br><small>Treating Physician</small></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 👤 My Profile
# ------------------------------------------------------------
elif menu == "👤 My Profile":
    st.markdown('<h2 class="section-title">👤 My Profile</h2>', unsafe_allow_html=True)
    
    # Custom CSS for Profile Page
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    .stApp { background-color: #F8F9FA; }
    
    /* Clean headers */
    .patient-header, .main-title, .section-title {
        color: #0056b3 !important;
        border-bottom: 2px solid #E3F2FD;
        padding-bottom: 10px;
        margin-bottom: 25px;
        font-weight: 700;
    }
    
    .patient-header {
        background-color: #FFFFFF;
        padding: 25px 30px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        border-left: 6px solid #0056b3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .patient-header h1 { font-size: 32px; margin: 0; font-weight: 800; color: #212529; border: none; }
    .patient-header p { font-size: 15px; color: #6c757d; margin-top: 5px; }
    
    .main-subtitle { font-size: 16px; color: #6c757d; font-weight: 400; text-align: center; margin-bottom: 25px; }
    .section-header { font-size: 20px; font-weight: 700; color: #0056b3; margin-top: 20px; margin-bottom: 15px; }
    
    /* Clean Cards */
    .card-container, .metric-card, .workspace-section, .result-card {
        background-color: #FFFFFF;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    
    .metric-card {
        border-top: 4px solid #0056b3;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
    
    .metric-title, .small-label { font-size: 13px; color: #6c757d; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
    .metric-value, .big-result { font-size: 26px; font-weight: 700; color: #212529; margin-bottom: 0px; }
    .result-title { font-size: 16px; font-weight: 600; color: #495057; margin-bottom: 15px; }
    
    /* Medical Alert/Info Boxes */
    .disclaimer-box { background-color: #FFF3CD; border-left: 4px solid #FFC107; padding: 15px; border-radius: 6px; color: #856404; font-size: 14px; margin-bottom: 15px; }
    .briefing-box, .doctor-box { background-color: #E3F2FD; border-left: 4px solid #0D6EFD; padding: 15px; border-radius: 6px; color: #004085; font-size: 14px; margin-bottom: 15px; }
    .agent-box, .ai-box { background-color: #E2E3E5; border-left: 4px solid #383D41; padding: 15px; border-radius: 6px; color: #383D41; font-size: 14px; margin-bottom: 15px; }
    
    .status-ok { font-size: 14px; margin: 5px 0; font-weight: 600; color: #198754; }
    .warning-note { font-size: 13px; color: #856404; }
    .workspace-title { font-size: 18px; font-weight: 600; color: #212529; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; margin-bottom: 15px; }
    
    /* Sidebar / Menus */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label { padding: 10px 15px; border-radius: 6px; margin-bottom: 5px; border: 1px solid transparent; transition: 0.2s; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: #f8f9fa; border-color: #dee2e6; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] { background-color: #E3F2FD; border: 1px solid #90CAF9; color: #0056b3; font-weight: 600; }
    
    .sidebar-profile { background-color: #F8F9FA; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 20px; }
    .sidebar-profile h3 { margin: 0; font-size: 16px; color: #212529; font-weight: 600; }
    .sidebar-profile p { margin: 5px 0 0 0; font-size: 13px; color: #6c757d; }
    
    /* Inner nav styling (doctor_dashboard) */
    .inner-nav-container div[role="radiogroup"] > label > div:first-child { display: none; }
    .inner-nav-container div[role="radiogroup"] > label { padding: 10px 15px; border-radius: 6px; margin-bottom: 5px; background-color: #f8f9fa; border: 1px solid #dee2e6; cursor: pointer; }
    .inner-nav-container div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] { background-color: #D4EDDA; border-color: #198754; color: #155724; font-weight: 600; }
    
    /* Badges */
    .badge-waiting { background-color: #FFF3CD; color: #856404; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
    .badge-completed { background-color: #D4EDDA; color: #155724; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
    .badge-in-consult { background-color: #CCE5FF; color: #004085; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
</style>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar">👤</div>
        <div class="profile-info">
            <h3>{patient_profile.get('patient_name')}</h3>
            <p>Patient ID: {patient_profile.get('patient_id')} | {str(patient_profile.get('gender', '')).title()}, {patient_profile.get('age')} yrs</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    profile_tabs = st.tabs(["📋 Personal Info", "🏥 Essential Needs"])
    
    with profile_tabs[0]:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Full Name:** {patient_profile.get('patient_name')}")
            st.markdown(f"**Patient ID:** {patient_profile.get('patient_id')}")
            st.markdown(f"**Gender:** {str(patient_profile.get('gender', '')).title()}")
            st.markdown(f"**Age:** {patient_profile.get('age')} years")
        with col2:
            st.markdown("**Phone:** +91-XXXXXXXXXX")
            st.markdown("**Email:** patient@example.com")
            st.markdown("**Address:** Aragonda Village, AP")
            st.markdown("**Registered On:** 2024-01-15")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("This page is read-only. To update your demographic information, please contact the hospital administration desk.")
    
    with profile_tabs[1]:
        st.markdown("### Emergency & Critical Info")
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            st.markdown("""
            <div class="essential-card">
                <h4>🩸 Blood Group</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0;">O Positive (O+)</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="essential-card" style="border-left-color: #ff4b4b;">
                <h4>⚠️ Known Allergies</h4>
                <p style="margin: 5px 0;">Penicillin, Peanuts</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_e2:
            st.markdown("""
            <div class="essential-card" style="border-left-color: #ffb703;">
                <h4>📞 Emergency Contact</h4>
                <p style="margin: 5px 0;"><strong>Name:</strong> Ravi Sharma (Spouse)<br><strong>Phone:</strong> +91-9876543210</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="essential-card" style="border-left-color: #2a9d8f;">
                <h4>🛡️ Insurance Information</h4>
                <p style="margin: 5px 0;"><strong>Provider:</strong> Star Health<br><strong>Policy No:</strong> P-123456789</p>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Made logout button full width and distinct
    col_btn, _, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("🚪 Logout", type="primary", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user_role"] = None
            st.query_params.clear()
            if "pat_menu_selection" in st.session_state:
                del st.session_state["pat_menu_selection"]
            st.rerun()

# ------------------------------------------------------------
# ⚙️ Settings
# ------------------------------------------------------------
elif menu == "⚙️ Settings":
    st.markdown('<h2 class="section-title">⚙️ App Settings</h2>', unsafe_allow_html=True)
    
    st.markdown("### App Preferences")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    st.toggle("📧 Receive Email Notifications for Appointments", value=True)
    st.toggle("📱 Receive SMS Alerts for Medication Reminders", value=True)
    st.toggle("🤖 Enable AI Health Tips", value=True)
    
    st.markdown("---")
    st.selectbox("Language Preference", ["English", "Telugu (తెలుగు)", "Hindi (हिंदी)"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Account Security")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.button("Update Password")
    st.button("Manage Devices")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Made logout button full width and distinct
    col_btn, _, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("🚪 Logout", type="primary", use_container_width=True, key="logout_settings"):
            st.session_state["authenticated"] = False
            st.session_state["user_role"] = None
            st.query_params.clear()
            if "pat_menu_selection" in st.session_state:
                del st.session_state["pat_menu_selection"]
            st.rerun()
