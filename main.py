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

# Auto-login from query params if page refreshed
if not st.session_state.get("authenticated"):
    # Handle Supabase OAuth PKCE redirect
    if "error" in st.query_params and "error_description" in st.query_params:
        st.error(f"Google Login Cancelled or Failed: {st.query_params['error_description']}")
        del st.query_params["error"]
        del st.query_params["error_description"]
        
    elif "code" in st.query_params:
        try:
            from supabase_client import supabase, get_patient_by_email
            auth_code = st.query_params["code"]
            res = supabase.auth.exchange_code_for_session({"auth_code": auth_code})
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
                        p001_res = supabase.table("patients").select("id").eq("patient_id", "P001").execute()
                        if p001_res.data:
                            st.session_state["patient_uuid"] = p001_res.data[0]["id"]
                        else:
                            st.session_state["patient_uuid"] = "fallback-uuid"
                    except:
                        st.session_state["patient_uuid"] = "fallback-uuid"
                
                # Clear code from URL
                if "code" in st.query_params:
                    del st.query_params["code"]
                if "google_auth_url" in st.session_state:
                    del st.session_state["google_auth_url"]
                st.rerun()
        except Exception as e:
            st.error(f"Authentication Error: {e}")
            if "code" in st.query_params:
                del st.query_params["code"]
            if "google_auth_url" in st.session_state:
                del st.session_state["google_auth_url"]

    # Handle standard app routing query params
    elif "auth_role" in st.query_params and "auth_user" in st.query_params:
        st.session_state["authenticated"] = True
        st.session_state["user_role"] = st.query_params["auth_role"]
        st.session_state["username"] = st.query_params["auth_user"]
        
        # If it's a patient, we also need patient_id and patient_uuid
        if st.query_params["auth_role"] == "patient":
            st.session_state["patient_id"] = st.query_params["auth_user"]
            if "auth_uuid" in st.query_params:
                st.session_state["patient_uuid"] = st.query_params["auth_uuid"]

def logout():
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["patient_id"] = None
    st.session_state["patient_uuid"] = None
    st.session_state["username"] = None
    
    # Clear query params
    if "auth_role" in st.query_params:
        del st.query_params["auth_role"]
    if "auth_user" in st.query_params:
        del st.query_params["auth_user"]
    if "auth_uuid" in st.query_params:
        del st.query_params["auth_uuid"]

# Routing Logic
if not st.session_state["authenticated"]:
    # Render Login Page
    with open("login.py", "r", encoding="utf-8") as f:
        env = globals().copy()
        env["__name__"] = "__imported__"
        exec(f.read(), env)
        env["render_login_page"]()
else:
    # Render appropriate dashboard based on role
    role = st.session_state["user_role"]
    
    if role == "patient":
        with open("patient_dashboard.py", "r", encoding="utf-8") as f:
            env = globals().copy()
            # Set name to something other than main so set_page_config is skipped in the imported file
            env["__name__"] = "__imported__" 
            exec(f.read(), env)
            
    elif role == "doctor":
        with open("doctor_dashboard.py", "r", encoding="utf-8") as f:
            env = globals().copy()
            env["__name__"] = "__imported__"
            exec(f.read(), env)
            
    elif role == "admin":
        with open("app.py", "r", encoding="utf-8") as f:
            env = globals().copy()
            env["__name__"] = "__imported__"
            exec(f.read(), env)
