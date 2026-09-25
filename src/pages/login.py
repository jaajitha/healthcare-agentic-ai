import streamlit as st
import textwrap

def initialize_session():
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
    if "otp_sent_to" not in st.session_state:
        st.session_state["otp_sent_to"] = None
    if "login_mode" not in st.session_state:
        st.session_state["login_mode"] = "password" # "password" or "magic_link"

def finalize_login(role, email):
    st.session_state["authenticated"] = True
    st.session_state["user_role"] = role
    st.session_state["username"] = email
    st.session_state["otp_sent_to"] = None
    
    if role == "patient":
        try:
            from src.services.supabase_client import get_patient_by_email
            patient = get_patient_by_email(email)
            if patient:
                st.session_state["patient_id"] = patient.get("patient_id")
                st.session_state["patient_uuid"] = patient.get("id")
                st.query_params["auth_role"] = "patient"
                st.query_params["auth_user"] = email
                st.query_params["auth_uuid"] = patient.get("id")
            else:
                st.session_state["patient_id"] = "P001"
                st.query_params["auth_role"] = "patient"
        except:
            st.session_state["patient_id"] = "P001"
            st.query_params["auth_role"] = "patient"
            
    elif role == "doctor":
        st.query_params["auth_role"] = "doctor"
        st.query_params["auth_user"] = email
        
    elif role == "admin":
        st.query_params["auth_role"] = "admin"
        st.query_params["auth_user"] = email
        
    st.rerun()

def do_login(role, username, password):
    try:
        from src.services.supabase_client import sign_in_with_email
        res = sign_in_with_email(username, password)
        if res and hasattr(res, 'user') and res.user:
            finalize_login(role, res.user.email)
            return
    except Exception as e:
        pass

    # --- DEMO FALLBACK ---
    if role == "patient":
        if username.startswith("P00") and password == "Patient@123":
            finalize_login("patient", username)
        else:
            st.error("Invalid Email/ID or Password")
    elif role == "doctor":
        valid_doctors = ["dr.sreedhar.b@apollohospitals.com", "dr.bharathi.mv@apollohospitals.com", "doctor"]
        if username in valid_doctors and password == "Doctor@123":
            finalize_login("doctor", username)
        else:
            st.error("Invalid Doctor Email or Password")
    elif role == "admin":
        if username == "admin" and password == "Admin@123":
            finalize_login("admin", username)
        else:
            st.error("Invalid Admin Username or Password")

def do_otp_request(email):
    if not email:
        st.error("Please enter a valid email address.")
        return
    try:
        from src.services.supabase_client import send_otp
        send_otp(email)
        st.session_state["otp_sent_to"] = email
        st.rerun()
    except Exception as e:
        st.error(f"Could not send OTP: {e}")

def do_otp_verify(role, email, code):
    try:
        from src.services.supabase_client import verify_otp
        res = verify_otp(email, code)
        if res and hasattr(res, 'user') and res.user:
            finalize_login(role, res.user.email)
        else:
            st.error("Invalid or expired code.")
    except Exception as e:
        st.error(f"Verification failed: {e}")

def render_google_button():
    if "google_auth_url" not in st.session_state:
        try:
            from src.services.supabase_client import sign_in_with_google
            res = sign_in_with_google("http://localhost:8501")
            if res and hasattr(res, 'url'):
                st.session_state["google_auth_url"] = res.url
            else:
                st.session_state["google_auth_url"] = "#"
        except Exception as e:
            st.session_state["google_auth_url"] = "#"
            
    target_url = st.session_state["google_auth_url"]
        
    btn_html = f"""
    <a href="{target_url}" target="_self" style="
        display: block;
        width: 100%;
        text-align: center;
        background-color: white;
        color: #444;
        padding: 12px 0;
        border-radius: 8px;
        text-decoration: none;
        font-size: 15px;
        font-weight: 600;
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #ddd;
        transition: all 0.3s ease;
    " onclick="if('{target_url}' === '#') {{ alert('Google Auth is not configured in Supabase Dashboard yet!'); return false; }}">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" width="18" height="18" style="vertical-align: middle; margin-right: 10px;">
        Continue with Google
    </a>
    """
    st.markdown(btn_html, unsafe_allow_html=True)

def render_login_page():
    initialize_session()
    
    # Modern CSS targeting stAppViewContainer to fix gradient background issue
    css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Fix for modern Streamlit background */
[data-testid="stAppViewContainer"], .stApp {
background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #121c21) !important;
background-size: 400% 400% !important;
animation: gradientBG 15s ease infinite !important;
font-family: 'Outfit', sans-serif !important;
}

@keyframes gradientBG {
0% { background-position: 0% 50%; }
50% { background-position: 100% 50%; }
100% { background-position: 0% 50%; }
}

header[data-testid="stHeader"], footer { display: none !important; }

/* Professional Glassmorphism Card */
.block-container {
background: rgba(15, 23, 36, 0.75) !important;
backdrop-filter: blur(25px) !important;
-webkit-backdrop-filter: blur(25px) !important;
border: 1px solid rgba(255, 255, 255, 0.08) !important;
border-radius: 24px !important;
padding: 4rem !important;
box-shadow: 0 40px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1) !important;
max-width: 1000px !important;
margin-top: 6vh !important;
margin-bottom: 6vh !important;
color: #ffffff !important;
}

h1, h2, h3, h4, h5, h6, p, span, div, label {
font-family: 'Outfit', sans-serif !important;
color: #ffffff !important;
}

label {
font-size: 14px !important;
font-weight: 500 !important;
opacity: 0.9 !important;
margin-bottom: 5px !important;
}

/* Tabs Styling */
button[data-baseweb="tab"] {
background: transparent !important;
border: none !important;
border-bottom: 3px solid transparent !important;
color: rgba(255, 255, 255, 0.4) !important;
font-size: 15px !important;
font-weight: 600 !important;
padding-bottom: 12px !important;
transition: all 0.3s ease !important;
text-transform: uppercase !important;
letter-spacing: 1px !important;
}

button[data-baseweb="tab"]:hover {
color: #ffffff !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
color: #00e5ff !important;
border-bottom: 3px solid #00e5ff !important;
}

div[data-baseweb="tab-list"] {
gap: 30px !important;
border-bottom: 1px solid rgba(255,255,255,0.1) !important;
margin-bottom: 25px !important;
}

/* Inputs - Professional Styling */
div[data-baseweb="input"], div[data-baseweb="base-input"] {
background: rgba(0, 0, 0, 0.2) !important;
border: 1px solid rgba(255, 255, 255, 0.15) !important;
border-radius: 8px !important;
transition: all 0.3s ease !important;
}

div[data-baseweb="input"]:focus-within {
border-color: #00e5ff !important;
background: rgba(0, 0, 0, 0.4) !important;
box-shadow: 0 0 0 1px #00e5ff !important;
}

div[data-baseweb="input"] > div {
background-color: transparent !important;
}

input {
color: white !important;
font-weight: 500 !important;
font-size: 15px !important;
padding: 12px !important;
}

input::placeholder {
color: rgba(255,255,255,0.3) !important;
}

/* Primary Button */
div[data-testid="stButton"] button[kind="primary"] {
background: #00e5ff !important;
color: #0f2027 !important;
border: none !important;
border-radius: 8px !important;
padding: 12px 0 !important;
font-size: 15px !important;
font-weight: 700 !important;
letter-spacing: 0.5px !important;
transition: all 0.3s ease !important;
width: 100% !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
transform: translateY(-2px) !important;
box-shadow: 0 10px 20px rgba(0, 229, 255, 0.3) !important;
background: #33eeff !important;
}

div[data-testid="stButton"] button[kind="primary"] p {
color: #0f2027 !important;
font-weight: 700 !important;
}

/* Secondary Button */
div[data-testid="stButton"] button[kind="secondary"] {
background: rgba(255,255,255,0.05) !important;
color: white !important;
border: 1px solid rgba(255,255,255,0.2) !important;
border-radius: 8px !important;
padding: 12px 0 !important;
font-size: 15px !important;
font-weight: 600 !important;
transition: all 0.3s ease !important;
width: 100% !important;
}

div[data-testid="stButton"] button[kind="secondary"]:hover {
background: rgba(255,255,255,0.1) !important;
border-color: rgba(255,255,255,0.4) !important;
}

.feature-pill {
background: rgba(0, 229, 255, 0.1);
border: 1px solid rgba(0, 229, 255, 0.3);
padding: 8px 16px;
border-radius: 20px;
font-size: 13px;
font-weight: 600;
display: inline-block;
margin: 0 10px 10px 0;
color: #00e5ff !important;
transition: all 0.3s;
}

.divider {
display: flex;
align-items: center;
text-align: center;
margin: 25px 0;
color: rgba(255,255,255,0.4);
font-size: 12px;
font-weight: 600;
text-transform: uppercase;
letter-spacing: 1px;
}
.divider::before, .divider::after {
content: '';
flex: 1;
border-bottom: 1px solid rgba(255,255,255,0.1);
}
.divider:not(:empty)::before { margin-right: .5em; }
.divider:not(:empty)::after { margin-left: .5em; }
</style>"""
    st.markdown(css, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.1, 1], gap="large")
    
    with col1:
        html1 = """<div style="padding-right: 30px; height: 100%; display: flex; flex-direction: column; justify-content: center;">
<div style="font-size: 60px; margin-bottom: 20px;">🏥</div>
<h1 style="font-size: 48px; font-weight: 800; line-height: 1.1; margin-bottom: 20px; letter-spacing: -1px;">Apollo Hospitals<br><span style="color: #00e5ff;">Aragonda</span></h1>
<p style="font-size: 18px; margin-bottom: 40px; opacity: 0.7; font-weight: 300; line-height: 1.6;">India's First Modern Rural Hospital powered by Intelligent Agentic AI. Securely access your medical portal.</p>
<div>
<div class="feature-pill">🛏️ 50-Bed Secondary Care</div>
<div class="feature-pill">🚑 24/7 Emergency Care</div>
<div class="feature-pill">💻 Telemedicine</div>
<div class="feature-pill">💊 24/7 Pharmacy</div>
</div>
</div>"""
        st.markdown(html1, unsafe_allow_html=True)
        
    with col2:
        html2 = """<div style="text-align: left; margin-bottom: 30px;">
<h2 style="font-size: 32px; font-weight: 700; margin-bottom: 5px;">Welcome Back</h2>
<p style="opacity: 0.6; font-size: 15px;">Sign in to your account</p>
</div>"""
        st.markdown(html2, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Patient", "Doctor", "Admin"])
        
        with tab1:
            if st.session_state["otp_sent_to"]:
                st.info(f"📧 A 6-digit code has been sent to **{st.session_state['otp_sent_to']}**.")
                with st.form("otp_verify_form", clear_on_submit=False):
                    otp_code = st.text_input("Enter 6-digit Code", placeholder="123456")
                    st.write("") # Spacer
                    if st.form_submit_button("Verify & Sign In", type="primary", use_container_width=True):
                        do_otp_verify("patient", st.session_state["otp_sent_to"], otp_code)
                if st.button("Cancel", type="secondary", use_container_width=True):
                    st.session_state["otp_sent_to"] = None
                    st.rerun()
            else:
                # Clean native mode selector
                mode = st.radio(
                    "Login Method",
                    ["Password", "Magic Link (Email OTP)"],
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                st.write("") # Spacer
                
                if mode == "Password":
                    with st.form("patient_login_form", clear_on_submit=False):
                        p_user = st.text_input("Email Address / ID", placeholder="patient@gmail.com")
                        p_pass = st.text_input("Password", type="password", placeholder="••••••••")
                        st.write("") # Spacer
                        if st.form_submit_button("Sign in securely", type="primary", use_container_width=True):
                            do_login("patient", p_user, p_pass)
                else:
                    with st.form("otp_request_form", clear_on_submit=False):
                        otp_email = st.text_input("Email Address", placeholder="patient@gmail.com")
                        st.write("") # Spacer
                        if st.form_submit_button("Send Magic Link", type="primary", use_container_width=True):
                            do_otp_request(otp_email)
                
                st.markdown('<div class="divider">or continue with</div>', unsafe_allow_html=True)
                render_google_button()
                
        with tab2:
            st.info("Staff Login Area")
            with st.form("doctor_login_form", clear_on_submit=False):
                d_user = st.text_input("Work Email", placeholder="dr.name@apollohospitals.com")
                d_pass = st.text_input("Password", type="password", placeholder="••••••••")
                st.write("") # Spacer
                if st.form_submit_button("Sign in to Portal", type="primary", use_container_width=True):
                    do_login("doctor", d_user, d_pass)
            
            st.markdown('<div class="divider">or continue with</div>', unsafe_allow_html=True)
            render_google_button()

        with tab3:
            with st.form("admin_login_form", clear_on_submit=False):
                a_user = st.text_input("Admin Username", placeholder="admin")
                a_pass = st.text_input("Password", type="password", placeholder="••••••••")
                st.write("") # Spacer
                if st.form_submit_button("Sign in to Console", type="primary", use_container_width=True):
                    do_login("admin", a_user, a_pass)
                    
    html3 = """<div style="text-align: center; margin-top: 60px; padding-top: 25px; border-top: 1px solid rgba(255,255,255,0.1);">
<p style="font-size: 13px; opacity: 0.5;">
Protected by Supabase Auth & Google Cloud infrastructure.<br>
Emergency/Lifeline: 1066 | Phone: 08573-283220
</p>
</div>"""
    st.markdown(html3, unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Login - Agentic AI in Healthcare", page_icon="🏥", layout="wide")
    render_login_page()
