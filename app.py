import streamlit as st
import os
from utils.core import aplicar_estilo_neon

# Configuración inicial de la página
st.set_page_config(page_title="BBO HUB CALIDAD", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Aplica la tipografía y el fondo base de nuestra librería
aplicar_estilo_neon()

# --- CSS GLOBAL DE ALTA GAMA ---
st.markdown("""
    <style>
    /* 1. Destructor total del menú feo por defecto de Streamlit */
    [data-testid="stSidebarNav"] {display: none !important;}
    
    /* 2. Botón de Iniciar Sesión (Login) */
    div[data-testid="stFormSubmitButton"] > button { 
        background-color: #050505 !important; 
        border: 1px solid #a3ff00 !important; 
        border-radius: 6px !important; 
        transition: all 0.3s ease !important; 
        width: 100% !important; 
        padding: 0.8rem 1rem !important; 
    }
    div[data-testid="stFormSubmitButton"] > button p { 
        color: #a3ff00 !important; 
        font-weight: 600 !important; 
        font-family: 'Space Grotesk', sans-serif !important; 
        font-size: 1rem !important; 
        margin: 0 !important;
        letter-spacing: 1px;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #a3ff00 !important; 
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important; 
        transform: translateY(-2px) !important; 
    }
    div[data-testid="stFormSubmitButton"] > button:hover p { 
        color: #050505 !important; 
    }

    /* 3. Botón de Cerrar Sesión (Pequeño, inferior izquierdo) */
    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background-color: transparent !important;
        border: 1px solid #1a1a1a !important;
        width: fit-content !important;
        padding: 4px 12px !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button p {
        color: #555555 !important;
        font-size: 0.75rem !important;
        margin: 0 !important;
        font-weight: bold !important;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #f87171 !important;
        background-color: rgba(248, 113, 113, 0.1) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p {
        color: #f87171 !important;
    }

    /* 4. Estilos para los Módulos/Tarjetas Clickables */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        padding: 25px 20px !important;
        border-radius: 12px !important;
        text-align: left !important;
        min-height: 180px !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        border-color: #a3ff00 !important;
        box-shadow: 0 10px 30px rgba(163, 255, 0, 0.05) !important;
        transform: translateY(-5px) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛑 PANTALLA DE LOGIN (Modo Bloqueo)
# ==========================================
if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
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
        with st.form("login_form"):
            col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
            with col_l2:
                if os.path.exists("LogoBBO.png"):
                    st.image("LogoBBO.png", use_container_width=True)
                else:
                    st.markdown("<h3 style='text-align: center; color: #a3ff00;'>BBO</h3>", unsafe_allow_html=True)
                    
            st.markdown("<h1 style='text-align: center; color: #a3ff00; font-size: 2.5rem; letter-spacing: 5px; margin-top: -15px; margin-bottom: 0;'>HUB</h1>", unsafe_allow_html=True)
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
                        st.rerun() 
                    else:
                        st.error("Credenciales incorrectas. Acceso denegado.")
                except Exception as e:
                    st.error("Error crítico: La Bóveda de Secretos no está configurada en Streamlit Cloud.")

# ==========================================
# 🟢 DASHBOARD PRINCIPAL (Modo Acceso)
# ==========================================
else:
    # --- SIDEBAR ---
    st.sidebar.markdown(f"""
        <div style='background-color: #050505; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 25px;'>
            <span style='color: #888888; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;'>Sesión Activa</span><br>
            <span style='color: #a3ff00; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>■ {st.session_state['usuario_actual'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<br>" * 15, unsafe_allow_html=True)
    
    if st.sidebar.button("■ CERRAR SESIÓN"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- CONTENIDO PRINCIPAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_d1, col_d2, col_d3 = st.columns([1.5, 1, 1.5])
    with col_d2:
        if os.path.exists("LogoBBO.png"):
            st.image("LogoBBO.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #a3ff00;'>BBO</h2>", unsafe_allow_html=True)
            
    st.markdown("<h1 style='text-align: center; font-size: 3rem; letter-spacing: 8px; color: #a3ff00; margin-top: -15px; margin-bottom: 0; line-height: 1;'>HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 1rem; letter-spacing: 3px; margin-bottom: 4rem; text-transform: uppercase;'>Centro de Control y Monitoreo</p>", unsafe_allow_html=True)

    # --- CUADRÍCULA DE MÓDULOS ---
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("■ CONTROL DE CALIDAD\n\nPlataforma de monitoreo estadístico avanzado. Analiza tendencias fisicoquímicas en tiempo real, calcula métricas de capacidad (Cp/Cpk) y exporta reportes.", use_container_width=True, key="btn_cc"):
            st.switch_page("pages/CONTROL_CALIDAD.py")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("■ ELABORACIÓN\n\nPanel de control para procesos de cocimiento, fermentación y filtración. Monitoreo de mermas, extractos y eficiencias de sala.", use_container_width=True, key="btn_elab"):
            try:
                st.switch_page("pages/ELABORACION.py")
            except:
                st.warning("🚧 Módulo en construcción.")

    with col2:
        if st.button("■ ESTADÍA DE TANQUES\n\nTablero de seguimiento logístico para tiempos de maduración. Cuenta con sistema dual de alertas tempranas, panel de estado crítico y notificaciones.", use_container_width=True, key="btn_est"):
            st.switch_page("pages/3_ESTADIA_TANQUES.py")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("■ ENVASADO\n\nSupervisión de líneas de llenado, mermas de empaque, control de oxígeno disuelto y eficiencias operativas de turno (OEE).", use_container_width=True, key="btn_env"):
            try:
                st.switch_page("pages/ENVASADO.py")
            except:
                st.warning("🚧 Módulo en construcción.")
        
    st.markdown("<br><br><hr style='border: 1px solid #1a1a1a; margin-top: 2rem;'><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #333333; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'>BBO Cervecería © 2026 - Departamento de Calidad</p>", unsafe_allow_html=True)