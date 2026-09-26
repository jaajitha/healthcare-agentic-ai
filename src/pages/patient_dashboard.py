import streamlit as st
import pandas as pd
import json
import datetime
from src.services.supabase_client import (
    get_supabase_client,
    get_patient_profile,
    get_assessment_history_by_uuid,
    get_patient_risk_flags,
    get_patient_medication_alerts,
    get_patient_visits,
    get_patient_medications
)
from src.fhir.parser import _load_fhir_database

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

import concurrent.futures

# ============================================================
# LOAD PATIENT DATA (CONCURRENTLY)
# ============================================================
with st.spinner("Loading health records..."):
    
    # Pre-initialize the Supabase client outside of any @st.cache_data functions!
    # This prevents the CookieController widget from executing inside a cached function
    # which causes the 'CachedWidgetWarning' and unexpected behavior.
    get_supabase_client()
    
    try:
        patient_profile = get_patient_profile(selected_patient_code)
    except Exception as e:
        st.error(f"Unable to load your medical information. Error: {str(e)}")
        st.stop()
        
    if not patient_profile:
        st.error("Unable to load your medical information. Please try again or contact the hospital.")
        st.stop()
        
    visits_response = get_patient_visits(selected_patient_uuid)
    medications_response = get_patient_medications(selected_patient_uuid)
    ai_assessments = get_assessment_history_by_uuid(selected_patient_uuid)
    risk_flags = get_patient_risk_flags(selected_patient_uuid)
    med_alerts = get_patient_medication_alerts(selected_patient_uuid)

    # Process results
    doctor_visits = visits_response if visits_response else []
    latest_visit = doctor_visits[0] if doctor_visits else None
    doctor_medications = medications_response if medications_response else []
    latest_assessment = ai_assessments[0] if ai_assessments else None

# ============================================================
# UI STYLING (Minimal adjustments for Streamlit Native Elements)
# ============================================================
st.markdown("""
<style>
    /* Remove padding at top completely */
    .block-container { padding-top: 1rem !important; max-width: 1200px !important; margin-top: -3rem !important; }
    
    /* Clean headers */
    h1, h2, h3 { letter-spacing: -0.5px !important; }
    
    /* Soft shadows for native containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* Hide default header completely so it takes up zero space */
    header[data-testid="stHeader"] { display: none !important; height: 0px !important; }
    
    /* Premium Tabs Styling - Enlarge and Pill Shape */
    button[data-baseweb="tab"] {
        font-size: 20px !important; /* Larger text */
        font-weight: 600 !important;
        padding: 16px 24px !important; /* Larger click area */
        background-color: #f1f5f9 !important; 
        border-radius: 30px !important; /* Pill shape */
        border: none !important;
        margin-right: 8px !important;
        box-shadow: inset 0 0 0 1px #cbd5e1 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Ensure the text inside the tab button is also enlarged */
    button[data-baseweb="tab"] p {
        font-size: 18px !important; 
        font-weight: 600 !important;
        margin: 0 !important;
        color: #475569 !important;
    }
    
    /* Hover state */
    button[data-baseweb="tab"]:hover {
        background-color: #e2e8f0 !important;
        transform: translateY(-2px) !important;
    }
    
    /* Selected state */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #0f172a !important;
        box-shadow: 0 4px 12px rgba(15,23,42,0.2) !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #ffffff !important;
    }
    
    /* Hide the default Streamlit underline indicator */
    div[data-testid="stTabIndicator"] {
        display: none !important;
    }
    
    /* Remove the bottom border of the tab list container */
    div[data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🏥 Apollo Healthcare")
    st.markdown("---")
    
    with st.container(border=True):
        st.markdown(f"**👤 {patient_profile.get('patient_name')}**")
        st.caption(f"ID: {selected_patient_code}")
        st.caption(f"{patient_profile.get('age')} Y/O • {patient_profile.get('gender')}")
    
    st.markdown("---")
    if st.button(":material/logout: Sign Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ============================================================
# MAIN HEADER
# ============================================================
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 30px 40px; border-radius: 16px; color: white; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
    <h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; color: white; border: none;">Welcome back, {patient_profile.get('patient_name')}</h1>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 16px;">Access your health records, view AI assessments, and manage your medical history.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# NAVIGATION TABS
# ============================================================
tabs = st.tabs([
    ":material/space_dashboard: Dashboard", 
    ":material/history: Medical History", 
    ":material/smart_toy: AI Insights", 
    ":material/person: Profile & Data"
])

# ------------------------------------------------------------
# TAB 1: DASHBOARD
# ------------------------------------------------------------
with tabs[0]:
    st.subheader("Current Status")
    
    care_status = latest_visit.get("diagnosis") if latest_visit and latest_visit.get("diagnosis") else "Stable"
    last_visit_str = latest_visit.get("visit_date") if latest_visit else "None"
    follow_up = latest_visit.get("follow_up_date") if latest_visit else None
    next_fu_str = str(follow_up) if follow_up and str(follow_up).lower() != "none" else "None"
    meds_count = str(len(doctor_medications))

    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px;">
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 20px; border-radius: 12px; border: 1px solid #bfdbfe; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="color: #3b82f6; font-size: 13px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Care Status</div>
            <div style="color: #1e3a8a; font-size: 20px; font-weight: 800; line-height: 1.2;">{care_status}</div>
        </div>
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 20px; border-radius: 12px; border: 1px solid #bbf7d0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="color: #22c55e; font-size: 13px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Last Visit</div>
            <div style="color: #14532d; font-size: 24px; font-weight: 800;">{last_visit_str}</div>
        </div>
        <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); padding: 20px; border-radius: 12px; border: 1px solid #fde68a; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="color: #f59e0b; font-size: 13px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Next Follow-up</div>
            <div style="color: #78350f; font-size: 24px; font-weight: 800;">{next_fu_str}</div>
        </div>
        <div style="background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); padding: 20px; border-radius: 12px; border: 1px solid #f5d0fe; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="color: #d946ef; font-size: 13px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Active Medicines</div>
            <div style="color: #701a75; font-size: 28px; font-weight: 800;">{meds_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_vitals, col_history = st.columns([2, 1])
    
    with col_vitals:
        st.subheader(":material/favorite: Latest Vitals")
        vitals = patient_profile.get("vitals", {})
        if any(v is not None for v in vitals.values()):
            hr = f"{vitals.get('heart_rate', '--')} bpm"
            spo2 = f"{vitals.get('spo2', '--')} %"
            temp = f"{vitals.get('temperature', '--')} °C"
            bp = f"{vitals.get('systolic_bp', '--')}/{vitals.get('diastolic_bp', '--')}"

            st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px;">
                <div style="background: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); text-align: center;">
                    <div style="color: #ef4444; font-size: 20px; margin-bottom: 5px;">❤️</div>
                    <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">Heart Rate</div>
                    <div style="color: #0f172a; font-size: 20px; font-weight: 800; margin-top: 4px;">{hr}</div>
                </div>
                <div style="background: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); text-align: center;">
                    <div style="color: #3b82f6; font-size: 20px; margin-bottom: 5px;">💧</div>
                    <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">SpO₂</div>
                    <div style="color: #0f172a; font-size: 20px; font-weight: 800; margin-top: 4px;">{spo2}</div>
                </div>
                <div style="background: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); text-align: center;">
                    <div style="color: #f59e0b; font-size: 20px; margin-bottom: 5px;">🌡️</div>
                    <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">Temp</div>
                    <div style="color: #0f172a; font-size: 20px; font-weight: 800; margin-top: 4px;">{temp}</div>
                </div>
                <div style="background: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); text-align: center;">
                    <div style="color: #8b5cf6; font-size: 20px; margin-bottom: 5px;">🩺</div>
                    <div style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">BP</div>
                    <div style="color: #0f172a; font-size: 20px; font-weight: 800; margin-top: 4px;">{bp}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No vital signs recorded recently.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(":material/sick: Reported Symptoms")
        symptoms = patient_profile.get("symptoms", [])
        if symptoms:
            st.pills("Current Symptoms", [s.replace("_", " ").title() for s in symptoms], disabled=True)
        else:
            st.info("No current symptoms reported.")

    with col_history:
        st.subheader(":material/clinical_notes: Pre-existing Conditions")
        history = patient_profile.get("medical_history", [])
        if history:
            items_html = "".join([f'<div style="background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; font-weight: 600; display: flex; align-items: center;"><span style="margin-right: 10px;">⚠️</span> {item}</div>' for item in history])
            st.markdown(f'<div style="margin-top: 5px;">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No recorded conditions.")


# ------------------------------------------------------------
# TAB 2: MEDICAL HISTORY
# ------------------------------------------------------------
with tabs[1]:
    st.markdown('<h3 style="margin-top: 10px; color: #0f172a; font-weight: 700;">💊 Active Prescriptions</h3>', unsafe_allow_html=True)
    if doctor_medications:
        meds_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-bottom: 30px;">'
        for med in doctor_medications:
            instructions = med.get('instructions')
            instructions_html = f'<div style="background: #f8fafc; padding: 10px; border-radius: 6px; font-size: 13px; color: #475569; margin-top: 10px;"><i>"{instructions}"</i></div>' if instructions else ''
            meds_html += f"""
            <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div style="color: #0f172a; font-size: 18px; font-weight: 800; margin-bottom: 2px;">{med.get('medication_name').title()}</div>
                        <div style="color: #64748b; font-size: 13px; font-weight: 500;">Prescribed by Dr. {med.get('doctor_name', 'Unknown')}</div>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <div style="background: #f3f4f6; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; color: #4b5563;">{med.get('dosage')}</div>
                    <div style="background: #f3f4f6; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; color: #4b5563;">{med.get('frequency')}</div>
                    <div style="background: #f3f4f6; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; color: #4b5563;">{med.get('duration')}</div>
                </div>
                {instructions_html}
            </div>
            """
        meds_html += '</div>'
        st.markdown(meds_html, unsafe_allow_html=True)
    else:
        st.info("No active prescriptions.")
        
    st.markdown("---")
    st.markdown('<h3 style="margin-top: 10px; color: #0f172a; font-weight: 700;">📅 Past Clinical Visits</h3>', unsafe_allow_html=True)
    if not doctor_visits:
        st.info("No previous visits found.")
    else:
        for visit in doctor_visits:
            with st.expander(f"Visit Date: {visit.get('visit_date')} | Dr. {visit.get('doctors', {}).get('name', 'Unknown')}"):
                st.markdown(f"""
                <div style="padding: 5px;">
                    <div style="margin-bottom: 15px;">
                        <span style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">Primary Diagnosis</span><br>
                        <span style="color: #0f172a; font-size: 16px; font-weight: 600;">{visit.get('diagnosis', 'None recorded')}</span>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">Doctor's Notes</span><br>
                        <span style="color: #334155; font-size: 14px;">{visit.get('doctor_notes', 'None recorded')}</span>
                    </div>
                    <div style="display: flex; gap: 20px;">
                        <div>
                            <span style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">Care Plan</span><br>
                            <span style="color: #334155; font-size: 14px;">{visit.get('future_plan', 'None recorded')}</span>
                        </div>
                        <div>
                            <span style="color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase;">Next Scheduled Follow-up</span><br>
                            <span style="color: #334155; font-size: 14px;">{visit.get('follow_up_date', 'No follow-up scheduled')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ------------------------------------------------------------
# TAB 3: AI INSIGHTS
# ------------------------------------------------------------
with tabs[2]:
    st.markdown('<div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 8px; color: #92400e; font-size: 14px; margin-bottom: 25px;">⚠️ <b>Disclaimer:</b> Information in this section is generated by AI for clinical decision support. It is <b>NOT</b> a confirmed diagnosis. Always consult your doctor.</div>', unsafe_allow_html=True)
    
    doc_diag = latest_visit.get('diagnosis') if latest_visit and latest_visit.get("diagnosis") else "No doctor-recorded diagnosis available."
    doc_meta = f"Diagnosed by Dr. {latest_visit.get('doctors', {}).get('name', 'Unknown')} on {latest_visit.get('visit_date')}" if latest_visit and latest_visit.get("diagnosis") else ""
    
    ai_diag = latest_assessment.get('top_prediction', 'No AI-assisted assessment is available.') if latest_assessment else 'No AI-assisted assessment is available.'
    ai_meta = f"Confidence Level: {latest_assessment.get('confidence_level', 'N/A')}" if latest_assessment else ""
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
        <div style="background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; border-top: 4px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                <div style="font-size: 24px;">👨‍⚕️</div>
                <div style="font-size: 16px; font-weight: 700; color: #0f172a;">Doctor's Assessment</div>
            </div>
            <div style="font-size: 20px; font-weight: 800; color: #1e293b; margin-bottom: 5px;">{doc_diag}</div>
            <div style="font-size: 13px; color: #64748b;">{doc_meta}</div>
        </div>
        <div style="background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; border-top: 4px solid #8b5cf6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                <div style="font-size: 24px;">🤖</div>
                <div style="font-size: 16px; font-weight: 700; color: #0f172a;">AI-Assisted Review</div>
            </div>
            <div style="font-size: 20px; font-weight: 800; color: #1e293b; margin-bottom: 5px;">{ai_diag}</div>
            <div style="font-size: 13px; color: #64748b;">{ai_meta}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
                
    st.markdown("---")
    st.markdown('<h3 style="margin-top: 10px; color: #0f172a; font-weight: 700;">🚨 Risk & Safety Alerts</h3>', unsafe_allow_html=True)
    
    r1, r2 = st.columns(2)
    with r1:
        if risk_flags:
            st.markdown('<div style="background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 15px; border-radius: 8px; font-weight: 600;">🚨 Your recent assessment contains risk flags. Your doctor will review them during your visit.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 15px; border-radius: 8px; font-weight: 600;">✅ No active risk flags detected.</div>', unsafe_allow_html=True)
    with r2:
        if med_alerts:
            st.markdown('<div style="background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 15px; border-radius: 8px; font-weight: 600;">💊 Medication safety alerts detected. Please discuss your prescriptions with your doctor.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 15px; border-radius: 8px; font-weight: 600;">✅ No medication interaction alerts detected.</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# TAB 4: PROFILE & DATA
# ------------------------------------------------------------
with tabs[3]:
    st.markdown('<h3 style="margin-top: 10px; color: #0f172a; font-weight: 700;">Personal Information</h3>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
        <div style="background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;">
            <div style="background: #eff6ff; padding: 15px; border-radius: 50%; color: #3b82f6; font-size: 24px;">👤</div>
            <div>
                <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Full Name</div>
                <div style="color: #0f172a; font-size: 18px; font-weight: 700;">{patient_profile.get("patient_name")}</div>
            </div>
        </div>
        <div style="background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;">
            <div style="background: #fdf4ff; padding: 15px; border-radius: 50%; color: #d946ef; font-size: 24px;">🆔</div>
            <div>
                <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Patient ID</div>
                <div style="color: #0f172a; font-size: 18px; font-weight: 700;">{selected_patient_code}</div>
            </div>
        </div>
        <div style="background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;">
            <div style="background: #f0fdf4; padding: 15px; border-radius: 50%; color: #22c55e; font-size: 24px;">📊</div>
            <div>
                <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Demographics</div>
                <div style="color: #0f172a; font-size: 18px; font-weight: 700;">{patient_profile.get('age')} Years • {patient_profile.get('gender')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown('<h3 style="margin-top: 10px; color: #0f172a; font-weight: 700;">Export Data</h3>', unsafe_allow_html=True)
    st.write("Download your medical records in standard formats securely to your local device.")
    
    st.markdown("""
    <div style="background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; border-top: 4px solid #ef4444; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; max-width: 600px; margin: 0 auto;">
        <div style="font-size: 32px; margin-bottom: 10px;">📄</div>
        <div style="color: #0f172a; font-size: 18px; font-weight: 800; margin-bottom: 5px;">Official Clinical Discharge Summary</div>
        <div style="color: #64748b; font-size: 14px; margin-bottom: 20px;">Download a highly formatted, hospital-branded PDF containing your complete medical history, visit notes, and active prescriptions.</div>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            from src.services.pdf_generator import generate_patient_pdf
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdf_path = generate_patient_pdf(patient_profile, doctor_visits, doctor_medications, tmpfile.name)
                
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"{selected_patient_code}_Discharge_Summary.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
            os.unlink(pdf_path) # Clean up temp file
        except Exception as e:
            st.error(f"Failed to generate PDF: {e}")

