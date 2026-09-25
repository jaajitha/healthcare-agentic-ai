import os
import re

def build_app():
    os.system("git restore app.py")
    
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Navigation to Sidebar
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
    
elif menu == "👥 Patient Management":
"""
    content = re.sub(
        r'# ============================================================\n# NAVIGATION\n# ============================================================.*?# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        sidebar + '# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        content,
        flags=re.DOTALL
    )

    # 2. Add elif menu == "Patient Assessment"
    content = content.replace(
        "# ============================================================\n# PATIENT ASSESSMENT\n# ============================================================\n",
        "elif menu == '🩺 Patient Assessment':\n# ============================================================\n# PATIENT ASSESSMENT\n# ============================================================\n"
    )

    # 3. Add tabs initialization at RESULTS
    tabs_setup = """    # ========================================================
    # RESULTS
    # ========================================================
    st.divider()
    st.markdown('<div class="section-header">📊 Assessment Results</div>', unsafe_allow_html=True)
    
    t_ai, t_risk, t_med, t_know, t_route, t_brief, t_hist = st.tabs([
        "🤖 AI Analysis", "⚠️ Risk & Alerts", "💊 Medication Safety", 
        "📚 Medical Knowledge", "🏥 Hospital Routing", "👨‍⚕️ Doctor Briefing", "📊 History"
    ])
    
    # We will alias st. methods for specific blocks to target tabs
"""
    content = content.replace("    # ========================================================\n    # RESULTS\n    # ========================================================\n\n    st.divider()\n\n    st.markdown(\n        '<div class=\"section-header\">'\n        '📊 Assessment Results'\n        '</div>',\n        unsafe_allow_html=True\n    )", tabs_setup)

    # 4. We will replace `st.` with `tab_xxx.` in specific blocks.
    # To do this robustly, we split the results section.
    parts = content.split(tabs_setup)
    
    if len(parts) == 2:
        top_half = parts[0]
        res_half = parts[1]
        
        # Result Cards (AI, Risk, Med) -> these use columns!
        # `col1, col2, col3 = st.columns(3)`
        # If we use `t_ai.columns(3)`, it works. But wait, they are distinct tabs now! We don't need 3 columns anymore.
        # But parsing out the columns is hard. Let's just use `with t_ai:` for AI, `with t_risk:` for Risk, etc.
        # It's better to just write the file completely.

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

build_app()
