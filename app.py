import streamlit as st
import os
from utils.core import aplicar_estilo_neon

# Configuración inicial de la página
st.set_page_config(page_title="HUB BBO CALIDAD", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Aplica la tipografía y el fondo base
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

    /* 3. Ajuste de posición del botón de Cerrar Sesión en el fondo del Sidebar */
    [data-testid="stSidebar"] {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] {
        margin-top: auto !important;
        padding-bottom: 20px !important;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background-color: transparent !important;
        border: 1px solid #1a1a1a !important;
        width: fit-content !important;
        padding: 6px 14px !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button p {
        color: #555555 !important;
        font-size: 0.75rem !important;
        margin: 0 !important;
        font-weight: bold !important;
        letter-spacing: 1px;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #f87171 !important;
        background-color: rgba(248, 113, 113, 0.1) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p {
        color: #f87171 !important;
    }

    /* 4. Estilizado Neón idéntico a las Tarjetas de la Derecha */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        padding: 28px 24px !important;
        border-radius: 12px !important;
        text-align: left !important;
        min-height: 220px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        border-color: #333333 !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        transform: translateY(-4px) !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
        text-align: left !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛑 PANTALLA DE LOGIN
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
            # ENCABEZADO LOGIN
            st.markdown("""
                <div style='display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 10px;'>
                    <span style='color: #a3ff00; font-size: 2.8rem; font-weight: 800; letter-spacing: 4px; font-family: "Space Grotesk", sans-serif;'>HUB</span>
                    <img src='https://raw.githubusercontent.com/aespada/hub-calidad/main/LogoBBO.png' style='height: 55px; object-fit: contain;' onerror="this.style.display='none'">
                </div>
                <p style='text-align: center; color: #888888; font-size: 0.85rem; letter-spacing: 2px; margin-bottom: 2.5rem; font-family: "Space Grotesk", sans-serif;'>CENTRO DE CONTROL Y MONITOREO</p>
            """, unsafe_allow_html=True)
            
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
# 🟢 DASHBOARD PRINCIPAL
# ==========================================
else:
    # --- SIDEBAR ---
    st.sidebar.markdown(f"""
        <div style='background-color: #050505; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 25px;'>
            <span style='color: #888888; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;'>Sesión Activa</span><br>
            <span style='color: #a3ff00; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>■ {st.session_state['usuario_actual'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Espaciador para empujar el botón de Cerrar Sesión al fondo absoluto del sidebar
    st.sidebar.markdown("<br>" * 18, unsafe_allow_html=True)
    
    if st.sidebar.button("■ CERRAR SESIÓN"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- ENCABEZADO CENTRAL (HUB BBO en la misma línea) ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Intentamos cargar la imagen local LogoBBO.png si existe
    logo_path = "LogoBBO.png"
    logo_exists = os.path.exists(logo_path)
    
    st.markdown(f"""
        <div style='display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 5px;'>
            <span style='color: #a3ff00; font-size: 4rem; font-weight: 800; letter-spacing: 6px; font-family: "Space Grotesk", sans-serif; line-height: 1;'>HUB</span>
            {'<img src="LogoBBO.png" style="height: 75px; object-fit: contain;">' if logo_exists else '<span style="color: #ffffff; font-size: 4rem; font-weight: 800; letter-spacing: 6px;">BBO</span>'}
        </div>
        <p style='text-align: center; color: #888888; font-size: 1rem; letter-spacing: 3px; margin-bottom: 3.5rem; text-transform: uppercase; font-family: "Space Grotesk", sans-serif;'>Centro de Control y Monitoreo</p>
    """, unsafe_allow_html=True)

    # --- CUADRÍCULA DE TARJETAS NEÓN ---
    col1, col2 = st.columns(2)
    
    # TEXTOS DE LAS TARJETAS (FORMATO EXACTO AL PANEL DE CALIDAD)
    txt_cc = "///\n\nControl de Calidad\n\nAnálisis SPC, tendencias y resumen de producción mensual.\n\n\n■ MÓDULO ACTIVO"
    txt_est = "///\n\nControl de Estadía\n\nMonitoreo de tiempos de residencia de tanques para Malta y Cervezas.\n\n\n■ MÓDULO ACTIVO"
    txt_elab = "///\n\nElaboración\n\nControl de procesos de cocimiento, fermentación y filtración. Mermas y eficiencias.\n\n\n■ EN DESARROLLO"
    txt_env = "///\n\nEnvasado\n\nSupervisión de líneas de llenado, mermas de empaque y eficiencias de turno (OEE).\n\n\n■ EN DESARROLLO"

    with col1:
        if st.button(txt_cc, use_container_width=True, key="card_cc"):
            st.switch_page("pages/CONTROL_CALIDAD.py")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button(txt_elab, use_container_width=True, key="card_elab"):
            try:
                st.switch_page("pages/ELABORACION.py")
            except:
                st.warning("🚧 Módulo de Elaboración en desarrollo.")

    with col2:
        if st.button(txt_est, use_container_width=True, key="card_est"):
            st.switch_page("pages/3_ESTADIA_TANQUES.py")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button(txt_env, use_container_width=True, key="card_env"):
            try:
                st.switch_page("pages/ENVASADO.py")
            except:
                st.warning("🚧 Módulo de Envasado en desarrollo.")
        
    st.markdown("<br><br><hr style='border: 1px solid #1a1a1a; margin-top: 2rem;'><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #333333; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-family: \"Space Grotesk\", sans-serif;'>BBO Cervecería © 2026 - Departamento de Calidad</p>", unsafe_allow_html=True)