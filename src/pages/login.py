import streamlit as st
import base64
import os

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

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
                from src.services.supabase_client import supabase
                st.session_state["patient_id"] = "P001"
                try:
                    p001_res = supabase.table("patients").select("id").eq("patient_id", "P001").execute()
                    st.session_state["patient_uuid"] = p001_res.data[0]["id"] if p001_res.data else "fallback-uuid"
                except:
                    st.session_state["patient_uuid"] = "fallback-uuid"
                st.query_params["auth_role"] = "patient"
        except:
            from src.services.supabase_client import supabase
            st.session_state["patient_id"] = "P001"
            try:
                p001_res = supabase.table("patients").select("id").eq("patient_id", "P001").execute()
                st.session_state["patient_uuid"] = p001_res.data[0]["id"] if p001_res.data else "fallback-uuid"
            except:
                st.session_state["patient_uuid"] = "fallback-uuid"
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
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        background-color: #ffffff;
        color: #0f172a;
        padding: 12px 0;
        border-radius: 6px;
        text-decoration: none;
        font-size: 15px;
        font-weight: 600;
        border: 1px solid #e2e8f0;
        transition: background-color 0.2s, border-color 0.2s;
        font-family: 'Inter', sans-serif;
    " onmouseover="this.style.backgroundColor='#f8fafc'; this.style.borderColor='#cbd5e1';" 
       onmouseout="this.style.backgroundColor='#ffffff'; this.style.borderColor='#e2e8f0';"
       onclick="if('{target_url}' === '#') {{ alert('Google Auth is not configured yet!'); return false; }}">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="20" height="20" style="margin-right: 12px;">
        Continue with Google
    </a>
    """
    st.markdown(btn_html, unsafe_allow_html=True)

def render_login_page():
    initialize_session()
    
    css = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Full Page Setup */
.stApp {{
    background: linear-gradient(rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.9)), 
                url("https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80") center/cover no-repeat fixed;
    font-family: 'Inter', sans-serif !important;
}}

header[data-testid="stHeader"], footer {{ display: none !important; }}

/* Left Side Branding (Injected via Markdown) */
.left-branding {{
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: 55%;
    padding: 10vh 8%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: white;
    z-index: 5;
    pointer-events: none;
}}
.left-branding h1 {{ font-size: 48px; font-weight: 800; line-height: 1.1; margin-bottom: 20px; letter-spacing: -1px; }}
.left-branding p {{ font-size: 20px; font-weight: 400; color: #cbd5e1; max-width: 480px; line-height: 1.5; }}
.brand-logo {{ display: flex; align-items: center; margin-bottom: 60px; }}
.brand-logo svg {{ width: 32px; height: 32px; margin-right: 12px; color: #38bdf8; }}
.brand-logo span {{ font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}

/* Right Side Form Container */
.block-container {{
    position: fixed !important;
    right: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    width: 45% !important;
    max-width: 650px !important;
    background: #ffffff !important;
    padding: 8vh 10% !important;
    box-shadow: -20px 0 50px rgba(0,0,0,0.3);
    overflow-y: auto;
    z-index: 10;
}}

/* Clean Enterprise Typography */
.auth-title {{ color: #0f172a; font-size: 32px; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px; }}
.auth-subtitle {{ color: #64748b; font-size: 16px; margin-bottom: 40px; font-weight: 400; }}

/* Minimalist Tabs (Segmented Control Style) */
div[data-testid="stTabs"] button[data-baseweb="tab"], 
div[data-testid="stTabs"] button[id^="tabs-"],
.stTabs button {{
    flex: 1 1 0 !important;
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    color: #64748b !important; 
    font-weight: 600 !important; 
    padding: 12px 10px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    margin: 0 5px !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"],
.stTabs button[aria-selected="true"] {{
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #0f172a !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}}
div[data-testid="stTabs"] button:hover,
.stTabs button:hover {{
    border-color: #94a3b8 !important;
}}

/* Hide Streamlit Native Tab Underlines / Tracks */
div[data-testid="stTabs"] [data-baseweb="tab-border"],
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-highlight"] {{ 
    display: none !important; 
}}
div[data-testid="stTabs"] div[style*="border-bottom"],
.stTabs div[style*="border-bottom"] {{ 
    border-bottom: none !important; 
}}

/* Form Inputs - Highly Visible */
.stTextInput > div > div {{
    background-color: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease;
}}
.stTextInput > div > div:focus-within {{
    background-color: #ffffff !important;
    border-color: #0f172a !important;
    box-shadow: 0 0 0 1px #0f172a !important;
}}
.stTextInput > div > div > input {{
    background-color: transparent !important;
    border: none !important;
    color: #0f172a !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}}

/* Checkbox and Link Styling */
.stCheckbox {{ margin-top: 5px !important; margin-bottom: 5px !important; }}
.stCheckbox label p {{ color: #64748b !important; font-size: 14px !important; font-weight: 500 !important; }}
.forgot-link {{ text-align: right; margin-top: 10px; font-size: 14px; font-weight: 500; }}
.forgot-link a {{ color: #0f172a; text-decoration: none; transition: color 0.2s; }}
.forgot-link a:hover {{ color: #2563eb; text-decoration: underline; }}

/* Minimal Radio */
.stRadio label {{ color: #475569 !important; font-weight: 500 !important; }}
.stRadio {{ margin-bottom: 5px !important; }}

/* Primary Button */
div[data-testid="stButton"] button[kind="primary"] {{
    background-color: #0f172a !important; 
    color: white !important; border: none !important;
    border-radius: 6px !important; font-weight: 600 !important; font-size: 15px !important;
    padding: 12px 0 !important; width: 100% !important;
    transition: background-color 0.2s !important;
}}
div[data-testid="stButton"] button[kind="primary"]:hover {{ background-color: #1e293b !important; }}

/* Divider */
.divider {{ display: flex; align-items: center; text-align: center; margin: 25px 0; color: #94a3b8; font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }}
.divider::before, .divider::after {{ content: ''; flex: 1; border-bottom: 1px solid #f1f5f9; }}
.divider:not(:empty)::before {{ margin-right: 15px; }}
.divider:not(:empty)::after {{ margin-left: 15px; }}

/* Remove streamlt spacing */
div[data-testid="stForm"] {{ padding: 0 !important; border: none !important; margin: 0 !important; }}
[data-testid="stVerticalBlock"] {{ gap: 15px !important; }}
</style>"""
    st.markdown(css, unsafe_allow_html=True)
    
    # Left Branding (Absolute Positioned via CSS)
    left_html = """
    <div class="left-branding">
        <div class="brand-logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            <span>Apollo Aragonda</span>
        </div>
        <h1>Intelligent healthcare,<br>built for the future.</h1>
        <p>Access your medical records, manage appointments, and connect with your care team through our secure AI-driven portal.</p>
    </div>
    """
    st.markdown(left_html, unsafe_allow_html=True)
    
    # Right Form Container
    st.markdown('<div class="auth-title">Log in</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Welcome back to your secure portal.</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Patient", "Doctor", "Clinical Staff"])
    
    with tab1:
        if st.session_state["otp_sent_to"]:
            st.info(f"📧 Code sent to **{st.session_state['otp_sent_to']}**")
            with st.form("otp_verify_form", clear_on_submit=False, border=False):
                otp_code = st.text_input("Enter 6-digit Code", placeholder="123456", label_visibility="collapsed")
                if st.form_submit_button("Verify & Sign In", type="primary", use_container_width=True):
                    do_otp_verify("patient", st.session_state["otp_sent_to"], otp_code)
            if st.button("Cancel", type="secondary", use_container_width=True):
                st.session_state["otp_sent_to"] = None
                st.rerun()
        else:
            mode = st.radio("Login Method", ["Password", "Magic Link"], horizontal=True, label_visibility="collapsed")
            if mode == "Password":
                with st.form("patient_login_form", clear_on_submit=False, border=False):
                    p_user = st.text_input("Email / ID", placeholder="jaajitha@gmail.com", label_visibility="collapsed")
                    p_pass = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.checkbox("Remember me", value=True, key="p_rem")
                    with c2:
                        st.markdown('<div class="forgot-link"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)
                        
                    if st.form_submit_button("Sign in", type="primary", use_container_width=True):
                        do_login("patient", p_user, p_pass)
            else:
                with st.form("otp_request_form", clear_on_submit=False, border=False):
                    otp_email = st.text_input("Email Address", placeholder="jaajitha@gmail.com", label_visibility="collapsed")
                    if st.form_submit_button("Send Magic Link", type="primary", use_container_width=True):
                        do_otp_request(otp_email)
            st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)
            render_google_button()
            
    with tab2:
        with st.form("doctor_login_form", clear_on_submit=False, border=False):
            d_user = st.text_input("Work Email", placeholder="provider@apollo.com", label_visibility="collapsed")
            d_pass = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.checkbox("Remember me", value=True, key="d_rem")
            with c2:
                st.markdown('<div class="forgot-link"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)
                
            if st.form_submit_button("Sign in to Workspace", type="primary", use_container_width=True):
                do_login("doctor", d_user, d_pass)
        st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)
        render_google_button()

    with tab3:
        with st.form("admin_login_form", clear_on_submit=False, border=False):
            a_user = st.text_input("Admin Username", placeholder="admin.workspace", label_visibility="collapsed")
            a_pass = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            if st.form_submit_button("Access Console", type="primary", use_container_width=True):
                do_login("admin", a_user, a_pass)

if __name__ == "__main__":
    st.set_page_config(page_title="Login - Apollo Hospitals", page_icon="🏥", layout="wide")
    render_login_page()
