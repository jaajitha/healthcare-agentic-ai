import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace Navigation
nav_replacement = """# ============================================================
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
    "📄 FHIR / EHR",
    "🩺 Patient Assessment",
    "🤖 AI Analysis",
    "⚠️ Risk & Safety",
    "💊 Medication Safety",
    "📚 Medical Knowledge",
    "🏥 Hospital Routing",
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
    col1, col2 = st.columns(2)
    col1.metric("Emergency", "24×7")
    col2.metric("Telemedicine", "Available")
    st.info("Use the sidebar to navigate the AI assessment workflows.")

elif menu in ["👥 Patient Management", "📄 FHIR / EHR"]:
"""

content = re.sub(r'# ============================================================\n# NAVIGATION\n# ============================================================.*?# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION', nav_replacement + '\n# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION', content, flags=re.DOTALL)

# 2. Indent the Patient Management and FHIR/EHR block
# From "# FHIR / EHR / SUPABASE INTEGRATION" up to "# PATIENT ASSESSMENT INPUTS"
fhir_block = re.search(r'(# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION.*?)(?=# ============================================================\n# PATIENT ASSESSMENT INPUTS)', content, re.DOTALL).group(1)
indented_fhir = "\n".join(["    " + line if line.strip() else line for line in fhir_block.split("\n")])
content = content.replace(fhir_block, indented_fhir)

# 3. Patient Assessment Inputs
assessment_input = """
elif menu == "🩺 Patient Assessment":
"""
content = content.replace("# ============================================================\n# PATIENT ASSESSMENT INPUTS", assessment_input + "\n    # ============================================================\n    # PATIENT ASSESSMENT INPUTS")

# Indent from "PATIENT ASSESSMENT INPUTS" to "RESULTS"
assess_block = re.search(r'(    # ============================================================\n    # PATIENT ASSESSMENT INPUTS.*?)(?=# ============================================================\n# RESULTS)', content, re.DOTALL).group(1)
indented_assess = "\n".join(["    " + line.removeprefix("    ") if line.strip() else line for line in assess_block.split("\n")]) # Fix double indent if already indented
# Actually just split and add 4 spaces
indented_assess = "\n".join(["    " + line if line.strip() else line for line in assess_block.split("\n")])
content = content.replace(assess_block, indented_assess)


# 4. Results Section 
# The results section starts at # RESULTS and goes until # SAVE ASSESSMENT
results_replacement = """
# ============================================================
# RESULTS RENDERERS
# ============================================================

if not ca and menu not in ["🏠 Overview", "👥 Patient Management", "📄 FHIR / EHR", "🩺 Patient Assessment", "📊 Assessment History", "⚙️ System Information"]:
    st.warning("No assessment data found in session. Please run a Patient Assessment first.")
elif ca:
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

    if menu == "🤖 AI Analysis":
"""
content = re.sub(r'ca = st\.session_state\["current_assessment"\].*?# ============================================================\n    # RESULT CARDS\n    # ============================================================', results_replacement + '\n    # ============================================================\n    # RESULT CARDS\n    # ============================================================', content, flags=re.DOTALL)

# 5. Fix tabs in results
content = content.replace('    with col1:\n\n        st.markdown(\n            \'<div class="result-card">\'', '        st.markdown(\n            \'<div class="result-card">\'')

# For this, it's easier to just do regex replaces for the specific menus.
# We will use replace_file_content to finalize it if needed.

with open("app_new.py", "w", encoding="utf-8") as f:
    f.write(content)
