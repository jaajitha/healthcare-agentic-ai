import streamlit as st
import os
import sys

# Ensure the current directory is in the path for importing supabase_client etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Single global page config for the entire application
st.set_page_config(
    page_title="Agentic AI in Healthcare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = None
if "patient_uuid" not in st.session_state:
    st.session_state["patient_uuid"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# OAuth redirect handling (Removed URL Auth backdoor)
if not st.session_state.get("authenticated") and "code" in st.query_params:
    try:
        from src.services.supabase_client import get_supabase_client, get_patient_by_email
        auth_code = st.query_params["code"]
        res = get_supabase_client().auth.exchange_code_for_session({"auth_code": auth_code})
        if res and hasattr(res, 'user') and res.user:
            st.session_state["authenticated"] = True
            st.session_state["user_role"] = "patient" # default to patient
            st.session_state["username"] = res.user.email
            
            pat = get_patient_by_email(res.user.email)
            if pat:
                st.session_state["patient_id"] = pat.get("patient_id")
                st.session_state["patient_uuid"] = pat.get("id")
            else:
                # Fallback to P001 for demo if Google email not in DB
                st.session_state["patient_id"] = "P001"
                try:
                    p001_res = get_supabase_client().table("patients").select("id").eq("patient_id", "P001").execute()
                    if p001_res.data:
                        st.session_state["patient_uuid"] = p001_res.data[0]["id"]
                    else:
                        st.session_state["patient_uuid"] = "fallback-uuid"
                except:
                    st.session_state["patient_uuid"] = "fallback-uuid"
            
            # Clear code from URL
            del st.query_params["code"]
            st.rerun()
    except Exception as e:
        st.error(f"Authentication Error: {e}")
        if "code" in st.query_params:
            del st.query_params["code"]

def logout():
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["patient_id"] = None
    st.session_state["patient_uuid"] = None
    st.session_state["username"] = None
    st.rerun()

# Routing Logic using st.navigation
if not st.session_state["authenticated"]:
    # Unauthenticated -> Login page
    pg = st.navigation([st.Page("src/pages/login.py", title="Login")])
    pg.run()
else:
    # Authenticated -> Role-based dashboard
    role = st.session_state["user_role"]
    
    if role == "patient":
        pg = st.navigation([st.Page("src/pages/patient_dashboard.py", title="Patient Dashboard")])
        pg.run()
    elif role == "doctor":
        pg = st.navigation([st.Page("src/pages/doctor_dashboard.py", title="Doctor Dashboard")])
        pg.run()
    elif role == "admin":
        pg = st.navigation([st.Page("src/pages/admin_dashboard.py", title="Admin Dashboard")])
        pg.run()
    else:
        st.error("Unknown role.")
        if st.button("Logout"):
            logout()
