import streamlit as st
import time

# Configuración inicial de la página (Debe ser la primera línea)
st.set_page_config(page_title="BBO HUB CALIDAD", page_icon="🍺", layout="wide", initial_sidebar_state="collapsed")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- CSS GENERAL (Tema Dark Neón) ---
st.markdown("""
    <style>
    body {background-color: #050505; color: #e0e0e0; font-family: 'Space Grotesk', sans-serif;}
    .stApp {background-color: #050505;}
    
    /* Diseño del panel de Login */
    .login-box {
        background-color: #0a0a0a;
        padding: 40px;
        border-radius: 10px;
        border: 1px solid #1a1a1a;
        box-shadow: 0 0 20px rgba(163, 255, 0, 0.1);
        text-align: center;
        max-width: 400px;
        margin: 50px auto;
    }
    
    /* Botones Neón */
    .stButton > button { background-color: #050505 !important; color: #a3ff00 !important; border: 1px solid #a3ff00 !important; border-radius: 6px !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100%; padding: 10px !important; }
    .stButton > button:hover { background-color: #a3ff00 !important; color: #050505 !important; box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important; transform: translateY(-2px) !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛑 PANTALLA DE LOGIN (Si no está autenticado)
# ==========================================
if not st.session_state['autenticado']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
            <div class='login-box'>
                <h1 style='color: #a3ff00; letter-spacing: 2px; margin-bottom: 5px;'>BBO HUB</h1>
                <p style='color: #888888; font-size: 0.9rem; margin-bottom: 30px;'>CONTROL CENTRAL DE CALIDAD</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Formulario de Ingreso
        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="Ingresa tu usuario...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submit = st.form_submit_button("INGRESAR AL SISTEMA")
            
            if submit:
                # Verificar credenciales en los Secretos de Streamlit
                try:
                    if usuario in st.secrets["passwords"] and st.secrets["passwords"][usuario] == password:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_actual'] = usuario
                        st.success("¡Acceso Concedido! Iniciando sistemas...")
                        time.sleep(1)
                        st.rerun() # Recarga la página para mostrar el HUB
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")
                except Exception as e:
                    st.error("⚠️ Error crítico: No se encontró la Bóveda de Secretos configurada en Streamlit Cloud.")

# ==========================================
# 🟢 DASHBOARD PRINCIPAL (Si está autenticado)
# ==========================================
else:
    # --- MENÚ LATERAL (SIDEBAR) ---
    st.sidebar.markdown(f"<div style='text-align: center; color: #a3ff00; font-weight: bold; margin-bottom: 20px;'>👤 USUARIO: {st.session_state['usuario_actual'].upper()}</div>", unsafe_allow_html=True)
    
    st.sidebar.page_link("pages/CONTROL_CALIDAD.py", label="🔬 CONTROL DE CALIDAD", icon="📊")
    st.sidebar.page_link("pages/3_ESTADIA_TANQUES.py", label="⏱️ ESTADÍA DE TANQUES", icon="⏳")
    
    st.sidebar.markdown("<br><hr style='border: 1px solid #1a1a1a;'><br>", unsafe_allow_html=True)
    
    # Botón de Cerrar Sesión
    if st.sidebar.button("🔴 CERRAR SESIÓN"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- CONTENIDO PRINCIPAL ---
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; letter-spacing: 2px; color: #ffffff;'>BBO <span style='color: #a3ff00;'>HUB</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 1.2rem; margin-bottom: 3rem;'>CENTRO DE CONTROL Y MONITOREO DE CALIDAD</p>", unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("<h3 style='color: #a3ff00;'>MÓDULOS ACTIVOS</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**🔬 Control de Calidad:** Monitoreo estadístico de parámetros fisicoquímicos.")
    with col2:
        st.warning("**⏱️ Estadía de Tanques:** Control de tiempos de residencia y alertas tempranas.")