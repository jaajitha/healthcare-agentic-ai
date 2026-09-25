import os

def build_app():
    os.system("git restore app.py")
    
    with open("app.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    out = []
    
    # 0. Setup and Helpers (Lines 0 to 408)
    for i in range(0, 409):
        out.append(lines[i])
        
    # 1. New Sidebar Navigation
    out.append("""
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
    
elif menu == "⚙️ System Information":
    st.markdown("## ⚙️ System Information")
    st.write("**Application Version:** 1.1.0")
    st.write("**Environment:** Prototype")
    st.write("**Hospital Focus:** Apollo Hospitals, Aragonda")
""")

    # Find where FHIR block starts
    fhir_start = -1
    for i, line in enumerate(lines):
        if line.startswith("# FHIR / EHR / SUPABASE INTEGRATION"):
            fhir_start = i - 1
            break
            
    # Find where PATIENT ASSESSMENT starts
    assessment_start = -1
    for i in range(fhir_start, len(lines)):
        if line.startswith("# PATIENT ASSESSMENT") and lines[i-1].startswith("# ===="):
            assessment_start = i - 1
            break
            
    # Hardcode based on our previous findings since the lines are stable in git
    fhir_start = 458
    assessment_start = 954
    
    # 2. Patient Management Block
    out.append('\nelif menu == "👥 Patient Management":\n')
    for i in range(fhir_start - 1, assessment_start - 1): # -1 because list is 0-indexed
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    # 3. Patient Assessment Block
    out.append('\nelif menu == "🩺 Patient Assessment":\n')
    for i in range(assessment_start - 1, len(lines)):
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(out)
        
    print("Refactoring complete.")

build_app()
