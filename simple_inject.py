import os
import re

def simple_inject():
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
    "🩺 AI Assessment Dashboard",
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
    
# We removed Doctor Dashboard block entirely, so we just fall through to the rest of the file 
# if menu == "🩺 AI Assessment Dashboard"!
"""
    # Replace the old Navigation and the Doctor Dashboard block up to the FHIR section.
    content = re.sub(
        r'# ============================================================\n# NAVIGATION\n# ============================================================.*?# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        sidebar + '\n# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        content,
        flags=re.DOTALL
    )

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Simple Injection complete.")

simple_inject()
