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
    
    /* Botones Neón Globales (Aplica también a los formularios) */
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button { 
        background-color: #050505 !important; 
        border: 1px solid #a3ff00 !important; 
        border-radius: 6px !important; 
        transition: all 0.3s ease !important; 
        width: 100% !important; 
        padding: 0.6rem 1rem !important; 
    }
    div[data-testid="stButton"] > button p,
    div[data-testid="stFormSubmitButton"] > button p { 
        color: #a3ff00 !important; 
        font-weight: 600 !important; 
        font-family: 'Space Grotesk', sans-serif !important; 
        font-size: 1rem !important; 
        margin: 0 !important;
    }
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #a3ff00 !important; 
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important; 
        transform: translateY(-2px) !important; 
    }
    div[data-testid="stButton"] > button:hover p,
    div[data-testid="stFormSubmitButton"] > button:hover p { 
        color: #050505 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛑 PANTALLA DE LOGIN (Si no está autenticado)
# ==========================================
if not st.session_state['autenticado']:
    # --- CSS EXCLUSIVO PARA EL LOGIN (Desaparece el Sidebar y estiliza la tarjeta) ---
    st.markdown("""
        <style>
        /* Desaparecer menú lateral por completo */
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        /* Convertir el formulario en una tarjeta Premium */
        [data-testid="stForm"] { 
            border: 1px solid #1a1a1a !important; 
            border-radius: 12px !important; 
            background-color: #0a0a0a !important; 
            padding: 3rem 2.5rem !important; 
            box-shadow: 0 15px 40px rgba(0,0,0,0.9), 0 0 20px rgba(163,255,0,0.03) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # Formulario Integrado
        with st.form("login_form"):
            st.markdown("<h1 style='text-align: center; color: #a3ff00; font-size: 3rem; letter-spacing: 3px; margin-bottom: 0;'>BBO HUB</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #888888; font-size: 0.85rem; letter-spacing: 2px; margin-bottom: 2.5rem;'>CONTROL CENTRAL DE CALIDAD</p>", unsafe_allow_html=True)
            
            usuario = st.text_input("Usuario", placeholder="Ingresa tu ID corporativo...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("ACCEDER AL SISTEMA")
            
            if submit:
                try:
                    if usuario in st.secrets["passwords"] and st.secrets["passwords"][usuario] == password:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_actual'] = usuario
                        st.rerun() # Recarga la página y borra el Login
                    else:
                        st.error("❌ Credenciales incorrectas. Acceso denegado.")
                except Exception as e:
                    st.error("⚠️ Error crítico: La Bóveda de Secretos no está configurada en Streamlit Cloud.")

# ==========================================
# 🟢 DASHBOARD PRINCIPAL (Si está autenticado)
# ==========================================
else:
    # --- MENÚ LATERAL (SIDEBAR) ---
    st.sidebar.markdown(f"""
        <div style='background-color: #0a0a0a; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;'>
            <span style='color: #888888; font-size: 0.8rem; letter-spacing: 1px;'>SESIÓN INICIADA</span><br>
            <span style='color: #a3ff00; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>👤 {st.session_state['usuario_actual'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
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