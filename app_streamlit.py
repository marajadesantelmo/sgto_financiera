import streamlit as st
from app_operaciones_usd import show_page_operaciones
from app_sgto_caja import show_page_caja
from supabase_connection import login_user, logout_user

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Operaciones Financieras",
    page_icon="📊",
    layout="wide"
)

# Inicialización de estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
 

def handle_logout():
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    logout_user()

# Página de login
if not st.session_state['authenticated']:
    st.title("🔐 Acceso al Sistema")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar Sesión")

    if submitted:
        try:
            user = login_user(email, password)
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                st.success('Login exitoso!')
                st.rerun()
            else:
                st.error('Credenciales incorrectas')
        except Exception as e:
            st.error(f'Error al iniciar sesión: {str(e)}')

else:
    st.sidebar.button("Cerrar Sesión", on_click=handle_logout)
    st.sidebar.info(f"Usuario: {st.session_state['user'].email}")

    st.sidebar.markdown("---")
    selected_page = st.sidebar.radio(
        "Seleccionar página",
        ("Operaciones USD", "Seguimiento Caja")
    )

    if selected_page == "Operaciones USD":
        show_page_operaciones()
    else:
        show_page_caja()
