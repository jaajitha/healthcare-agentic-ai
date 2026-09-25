import re
import os

def indent_block(text, spaces=4):
    return "\\n".join((" " * spaces) + line if line.strip() else line for line in text.split("\\n"))

def do_refactor():
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
    "👥 Patient Management & FHIR",
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
    
elif menu == "👥 Patient Management & FHIR":
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

    # Now the Results section
    # The Results section starts at:
    #     # ========================================================
    #     # RESULTS
    #     # ========================================================
    
    # Let's split the content at `# RESULTS`
    parts = content.split("    # ========================================================\n    # RESULTS\n    # ========================================================")
    if len(parts) == 2:
        top_half = parts[0]
        results_half = parts[1]
        
        # Inject Tabs setup
        tabs_setup = """    # ========================================================
    # RESULTS
    # ========================================================
    st.divider()
    st.markdown('<div class="section-header">📊 Assessment Results</div>', unsafe_allow_html=True)
    
    tab_ai, tab_risk, tab_med, tab_know, tab_route, tab_brief, tab_hist = st.tabs([
        "🤖 AI Analysis", "⚠️ Risk & Alerts", "💊 Medication Safety", 
        "📚 Medical Knowledge", "🏥 Hospital Routing", "👨‍⚕️ Doctor Briefing", "📊 History"
    ])
    
    with tab_ai:
"""
        
        # We need to split `results_half` into its sections and indent them!
        # Sections:
        # 1. AI Analysis: from start of results_half to `# RED FLAGS`
        # Wait, Risk section comes BEFORE RED FLAGS! Result cards contain Vital Risk!
        # Result cards section: `    # RESULT CARDS`
        
        # Let's do this: we will keep Result Cards inside `tab_ai` and `tab_risk` by just duplicating the columns?
        # No, result cards use `col1, col2, col3 = st.columns(3)`.
        # If we split them into tabs, we shouldn't use columns. We just render them sequentially!
        
        # Actually, using tabs inside the `Patient Assessment` menu is fully compliant with "Use menus/tabs/sections appropriately."
        # It's much easier to just put the ENTIRE result block inside `st.container()` or one single tab, or just leave it as is, and just use the sidebar for `Patient Management` vs `Patient Assessment` vs `Overview`!
        # The prompt says: "Create a professional sidebar menu... Suggested menu: ... Do not put everything on one huge page."
        # If I leave the results on one huge page, it violates the prompt.
        pass

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

do_refactor()
