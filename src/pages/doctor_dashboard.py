import streamlit as st
import pandas as pd
from datetime import date
import json
import sys

MENU_DASHBOARD = "🏠 Dashboard"
MENU_TODAY_PATIENTS = "👥 Today's Patients"
MENU_DR_PROFILE = "👨‍⚕️ Dr. Profile"
STATUS_IN_CONSULTATION = "IN CONSULTATION"


if "supabase_client" in sys.modules:
    del sys.modules["supabase_client"]

from src.services.supabase_client import (
    get_supabase_client,
    get_patients as supabase_get_patients,
    get_patient_profile as supabase_get_patient_profile,
    get_patient_risk_flags,
    get_patient_medication_alerts,
    get_patient_doctor_briefings,
    get_assessment_history_by_uuid,
    get_today_encounters,
    update_hospital_encounter_status,
)

from src.services.hospital_client import get_hospital
from src.agents.hospital_routing_agent import format_routing_result
from src.fhir.parser import _load_fhir_database

# ============================================================
# PAGE CONFIG
# ============================================================
if __name__ == "__main__":
    st.set_page_config(page_title="Doctor Dashboard", page_icon="👨‍⚕️", layout="wide", initial_sidebar_state="expanded")

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
# CHECK AUTHENTICATION
# ============================================================
if not st.session_state.get("authenticated") or st.session_state.get("user_role") != "doctor":
    st.error("Unauthorized. Please login from the main page.")
    st.stop()

doctor_name = "Dr V Sukaveni"
doctor_speciality = "Internal Medicine"

d_res = get_supabase_client().table("doctors").select("id").eq("name", doctor_name).execute()
doctor_uuid = d_res.data[0]["id"] if d_res.data else None

# ============================================================
# INITIALIZE STATE
# ============================================================
if "doctor_selected_patient_code" not in st.session_state:
    st.session_state["doctor_selected_patient_code"] = None
if "doctor_selected_patient_uuid" not in st.session_state:
    st.session_state["doctor_selected_patient_uuid"] = None
if "doctor_selected_encounter_id" not in st.session_state:
    st.session_state["doctor_selected_encounter_id"] = None
if "visit_saved_today" not in st.session_state:
    st.session_state["visit_saved_today"] = False

# ============================================================
# DATA HELPERS
# ============================================================
today_str = date.today().isoformat()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown(f'''
<div class="sidebar-profile">
    <h3 style="color: #f8fafc; font-size: 20px; font-weight: 700; margin-bottom: 4px;">👨‍⚕️ {doctor_name}</h3>
    <p style="color: #38bdf8; font-weight: 600; font-size: 14px; margin-top: 0; margin-bottom: 4px;">{doctor_speciality}</p>
    <p style="color: #64748b; font-size: 12px; margin-top: 0;">Apollo Hospitals, Aragonda</p>
</div>
<hr style="border-color: #1e293b; margin-top: 15px; margin-bottom: 20px;">
''', unsafe_allow_html=True)

if "doc_menu_selection" not in st.session_state:
    st.session_state["doc_menu_selection"] = MENU_DASHBOARD

st.sidebar.markdown(f'<p style="color: #64748b; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; padding-left: 16px; margin-bottom: 8px;">Navigation</p>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    options=[MENU_DASHBOARD, MENU_TODAY_PATIENTS, MENU_DR_PROFILE],
    index=[MENU_DASHBOARD, MENU_TODAY_PATIENTS, MENU_DR_PROFILE].index(st.session_state["doc_menu_selection"]),
    label_visibility="collapsed"
)

if menu != st.session_state["doc_menu_selection"]:
    st.session_state["doc_menu_selection"] = menu
    st.rerun()

if menu == MENU_DR_PROFILE:
    st.markdown('<h2 class="section-title">👨‍⚕️ Doctor Profile</h2>', unsafe_allow_html=True)
    st.write(f"**Name:** {doctor_name}")
    st.write(f"**Speciality:** {doctor_speciality}")
    st.write("**Hospital:** Apollo Hospitals, Aragonda")
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        js_code = """
        <script>
        document.cookie = "auth_role=; path=/; max-age=0";
        document.cookie = "auth_username=; path=/; max-age=0";
        document.cookie = "auth_patient_id=; path=/; max-age=0";
        document.cookie = "auth_patient_uuid=; path=/; max-age=0";
        window.parent.location.reload();
        </script>
        """
        import streamlit.components.v1 as components
        components.html(js_code, height=0)
        st.stop()

# ============================================================
# MAIN CONTENT
# ============================================================
# If a patient is selected, DO NOT show the main global header to keep it clean.
if not st.session_state.get("doctor_selected_patient_code") and menu != MENU_DR_PROFILE:
    st.markdown(f"""
    <div class="patient-header">
        <h1>👨‍⚕️ Doctor Dashboard</h1>
        <p>Clinical workspace — {doctor_name} | Apollo Hospitals, Aragonda</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# 🏠 DASHBOARD
# ------------------------------------------------------------
if menu == MENU_DASHBOARD:
    st.markdown('<h2 class="section-title">📊 Today\'s Overview</h2>', unsafe_allow_html=True)
    try:
        tp = get_today_encounters(today_str)
    except Exception:
        tp = []
    total_tp = len(tp)
    completed = len([e for e in tp if e.get("status") == "COMPLETED"])
    waiting = len([e for e in tp if e.get("status") in ["WAITING", STATUS_IN_CONSULTATION]])
    
    visits_res = get_supabase_client().table("doctor_visits").select("follow_up_date").execute()
    all_fups = [v.get("follow_up_date") for v in (visits_res.data or []) if v.get("follow_up_date") and v.get("follow_up_date") > today_str]
    fups_count = len(all_fups)
    
    dashboard_html = f"""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px;">
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Today's Encounters</div>
        <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1;">{total_tp}</div>
    </div>
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Completed Visits</div>
        <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1;">{completed}</div>
    </div>
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Waiting</div>
        <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1; color: #f59e0b;">{waiting}</div>
    </div>
    <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Upcoming Follow-ups</div>
        <div style="color: #0f172a; font-size: 36px; font-weight: 800; line-height: 1; color: #0ea5e9;">{fups_count}</div>
    </div>
</div>
"""
    st.markdown(dashboard_html, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.info("Select '👥 Today's Patients' from the sidebar to begin consultations.")

# ------------------------------------------------------------
# 👥 TODAY'S PATIENTS
# ------------------------------------------------------------
elif menu == MENU_TODAY_PATIENTS and not st.session_state.get("doctor_selected_patient_code"):
    st.markdown('<h2 class="section-title">👥 Today\'s Patients <span style="font-size: 14px; font-weight: normal; color: green; float: right; margin-top: 10px;">🟢 Live Updates Active</span></h2>', unsafe_allow_html=True)
    
    @st.fragment(run_every="10s")
    def live_patient_queue():
        try:
            # We explicitly clear the cache for this specific call so it gets fresh data
            import src.services.supabase_client as sc
            if hasattr(sc.get_today_encounters, "clear"):
                sc.get_today_encounters.clear()
            tp = sc.get_today_encounters(today_str)
        except Exception as e:
            st.error(f"Error fetching encounters: {e}")
            tp = []
            
        if not tp:
            st.info("No patients are waiting for consultation today.")
        else:
            tp = sorted(tp, key=lambda x: (x.get("status") == "COMPLETED", x.get("created_at") or ""))
            for e in tp:
                patient_data = e.get("patients")
                if not patient_data: continue
                    
                st.markdown('<div class="card-container" style="padding: 15px;">', unsafe_allow_html=True)
                cols = st.columns([1, 2, 2, 2, 2, 2])
                
                p_code = patient_data.get("patient_id")
                cols[0].markdown(f"**{p_code}**")
                cols[1].markdown(f"{patient_data.get('name')}")
                cols[2].markdown(f"{patient_data.get('age')} years • {patient_data.get('gender')}")
                cols[3].markdown(f"{e.get('department') or 'Unspecified'}")
                
                status = e.get("status", "WAITING")
                if status == "COMPLETED": badge = '<span class="badge-completed">🟢 Completed</span>'
                elif status == STATUS_IN_CONSULTATION: badge = '<span class="badge-in-consult">🔵 In Consultation</span>'
                else: badge = '<span class="badge-waiting">🟡 Waiting</span>'
                cols[4].markdown(badge, unsafe_allow_html=True)
                
                with cols[5]:
                    if st.button("Review Patient", key=f"btn_{e['id']}"):
                        st.session_state["doctor_selected_patient_code"] = p_code
                        st.session_state["doctor_selected_patient_uuid"] = e.get("patient_id")
                        st.session_state["doctor_selected_encounter_id"] = e.get("id")
                        st.session_state["visit_saved_today"] = (status == "COMPLETED")
                        st.session_state["inner_nav_selection"] = "👤 Patient Profile"
                        
                        if status == "WAITING":
                            update_hospital_encounter_status(e.get("id"), STATUS_IN_CONSULTATION)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    live_patient_queue()



# ============================================================
# 👤 COMPLETE PATIENT REVIEW (WORKSPACE)
# ============================================================
if menu == MENU_TODAY_PATIENTS and st.session_state.get("doctor_selected_patient_code"):
    selected_code = st.session_state.get("doctor_selected_patient_code")
    selected_uuid = st.session_state.get("doctor_selected_patient_uuid")
    encounter_id = st.session_state.get("doctor_selected_encounter_id")
    
    try:
        p_data = supabase_get_patient_profile(selected_code)
    except Exception:
        p_data = None
        
    if not p_data:
        st.error("Unable to load patient information.")
        st.stop()
        
    # --------------------------------------------------------
    # CONCURRENT DATA FETCHING FOR DOCTOR WORKSPACE
    # --------------------------------------------------------
    import concurrent.futures

    def fetch_visits():
        return get_supabase_client().table("doctor_visits").select("*, doctors(name)").eq("patient_id", selected_uuid).order("visit_date", desc=True).execute()

    def fetch_meds():
        return get_supabase_client().table("doctor_medications").select("*").eq("patient_id", selected_uuid).execute()
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        f_visits = executor.submit(fetch_visits)
        f_meds = executor.submit(fetch_meds)
        f_ai = executor.submit(get_assessment_history_by_uuid, selected_uuid)
        f_risks = executor.submit(get_patient_risk_flags, selected_uuid)
        f_alerts = executor.submit(get_patient_medication_alerts, selected_uuid)
        f_briefs = executor.submit(get_patient_doctor_briefings, selected_uuid)
        
        v_res = f_visits.result()
        m_res = f_meds.result()
        ai_hist = f_ai.result()
        risks = f_risks.result()
        med_alerts = f_alerts.result()
        briefings = f_briefs.result()

    p_visits = v_res.data if v_res.data else []
    past_visits = [v for v in p_visits if v.get("visit_date") != today_str]
    today_visit_record = next((v for v in p_visits if v.get("visit_date") == today_str), None)
    
    p_meds = m_res.data if m_res.data else []
    
    latest_ai = ai_hist[0] if ai_hist else None
    latest_briefing = briefings[0] if briefings else None

    # Workspace Header
    col_back, _ = st.columns([1, 5])
    with col_back:
        if st.button("← Back to Today's Patients"):
            st.session_state["doctor_selected_patient_code"] = None
            st.session_state["doctor_selected_patient_uuid"] = None
            st.session_state["doctor_selected_encounter_id"] = None
            st.session_state["visit_saved_today"] = False
            if "inner_nav_selection" in st.session_state:
                del st.session_state["inner_nav_selection"]
            st.rerun()

    st.markdown(f'''
    <div class="patient-header" style="border-left: 5px solid #007bff;">
        <h2 style="margin: 0; font-size: 28px; font-weight: 800;">👤 {p_data.get('patient_name')}</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 16px;">
            {p_data.get('patient_id')} • {p_data.get('age')} Years • {str(p_data.get('gender')).title()}
        </p>
    </div>
    ''', unsafe_allow_html=True)

    tabs = st.tabs([
        "👤 Patient Profile",
        "📋 Doctor Briefing",
        "🏥 Hospital Routing",
        "📅 Previous Visits",
        "🩺 Today's Visit",
        "📄 Saved Visit Report"
    ])
    
    with tabs[0]:
        st.markdown(f"""
        <div style='background: linear-gradient(145deg, rgba(128, 128, 128, 0.05) 0%, rgba(128, 128, 128, 0.02) 100%); backdrop-filter: blur(10px); padding: 30px; border-radius: 16px; border: 1px solid rgba(128,128,128,0.1); box-shadow: 0 4px 15px rgba(0,0,0,0.02); margin-bottom: 20px;'>
            <h4 style='margin-top: 0; color: var(--text-color); border-bottom: 2px solid rgba(128,128,128,0.1); font-weight: 600; padding-bottom: 10px; margin-bottom: 15px;'>Patient Demographics</h4>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 15px;'>
                <div><span style='opacity: 0.7;'>Patient ID:</span> <br><strong>{p_data.get('patient_id')}</strong></div>
                <div><span style='opacity: 0.7;'>Patient Name:</span> <br><strong>{p_data.get('patient_name')}</strong></div>
                <div><span style='opacity: 0.7;'>Age:</span> <br><strong>{p_data.get('age')} Years</strong></div>
                <div><span style='opacity: 0.7;'>Gender:</span> <br><strong>{str(p_data.get('gender')).capitalize()}</strong></div>
                <div><span style='opacity: 0.7;'>Date of Birth:</span> <br><strong>{p_data.get('date_of_birth', 'N/A')}</strong></div>
                <div><span style='opacity: 0.7;'>Hospital:</span> <br><strong>Apollo Hospitals, Aragonda</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        last_visit_date = past_visits[0].get('visit_date') if past_visits else 'None'
        last_visit_diag = past_visits[0].get('diagnosis') if past_visits else 'No doctor-recorded diagnosis available.'
        active_meds = p_data.get("medications", [])
        meds_str = ', '.join(active_meds) if active_meds else 'None'
        status_str = '🟢 COMPLETED' if st.session_state.get('visit_saved_today') else '🟡 WAITING / IN CONSULTATION'
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(0,123,255,0.08) 0%, rgba(0,86,179,0.04) 100%); backdrop-filter: blur(10px); padding: 30px; border-radius: 16px; border: 1px solid rgba(0,123,255,0.2); box-shadow: 0 4px 15px rgba(0,123,255,0.05);'>
            <h4 style='margin-top: 0; color: var(--text-color); border-bottom: 1px solid rgba(0,123,255,0.2); padding-bottom: 10px; margin-bottom: 15px;'>Clinical Summary</h4>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 15px;'>
                <div><span style='opacity: 0.7;'>Latest Visit Date:</span> <br><strong>{last_visit_date}</strong></div>
                <div><span style='opacity: 0.7;'>Current Visit Status:</span> <br><strong>{status_str}</strong></div>
                <div style='grid-column: span 2;'><span style='opacity: 0.7;'>Doctor-recorded Diagnosis:</span> <br><strong>{last_visit_diag}</strong></div>
                <div style='grid-column: span 2;'><span style='opacity: 0.7;'>Current Medications:</span> <br><strong>{meds_str}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------

    # 5. DOCTOR BRIEFING
    # --------------------------------------------------------
    with tabs[1]:
        if latest_briefing:
            st.write(latest_briefing.get("summary"))
        else:
            st.info("No briefing available for this patient.")



    # --------------------------------------------------------
    # 7. HOSPITAL ROUTING
    # --------------------------------------------------------
    with tabs[2]:
        st.markdown('**Apollo Hospitals, Aragonda**')
        st.write("**Suggested Speciality:** Appropriate Department Based on Symptoms")
        st.write("**Relevant Doctor:** Recommended available specialist")
        st.caption("Hospital routing is decision support based on reported symptoms and available hospital data. Final clinical decisions remain with the treating doctor.")

    # --------------------------------------------------------
    # 8. PREVIOUS VISITS
    # --------------------------------------------------------
    with tabs[3]:
        if not past_visits:
            st.info("No previous visits found for this patient.")
        else:
            for v in past_visits:
                with st.expander(f"{v.get('visit_date')} - Dr. {v.get('doctors', {}).get('name', 'Unknown')}"):
                    st.write(f"**Diagnosis:** {v.get('diagnosis')}")
                    st.write(f"**Doctor Notes:** {v.get('doctor_notes')}")
                    st.write(f"**Future Plan:** {v.get('future_plan')}")
                    st.write(f"**Follow-up Date:** {v.get('follow_up_date', 'None')}")
                    
                    visit_meds = [m for m in p_meds if m.get("visit_id") == v.get("id")]
                    if visit_meds:
                        st.write("**Prescribed Medicines:**")
                        for m in visit_meds:
                            st.write(f"- {m.get('medication_name')} ({m.get('dosage')}, {m.get('frequency')}) for {m.get('duration')} | {m.get('instructions')}")

    # --------------------------------------------------------
    # 9. TODAY'S VISIT
    # --------------------------------------------------------
    with tabs[4]:
        # READ-ONLY CONTEXT SUMMARY
        st.markdown('<div style="background-color: rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; padding: 15px; margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown("#### Patient Context (Read-Only)")
        ct_col1, ct_col2 = st.columns(2)
        with ct_col1:
            st.write(f"**Latest Symptoms:** {', '.join([s.replace('_', ' ').title() for s in p_data.get('symptoms', [])])}")
            vitals = p_data.get("vitals", {})
            st.write(f"**Latest Vitals:** HR: {vitals.get('heart_rate','-')}, SpO2: {vitals.get('spo2','-')}")
            st.write(f"**Current Medications:** {', '.join(p_data.get('medications', []))}")
        with ct_col2:
            st.write(f"**AI Assessment:** {latest_ai.get('top_prediction') if latest_ai else 'None'}")
            st.write(f"**AI Confidence:** {latest_ai.get('confidence_level') if latest_ai else 'None'}")
            past_v = past_visits[0] if past_visits else None
            st.write(f"**Previous Diagnosis:** {past_v.get('diagnosis') if past_v else 'None'}")
            st.write(f"**Last Visit:** {past_v.get('visit_date') if past_v else 'None'}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.get("visit_saved_today") or today_visit_record:
            st.success("✅ Visit report saved successfully. Please navigate to '📄 Saved Visit Report' to view.")
        else:
            st.write(f"**Patient:** {p_data.get('patient_name')} ({p_data.get('patient_id')}) | **Age:** {p_data.get('age')} | **Gender:** {p_data.get('gender')}")
            st.write(f"**Visit Date:** {today_str} | **Doctor:** {doctor_name}")
            
            @st.fragment
            def render_visit_form():
                with st.form("todays_visit_form"):
                    st.markdown("#### Doctor's Final Clinical Input")
                    diagnosis = st.text_input("Diagnosis / Clinical Assessment", placeholder="e.g., Acute Bronchitis")
                    notes = st.text_area("Doctor Notes", placeholder="Clinical observations...")
                    
                    st.markdown("#### Prescribed Medicines")
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        med_name = st.text_input("Medication Name")
                        med_dosage = st.text_input("Dosage")
                        med_freq = st.text_input("Frequency")
                    with col_m2:
                        med_dur = st.text_input("Duration")
                        med_inst = st.text_area("Instructions", height=130)
                        
                    st.markdown("#### Plan & Follow-up")
                    future_plan = st.text_area("Future Care Plan")
                    req_fup = st.radio("Follow-up Required?", ["No", "Yes"], horizontal=True)
                    follow_up_date = None
                    if req_fup == "Yes":
                        follow_up_date = st.date_input("Follow-up Date")
                        
                    submitted = st.form_submit_button("💾 Save Visit Report")
                    
                    if submitted:
                        if not diagnosis.strip():
                            st.error("Diagnosis or clinical assessment is required.")
                        elif req_fup == "Yes" and not follow_up_date:
                            st.error("Please provide a valid follow-up date.")
                        elif med_name and (not med_dosage or not med_freq):
                            st.error("Incomplete medication record. Please provide dosage and frequency.")
                        else:
                            try:
                                v_data = {
                                    "patient_id": selected_uuid,
                                    "doctor_id": doctor_uuid,
                                    "visit_date": today_str,
                                    "diagnosis": diagnosis,
                                    "doctor_notes": notes,
                                    "future_plan": future_plan,
                                    "follow_up_date": str(follow_up_date) if req_fup == "Yes" else None
                                }
                                v_res = get_supabase_client().table("doctor_visits").insert(v_data).execute()
                                
                                if v_res.data:
                                    visit_id = v_res.data[0]["id"]
                                    if med_name:
                                        m_data = {
                                            "visit_id": visit_id,
                                            "patient_id": selected_uuid,
                                            "medication_name": med_name,
                                            "dosage": med_dosage,
                                            "frequency": med_freq,
                                            "duration": med_dur,
                                            "instructions": med_inst
                                        }
                                        get_supabase_client().table("doctor_medications").insert(m_data).execute()
                                    
                                    if encounter_id:
                                        update_hospital_encounter_status(encounter_id, "COMPLETED")
                                        
                                    st.session_state["visit_saved_today"] = True
                                    st.rerun()
                                else:
                                    st.error("Failed to save visit.")
                            except Exception as e:
                                st.error(f"Error saving visit: {e}")

            render_visit_form()

    # --------------------------------------------------------
    # 10. SAVED VISIT REPORT
    # --------------------------------------------------------
    with tabs[5]:
        if not st.session_state.get("visit_saved_today") and not today_visit_record:
            st.info("No visit report has been saved for today yet.")
        else:
            if not today_visit_record:
                 v_res = get_supabase_client().table("doctor_visits").select("*, doctors(name)").eq("patient_id", selected_uuid).eq("visit_date", today_str).limit(1).execute()
                 today_visit_record = v_res.data[0] if v_res.data else {}
                 
            st.write(f"**Patient:** {p_data.get('patient_name')} | **Doctor:** {today_visit_record.get('doctors', {}).get('name', 'Unknown')} | **Visit Date:** {today_visit_record.get('visit_date')}")
            st.markdown("### Diagnosis / Clinical Assessment")
            st.write(today_visit_record.get('diagnosis'))
            st.markdown("### Doctor Notes")
            st.write(today_visit_record.get('doctor_notes'))
            
            today_meds = [m for m in p_meds if m.get("visit_id") == today_visit_record.get("id")]
            if today_meds:
                st.markdown("### Prescribed Medicines")
                for m in today_meds:
                    st.write(f"- **{m.get('medication_name')}**: {m.get('dosage')}, {m.get('frequency')} for {m.get('duration')}")
                    st.write(f"  *Instructions: {m.get('instructions')}*")
            
            st.markdown("### Future Care Plan")
            st.write(today_visit_record.get('future_plan'))
            
            req_fup = "Yes" if today_visit_record.get('follow_up_date') else "No"
            st.write(f"**Follow-up Required:** {req_fup}")
            if req_fup == "Yes":
                st.write(f"**Follow-up Date:** {today_visit_record.get('follow_up_date')}")
