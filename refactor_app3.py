import os

def build_app():
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
    "👥 Patient Management & FHIR",
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
""")

    # 2. Patient Management (Lines 646 to 1139)
    # We will combine FHIR and Loaded Patient
    out.append('\nelif menu == "👥 Patient Management & FHIR":\n')
    for i in range(646, 1139):
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    # 3. Patient Assessment (Lines 1139 to 1718)
    out.append('\nelif menu == "🩺 Patient Assessment":\n')
    for i in range(1139, 1718):
        # We also need to add hospital_routing logic right after `top_indices` calculation (around line 1444)
        if "top_indices = (" in lines[i] or ".argsort()[-5:][::-1]" in lines[i-2 if i>=2 else i]:
            pass # just noting where it is
        out.append("    " + lines[i] if lines[i].strip() else "\n")

    # Inject Hospital Routing fix directly into the file string later
        
    # 4. Results Block Setup (Loading CA variables)
    out.append("""
# ============================================================
# RESULTS ROUTING
# ============================================================
elif not ca and menu not in ["🏠 Overview", "👥 Patient Management & FHIR", "🩺 Patient Assessment", "📊 Assessment History", "⚙️ System Information"]:
    st.warning("No assessment data found in session. Please run a Patient Assessment first.")

elif ca:
""")
    for i in range(1720, 1752):
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    # 🤖 AI Analysis (Result Cards Prediction, Top 5)
    out.append('\n    if menu == "🤖 AI Analysis":\n')
    # Result cards (prediction) lines 1775 to 1827
    for i in range(1775, 1827):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
    # Top 5 lines 1888 to 1928
    for i in range(1888, 1928):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # ⚠️ Risk & Safety (Result Cards Vital Risk, Red Flags)
    out.append('\n    elif menu == "⚠️ Risk & Safety":\n')
    # Result cards (Vital Risk) lines 1828 to 1856
    for i in range(1828, 1856):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
    # Red Flags lines 1999 to 2023
    for i in range(1999, 2023):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # 💊 Medication Safety (Result Cards Med Safety, Current Meds)
    out.append('\n    elif menu == "💊 Medication Safety":\n')
    # Result cards (Med Safety) lines 1857 to 1887
    for i in range(1857, 1887):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # 📚 Medical Knowledge (Knowledge Retrieval lines 1928 to 1999)
    out.append('\n    elif menu == "📚 Medical Knowledge":\n')
    for i in range(1928, 1999):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # 🏥 Hospital Routing 
    # (Since it was missing in the original file, we implement it here)
    out.append("""
    elif menu == "🏥 Hospital Routing":
        st.markdown("### 🏥 Apollo Aragonda Hospital Routing")
        from hospital_routing_agent import route_patient_to_hospital, format_routing_result
        if ca.get("valid_symptoms"):
            routing_result = route_patient_to_hospital(symptoms=ca["valid_symptoms"])
            st.write(format_routing_result(routing_result))
        else:
            st.info("No symptoms reported for routing.")
""")

    # 👨‍⚕️ Doctor Briefing (Information Status, Agentic Decision, Doctor Briefing, Save Assessment)
    out.append('\n    elif menu == "👨‍⚕️ Doctor Briefing":\n')
    # Info Status lines 2023 to 2047
    for i in range(2023, 2047):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
    # Agentic Decision lines 2047 to 2091
    for i in range(2047, 2091):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
    # Doctor Briefing lines 2091 to 2161
    for i in range(2091, 2161):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
    # Save Assessment lines 2161 to 2208
    for i in range(2161, 2208):
        out.append("        " + lines[i] if lines[i].strip() else "\n")
        
    # End of CA blocks
    
    # 📊 Assessment History (Lines 2208 to 2240)
    out.append('\nelif menu == "📊 Assessment History":\n')
    for i in range(2208, 2240):
        out.append("    " + lines[i] if lines[i].strip() else "\n")
        
    # ⚙️ System Information
    out.append("""
elif menu == "⚙️ System Information":
    st.markdown("## ⚙️ System Information")
    st.write("**Application Version:** 1.1.0")
    st.write("**Environment:** Prototype")
    st.write("**Hospital Focus:** Apollo Hospitals, Aragonda")
""")

    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(out)
        
    print("Refactoring complete.")

build_app()
