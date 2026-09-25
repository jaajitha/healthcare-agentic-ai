import os

def restructure_app():
    with open("app.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    out = []
    
    # 1. Base Setup (Lines 0 to 437)
    for i in range(0, 437):
        out.append(lines[i])
        
    # 2. Add New Navigation
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

""")

    # 3. Handle 🏠 Overview
    out.append("""
if menu == "🏠 Overview":
    st.markdown("## 🧠 Main AI Dashboard")
    st.write("### Hospital: Apollo Hospitals, Aragonda")
    st.info("Use the sidebar to navigate the AI assessment workflows.")
    col1, col2 = st.columns(2)
    col1.metric("Emergency", "24×7")
    col2.metric("Telemedicine", "Available")
""")

    # 4. Handle 👥 Patient Management & 📄 FHIR / EHR
    out.append("""
elif menu in ["👥 Patient Management", "📄 FHIR / EHR"]:
""")
    for i in range(457, 953):
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    # 5. Handle 🩺 Patient Assessment
    out.append("""
elif menu == "🩺 Patient Assessment":
""")
    for i in range(953, 1549):
        # We need to indent this too
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    # 6. Handle the Results block
    out.append("""
# ============================================================
# RESULTS ROUTING
# ============================================================

elif not ca and menu not in ["🏠 Overview", "👥 Patient Management", "📄 FHIR / EHR", "🩺 Patient Assessment", "📊 Assessment History", "⚙️ System Information"]:
    st.warning("No assessment data found in session. Please run a Patient Assessment first.")

elif ca:
""")
    # We copy the ca loading block (1549 to 1582)
    for i in range(1549, 1582):
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    # Now we map the remaining results block to specific menus
    # AI Analysis (1583 to 1649)
    out.append("""
    if menu == "🤖 AI Analysis":
""")
    for i in range(1582, 1649):
        # Double indent because it's inside `elif ca` and `if menu`
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # Risk & Safety (1649 to 1716, plus Red Flags 1845 to 1921)
    out.append("""
    elif menu == "⚠️ Risk & Safety":
""")
    for i in range(1649, 1716):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
    for i in range(1845, 1921):
        out.append("        " + lines[i] if lines[i].strip() else "\n")

    # Medication Safety (1716 to 1756)
    out.append("""
    elif menu == "💊 Medication Safety":
""")
    for i in range(1716, 1756):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # Medical Knowledge (1756 to 1845)
    out.append("""
    elif menu == "📚 Medical Knowledge":
""")
    for i in range(1756, 1845):
        out.append("        " + lines[i] if lines[i].strip() else "\n")

    # Hospital Routing (1921 to 1974)
    out.append("""
    elif menu == "🏥 Hospital Routing":
""")
    for i in range(1921, 1974):
        out.append("        " + lines[i] if lines[i].strip() else "\n")

    # Doctor Briefing (1974 to 2070)
    out.append("""
    elif menu == "👨‍⚕️ Doctor Briefing":
""")
    for i in range(1974, 2070):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # We close out the elif ca block.
    # What about Assessment History (2113 to 2145) and System Info?
    out.append("""
# End of CA results blocks

elif menu == "📊 Assessment History":
""")
    for i in range(2113, 2145):
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    out.append("""
elif menu == "⚙️ System Information":
    st.markdown("## ⚙️ System Information")
    st.write("**Application Version:** 1.0.0")
    st.write("**Environment:** Development")
""")

    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(out)
        
    print("app.py successfully refactored!")

restructure_app()
