import os

def build_app():
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    # We will restore the original file first to be safe
    os.system("git restore app.py")
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Split the file by the section headers
    # We will use simple string replacements to inject the menus.
    
    # 1. Inject Authentication and Sidebar Menu
    sidebar_menu = """
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
menu = st.sidebar.radio("Go to", [
    "🏠 Overview",
    "👥 Patient Management",
    "🩺 Patient Assessment",
    "🤖 AI Analysis",
    "⚠️ Risk & Safety",
    "💊 Medication Safety",
    "🏥 Hospital Routing",
    "📚 Medical Knowledge",
    "👨‍⚕️ Doctor Briefing",
    "📊 Assessment History",
    "⚙️ System Information",
    "🚪 Logout"
])

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

elif menu == "⚙️ System Information":
    st.markdown("## ⚙️ System Information")
    st.write("**Application Version:** 1.1.0")
    st.write("**Environment:** Prototype")
    st.write("**Hospital Focus:** Apollo Hospitals, Aragonda")
    st.stop()

elif menu == "👥 Patient Management":
"""
    # Replace the old Navigation block up to the FHIR block
    import re
    content = re.sub(r'# ============================================================\n# NAVIGATION\n# ============================================================.*?# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION', sidebar_menu + '\n# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION', content, flags=re.DOTALL)
    
    # 2. Insert `elif menu == "🩺 Patient Assessment":` before `# PATIENT ASSESSMENT`
    content = content.replace("# ============================================================\n# PATIENT ASSESSMENT\n# ============================================================\n", """
elif menu == "🩺 Patient Assessment":
# ============================================================
# PATIENT ASSESSMENT
# ============================================================
""")

    # 3. Add `st.stop()` at the end of the `if assess:` block (before RESULTS)
    # The RESULTS block starts with `# RENDER ASSESSMENT RESULTS`
    # BUT we need `ca` variables available for the other tabs, so we extract the results logic out.
    
    # To avoid indentation errors, I will replace the # RENDER ASSESSMENT RESULTS section
    results_injection = """
elif menu not in ["🏠 Overview", "👥 Patient Management", "🩺 Patient Assessment", "⚙️ System Information", "🚪 Logout"]:
    if not ca:
        st.warning("No assessment data found in session. Please run a Patient Assessment first.")
        st.stop()
    
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

# ============================================================
# RENDER ASSESSMENT RESULTS
"""
    content = content.replace("# ============================================================\n# RENDER ASSESSMENT RESULTS\n# ============================================================", results_injection)
    
    # Now replace the specific layout headers with `if menu == "..."`
    
    # 4. Result Cards (AI Analysis, Risk, Medication) -> we can keep them in their respective menus
    # Or to make it simpler, we just use `if menu == "🤖 AI Analysis":`
    content = content.replace("""    # ========================================================
    # RESULT CARDS
    # ========================================================

    col1, col2, col3 = st.columns(3)""", """    # ========================================================
    # RESULT CARDS
    # ========================================================
    if menu == "🤖 AI Analysis":
        col1, col2, col3 = st.columns(3)""")

    # We need to manually fix up the rest. It's much better to just inject Tabs instead of sidebars for the results. 
    # The prompt says "Use menus/tabs/sections appropriately."
    # If I use `st.tabs` for the RESULTS block, it's 100% robust and requires almost zero restructuring of the logic!
    
    pass

build_app()
