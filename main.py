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
if "cookie_controller" not in st.session_state:
    try:
        from streamlit_cookies_controller import CookieController
        st.session_state["cookie_controller"] = CookieController()
    except Exception:
        st.session_state["cookie_controller"] = None

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

# Check cookies for persisted authentication
# Check cookies for persisted authentication using native context (instant)
if not st.session_state.get("authenticated") and hasattr(st, "context"):
    try:
        saved_role = st.context.cookies.get("auth_role")
        if saved_role:
            saved_role = saved_role.strip('"').strip("'")
            st.session_state["authenticated"] = True
            st.session_state["user_role"] = saved_role
            st.session_state["username"] = st.context.cookies.get("auth_username", "").strip('"').strip("'")
            if saved_role == "patient":
                st.session_state["patient_id"] = st.context.cookies.get("auth_patient_id", "").strip('"').strip("'")
                st.session_state["patient_uuid"] = st.context.cookies.get("auth_patient_uuid", "").strip('"').strip("'")
    except Exception as e:
        print("Cookie read error:", e)

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
            
            # Write to cookie for OAuth login persistence
            patient_id = st.session_state.get("patient_id", "")
            patient_uuid = st.session_state.get("patient_uuid", "")
            email = res.user.email
            
            # Clear code from URL first
            del st.query_params["code"]
            
            js_code = f"""
            <script>
            document.cookie = "auth_role=patient; path=/; max-age=31536000";
            document.cookie = "auth_username={email}; path=/; max-age=31536000";
            document.cookie = "auth_patient_id={patient_id}; path=/; max-age=31536000";
            document.cookie = "auth_patient_uuid={patient_uuid}; path=/; max-age=31536000";
            window.parent.location.reload();
            </script>
            """
            import streamlit.components.v1 as components
            components.html(js_code, height=0)
            st.stop()
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
    
    js_code = """
    <script>
    document.cookie = "auth_role=; path=/; max-age=0";
    document.cookie = "auth_username=; path=/; max-age=0";
    document.cookie = "auth_patient_id=; path=/; max-age=0";
    document.cookie = "auth_patient_uuid=; path=/; max-age=0";
    window.parent.location.reload();
    </script>
    """
    import streamlit.components.v1 as components
    components.html(js_code, height=0)
    st.stop()

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
