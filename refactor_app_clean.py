import os
import re

def refactor():
    os.system("git restore app.py")
    
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    sidebar = """# ============================================================
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
    st.stop()
    
elif menu == "⚙️ System Information":
    st.markdown("## ⚙️ System Information")
    st.write("**Application Version:** 1.1.0")
    st.write("**Environment:** Prototype")
    st.write("**Hospital Focus:** Apollo Hospitals, Aragonda")
    st.stop()

# We don't use 'elif' for the others, we just do 'if menu != ...: st.stop()' to avoid indenting the rest of the file!
if menu == "👥 Patient Management":
    pass # we will let it flow into the FHIR block, and then st.stop() before PATIENT ASSESSMENT

elif menu == "🩺 Patient Assessment":
    pass # we will skip the FHIR block and jump straight to PATIENT ASSESSMENT
"""
    
    # Replace the navigation block
    content = re.sub(
        r'# ============================================================\n# NAVIGATION\n# ============================================================.*?# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        sidebar + '# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        content,
        flags=re.DOTALL
    )

    # Wrap the FHIR block
    # It starts at `# FHIR / EHR / SUPABASE INTEGRATION` and ends before `# PATIENT ASSESSMENT`
    fhir_setup = """if menu != "👥 Patient Management":
    # Skip FHIR block
    pass
else:
"""
    content = content.replace("# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION", fhir_setup + "# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION")
    
    # We must indent the FHIR block! But it's only from line 646 to 1139. 
    # Or, we can just use `if menu == "👥 Patient Management":` and `st.stop()` at the end of it!
    # Wait, `st.stop()` is brilliant.
    pass

refactor()
