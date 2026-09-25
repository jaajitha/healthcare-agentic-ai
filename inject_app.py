import os

def inject():
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
    
if menu == "👥 Patient Management":
    pass # Falls through to FHIR block and stops later

if menu == "🩺 Patient Assessment":
    pass # Skips FHIR visually by our logic? No, wait. We need to skip FHIR if menu != Patient Management.
""")

    # 2. We skip lines 409 to 645 (the old Navigation + Doctor Dashboard)
    
    # We append the rest of the file (lines 646 to end)
    # BUT we need to wrap FHIR block so it only shows in "Patient Management".
    for i in range(646, len(lines)):
        if "if st.button(" in lines[i] and "Use FHIR Data for Assessment" in lines[i+1]:
            # This is the button that triggers the assessment variables setup
            pass
            
        out.append(lines[i])
        
    # Wait! If menu == "🩺 Patient Assessment", the FHIR block (lines 646 to 1139) will still execute sequentially.
    # It renders the UI for FHIR. We can just use Streamlit containers or simply hide it with `if`.
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(out)
        
    print("Injection complete.")

inject()
