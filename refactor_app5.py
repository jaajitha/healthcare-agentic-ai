import os
import re

def refactor():
    os.system("git restore app.py")
    
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. Replace Navigation
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
    
elif menu == "👥 Patient Management":
"""
    content = re.sub(
        r'# ============================================================\n# NAVIGATION\n# ============================================================.*?# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        sidebar + '# ============================================================\n# FHIR / EHR / SUPABASE INTEGRATION',
        content,
        flags=re.DOTALL
    )
    
    # 2. Insert menu == "Patient Assessment"
    content = content.replace(
        "# ============================================================\n# PATIENT ASSESSMENT\n# ============================================================\n",
        "elif menu == '🩺 Patient Assessment':\n# ============================================================\n# PATIENT ASSESSMENT\n# ============================================================\n"
    )
    
    # 3. Add st.tabs in the RESULTS block
    tabs_setup = """    # ========================================================
    # RESULTS
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-header">'
        '📊 Assessment Results'
        '</div>',
        unsafe_allow_html=True
    )
    
    tab_ai, tab_risk, tab_med, tab_know, tab_route, tab_brief, tab_hist = st.tabs([
        "🤖 AI Analysis", "⚠️ Risk & Alerts", "💊 Medication Safety", 
        "📚 Medical Knowledge", "🏥 Hospital Routing", "👨‍⚕️ Doctor Briefing", "📊 History"
    ])
    
    with tab_ai:
"""
    content = re.sub(
        r'    # ========================================================\n    # RESULTS\n    # ========================================================\n\n    st\.divider\(\)\n\n    st\.markdown\(\n        \'<div class="section-header">\'\n        \'📊 Assessment Results\'\n        \'</div>\',\n        unsafe_allow_html=True\n    \)',
        tabs_setup,
        content,
        flags=re.DOTALL
    )

    # 4. Map the sections to tabs.
    # By default, everything is indented correctly. We just need to replace specific section headers with `with tab_X:`
    # Risk tab
    content = content.replace("""    # ========================================================
    # TOP 5
    # ========================================================

    st.markdown(
        "### 📈 Top 5 ML Candidates"
    )""", """    # ========================================================
    # TOP 5
    # ========================================================

    st.markdown(
        "### 📈 Top 5 ML Candidates"
    )""") # Top 5 is already in tab_ai since it comes after RESULT CARDS.
    
    # We will just inject the `with tab_...:` for the others.
    # To do this robustly without breaking indentation, we won't indent the code block, we will just start `with tab:` and it will apply to the immediate next block. BUT wait! If we do `with tab_risk:`, all subsequent code must be indented!
    # Instead of Python string matching, we can use `st.container()` or simply write a small loop that indents blocks based on keywords!
    
    lines = content.split('\n')
    out_lines = []
    current_tab = "tab_ai"
    in_results = False
    
    for i, line in enumerate(lines):
        if "tab_ai, tab_risk" in line:
            in_results = True
            
        if in_results:
            if "# RED FLAGS" in line:
                current_tab = "tab_risk"
                out_lines.append(f"    with {current_tab}:")
            elif "# KNOWLEDGE" in line:
                current_tab = "tab_know"
                out_lines.append(f"    with {current_tab}:")
            elif "# INFORMATION STATUS" in line:
                current_tab = "tab_brief"
                out_lines.append(f"    with {current_tab}:")
            elif "# SAVE ASSESSMENT" in line:
                pass # remains in tab_brief
            elif "# ASSESSMENT HISTORY" in line:
                current_tab = "tab_hist"
                out_lines.append(f"    with {current_tab}:")
            elif "# SAFETY" in line:
                # We want safety outside the tabs
                current_tab = None
                
            # If we are inside results and we hit a `st.` or similar, we might need to indent it...
            # Actually, `with tab_risk:` requires indentation.
            # If I add `with tab_xxx:`, the subsequent lines MUST be indented 4 more spaces.
            
    # This is getting too complicated again.
    
    pass

refactor()
