import streamlit as st
import pandas as pd
import json

from src.services.supabase_client import (
    get_patient_profile,
    get_patient_observations,
    get_patient_risk_flags,
    get_patient_medication_alerts,
    get_assessment_history_by_uuid,
    supabase
)

from src.fhir.parser import _load_fhir_database

# ============================================================
# PAGE CONFIG
# ============================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="Patient Dashboard - Apollo Hospitals",
        page_icon="👤",
        layout="wide"
    )

# ============================================================
# CUSTOM CSS FOR PROFESSIONAL HEALTHCARE PORTAL
# ============================================================
st.markdown("""
<style>
    /* Premium, Theme-Aware Medical Portal UI */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .patient-header {
        background: linear-gradient(135deg, rgba(0, 86, 179, 0.7) 0%, rgba(0, 168, 232, 0.7) 100%);
        padding: 40px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 30px;
        color: white;
    }
    .patient-header h1 {
        margin: 0;
        font-size: 36px;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
    }
    .patient-header p {
        margin: 10px 0 0 0;
        font-size: 16px;
        opacity: 0.95;
        font-family: 'Inter', sans-serif;
    }
    
    .card-container {
        background-color: var(--secondary-background-color);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 25px;
        border: 1px solid rgba(128,128,128,0.2);
    }
    
    .metric-card {
        text-align: center;
        padding: 25px 20px;
        background-color: var(--secondary-background-color);
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,0.2);
        border-top: 4px solid var(--primary-color, #00a8e8);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .metric-title {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    .metric-value {
        color: var(--text-color);
        font-size: 28px;
        font-weight: 800;
    }
    
    .disclaimer-box {
        background-color: rgba(255, 193, 7, 0.15);
        color: var(--text-color);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #ffc107;
        margin: 20px 0;
    }
    
    .doctor-box {
        background-color: rgba(0, 188, 212, 0.15);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #00bcd4;
        margin-bottom: 20px;
        color: var(--text-color);
    }
    
    .ai-box {
        background: linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(103, 58, 183, 0.1) 100%);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #9c27b0;
        margin-bottom: 20px;
        color: var(--text-color);
    }
    
    .section-title {
        color: var(--text-color);
        border-bottom: 2px solid rgba(128,128,128,0.2);
        padding-bottom: 15px;
        margin-bottom: 30px;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
        font-size: 24px;
    }
    
    /* Sidebar styling for a professional menu */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        background-color: transparent;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(128,128,128,0.1);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"][aria-checked="true"] {
        background-color: rgba(0, 123, 255, 0.15);
        border-left: 4px solid #007bff;
        border-radius: 0 8px 8px 0;
    }
    .sidebar-profile {
        background-color: rgba(128,128,128,0.1);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        border: 1px solid rgba(128,128,128,0.2);
    }
    .sidebar-profile h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 700;
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }
    .sidebar-profile p {
        margin: 5px 0 0 0;
        font-size: 14px;
        opacity: 0.8;
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }

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
    
    col1, col2, col3, col4 = st.columns(4)
    
    current_care = latest_visit.get("diagnosis") if latest_visit and latest_visit.get("diagnosis") else "No active diagnosis"
    last_visit_date = latest_visit.get("visit_date") if latest_visit else "No recent visits"
    
    follow_up = latest_visit.get("follow_up_date") if latest_visit else None
    if not follow_up or str(follow_up).strip().lower() == "none":
        follow_up_display = "No follow-up"
    else:
        follow_up_display = str(follow_up)
        
    med_count = str(len(doctor_medications))
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Current Care Status</div><div class="metric-value">{current_care}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Last Doctor Visit</div><div class="metric-value">{last_visit_date}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Next Follow-up</div><div class="metric-value" style="font-size: 18px;">{follow_up_display}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Current Medicines</div><div class="metric-value">{med_count}</div></div>', unsafe_allow_html=True)

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
                    body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 40px; color: #333; line-height: 1.6; }}
                    .header {{ border-bottom: 4px solid #0056b3; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }}
                    .header-left h1 {{ margin: 0; color: #0056b3; font-size: 32px; font-weight: 800; }}
                    .header-left p {{ margin: 5px 0 0 0; color: #666; font-size: 14px; }}
                    .header-right {{ text-align: right; color: #666; font-size: 13px; }}
                    h2 {{ color: #0056b3; font-size: 22px; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px; margin-top: 40px; }}
                    .patient-info {{ background: #f8f9fa; padding: 25px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #e9ecef; }}
                    .patient-info p {{ margin: 8px 0; font-size: 15px; }}
                    .visit-block {{ background: #fff; border: 1px solid #e9ecef; border-left: 5px solid #17a2b8; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }}
                    .visit-block h4 {{ margin-top: 0; color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }}
                    .visit-block p {{ margin: 8px 0; }}
                    .footer {{ margin-top: 60px; font-size: 13px; color: #999; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
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
    .profile-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
    }
    .profile-avatar {
        background: linear-gradient(135deg, #007bb5, #00bcd4);
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        color: white;
        box-shadow: 0 10px 20px rgba(0, 188, 212, 0.3);
    }
    .profile-info h3 {
        margin: 0 0 5px 0;
        font-size: 28px;
        font-weight: 800;
        color: var(--text-color);
    }
    .profile-info p {
        margin: 0;
        opacity: 0.8;
        font-size: 16px;
    }
    .essential-card {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 4px solid #00bcd4;
    }
    .essential-card h4 {
        margin-top: 0;
        color: #00bcd4;
        font-size: 16px;
    }
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
            st.session_state["patient_id"] = None
            st.session_state["patient_uuid"] = None
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
        if st.button("🚪 Logout", type="primary", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user_role"] = None
            st.session_state["patient_id"] = None
            st.session_state["patient_uuid"] = None
            if "pat_menu_selection" in st.session_state:
                del st.session_state["pat_menu_selection"]
            st.query_params.clear()
            st.rerun()
