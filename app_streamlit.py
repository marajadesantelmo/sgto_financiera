import streamlit as st
import extra_streamlit_components as stx
from app_operaciones_usd import show_page_operaciones
from app_sgto_caja import show_page_caja
from app_analisis_clientes import show_page_analisis_clientes
from supabase_connection import login_user, logout_user
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Operaciones Financieras",
    page_icon="📊",
    layout="wide"
)

# Initialize cookie manager
cookie_manager = stx.CookieManager(key='sgto_financiera_cookies')

# Cookie configuration
COOKIE_EMAIL_KEY = 'saved_email'
COOKIE_PASSWORD_KEY = 'saved_password'
COOKIE_EXPIRES_AT = datetime.utcnow() + timedelta(days=3650)  # ~10 years

# Inicialización de estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'auto_login_attempted' not in st.session_state:
    st.session_state['auto_login_attempted'] = False

# Retrieve cookies every run
raw_cookies = cookie_manager.get_all()
cookies_ready = raw_cookies is not None
cookies = raw_cookies or {}

# Auto-login using stored credentials once cookies are ready
if (
    cookies_ready
    and not st.session_state['authenticated']
    and not st.session_state['auto_login_attempted']
):
    saved_email = cookies.get(COOKIE_EMAIL_KEY)
    saved_password = cookies.get(COOKIE_PASSWORD_KEY)

    if saved_email and saved_password:
        try:
            user = login_user(saved_email, saved_password)
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                st.session_state['auto_login_attempted'] = True
                st.rerun()
            else:
                st.session_state['auto_login_attempted'] = True
        except Exception:
            st.session_state['auto_login_attempted'] = True
            try:
                cookie_manager.delete(COOKIE_EMAIL_KEY, key='auto_delete_email')
                cookie_manager.delete(COOKIE_PASSWORD_KEY, key='auto_delete_password')
            except Exception:
                pass
    else:
        st.session_state['auto_login_attempted'] = True

def handle_logout():
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.session_state['auto_login_attempted'] = False
    logout_user()
    # Clear cookies on logout
    try:
        cookie_manager.delete(COOKIE_EMAIL_KEY, key='logout_delete_email')
        cookie_manager.delete(COOKIE_PASSWORD_KEY, key='logout_delete_password')
    except:
        pass
    st.rerun()

# Página de login
if not st.session_state['authenticated']:
    st.title("🔐 Acceso al Sistema")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        remember_me = st.checkbox("Recordar mis credenciales", value=True)
        submitted = st.form_submit_button("Iniciar Sesión")

    if submitted:
        try:
            user = login_user(email, password)
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                
                # Save credentials in cookies if "Remember me" is checked
                if remember_me:
                    try:
                        cookie_manager.set(
                            COOKIE_EMAIL_KEY,
                            email,
                            expires_at=COOKIE_EXPIRES_AT,
                            key='login_set_email',
                        )
                        cookie_manager.set(
                            COOKIE_PASSWORD_KEY,
                            password,
                            expires_at=COOKIE_EXPIRES_AT,
                            key='login_set_password',
                        )
                    except Exception:
                        pass
                
                st.success('Login exitoso!')
                st.rerun()
            else:
                st.error('Credenciales incorrectas')
        except Exception as e:
            st.error(f'Error al iniciar sesión: {str(e)}')

else:
    NAV_ITEMS = {
        "Operaciones USD": {
            "icon": "💱",
        },
        "Seguimiento Caja": {
            "icon": "💰",
        },
        "Análisis Clientes": {
            "icon": "👥",
        },
    }

    if "selected_page" not in st.session_state:
        st.session_state["selected_page"] = "Operaciones USD"

    sidebar_css = """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101e3a 0%, #142542 55%, #1c2f53 100%);
        color: #f5f7ff;
    }
    [data-testid="stSidebar"] * {
        color: #f5f7ff !important;
    }
    .user-card {
        border: 1px solid rgba(255, 255, 255, 0.18);
        background: rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 18px;
    }
    .user-card .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 10px;
    }
    .user-card .meta {
        display: flex;
        flex-direction: column;
        gap: 2px;
        font-size: 0.85rem;
    }
    .nav-wrapper {
        border-radius: 16px;
        padding: 14px 12px;
        background: rgba(0, 0, 0, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .nav-wrapper h3 {
        font-size: 0.95rem;
        margin-bottom: 12px;
        letter-spacing: 0.02em;
    }
    .nav-wrapper div[data-baseweb="radio"] > div {
        gap: 0.45rem;
    }
    .nav-wrapper div[data-baseweb="radio"] label {
        border: 1px solid rgba(255, 255, 255, 0.18);
        background: rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.65rem 0.75rem;
        transition: all 0.2s ease;
    }
    .nav-wrapper div[data-baseweb="radio"] label:hover {
        border-color: rgba(255, 255, 255, 0.35);
        background: rgba(255, 255, 255, 0.12);
    }
    .nav-wrapper div[data-baseweb="radio"] input:checked + div {
        border: 1px solid #7aa5ff;
        background: rgba(122, 165, 255, 0.16);
        box-shadow: 0 0 0 1px rgba(122, 165, 255, 0.3);
    }
    .nav-wrapper .nav-caption {
        margin-top: 10px;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.75) !important;
    }
    </style>
    """
    st.sidebar.markdown(sidebar_css, unsafe_allow_html=True)

    user_email = getattr(st.session_state["user"], "email", "Usuario")
    user_initials = user_email[:2].upper()
    with st.sidebar:
        st.markdown(
            f"""
            <div class="user-card">
                <div style="display:flex; align-items:center;">
                    <div class="avatar">{user_initials}</div>
                    <div class="meta">
                        <span style="font-weight:600;">{user_email}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    nav_container = st.sidebar.container()
    with nav_container:      
        for title, item in NAV_ITEMS.items():
            is_selected = st.session_state['selected_page'] == title
            button_class = "nav-button selected" if is_selected else "nav-button"
            
            button_html = f"""
            <div class="{button_class}" onclick="selectPage('{title}')">
                <span class="nav-icon">{item['icon']}</span>
                <span class="nav-title">{title}</span>
            </div>
            """
            
            if st.button(f"{item['icon']}  {title}", key=f"nav_{title}", use_container_width=True):
                st.session_state['selected_page'] = title
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add custom CSS for button styling
        st.markdown("""
        <style>
        .nav-wrapper .stButton > button {
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            background: rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px !important;
            padding: 0.75rem 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
            margin-bottom: 8px !important;
            color: #f5f7ff !important;
            font-weight: 500 !important;
        }
        
        .nav-wrapper .stButton > button:hover {
            border-color: rgba(255, 255, 255, 0.35) !important;
            background: rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
            transform: translateY(-1px) !important;
        }
        
        .nav-wrapper .stButton > button:focus {
            border: 1px solid #7aa5ff !important;
            background: rgba(122, 165, 255, 0.16) !important;
            box-shadow: 0 0 0 2px rgba(122, 165, 255, 0.3), 0 4px 16px rgba(0, 0, 0, 0.25) !important;
        }
        </style>
        """, unsafe_allow_html=True)

    selected_page = st.session_state['selected_page']

    if selected_page == "Operaciones USD":
        show_page_operaciones()
    elif selected_page == "Seguimiento Caja":
        show_page_caja()
    else:  # Análisis Clientes
        show_page_analisis_clientes()

    st.markdown("<hr style='margin-top:3rem;'>", unsafe_allow_html=True)
    _, logout_col, _ = st.columns([1, 2, 1])
    with logout_col:
        st.button("Cerrar Sesión", on_click=handle_logout, use_container_width=True)
