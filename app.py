import streamlit as st
from utils.core import aplicar_estilo_neon

# Configuración inicial de la página
st.set_page_config(page_title="HUB BBO CALIDAD", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Aplica la tipografía y el fondo base
aplicar_estilo_neon()

# --- CSS GLOBAL: BLINDAJE DARK NEÓN FUTURISTA ---
st.markdown("""
    <style>
    /* Tipografía Global */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap');
    
    /* 1. FORZAR MODO OSCURO ABSOLUTO (Anti-Tema Claro) */
    html, body, [class*="css"], .stApp {
        font-family: 'Space Grotesk', sans-serif !important;
        background-color: #030303 !important;
        color: #e0e0e0 !important;
    }
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #080808 !important;
        border-right: 1px solid #1a1a1a !important;
    }
    [data-testid="stSidebarNav"] {display: none !important;}
    
    /* 2. FORZAR BOTÓN DE CERRAR SESIÓN AL FONDO DEL SIDEBAR */
    [data-testid="stSidebar"] > div:first-child {
        display: flex !important;
        flex-direction: column !important;
        height: 100vh !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] {
        margin-top: auto !important;
        padding-bottom: 25px !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        width: auto !important;
        padding: 6px 14px !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
        color: #666666 !important;
        font-size: 0.75rem !important;
        margin: 0 !important;
        font-weight: bold !important;
        letter-spacing: 1px;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #f87171 !important;
        background-color: rgba(248, 113, 113, 0.05) !important;
        box-shadow: 0 0 10px rgba(248, 113, 113, 0.2) !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p {
        color: #f87171 !important;
    }

    /* 3. TARJETAS MÓDULOS (DISEÑO FUTURISTA) */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background: linear-gradient(145deg, #0a0a0a, #050505) !important;
        border: 1px solid #1a1a1a !important;
        padding: 28px 24px !important;
        border-radius: 12px !important;
        min-height: 220px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        text-align: left !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5), -5px -5px 15px rgba(255,255,255,0.02) !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        border-color: #a3ff00 !important;
        background: #0d0d0d !important;
        box-shadow: 0 0 25px rgba(163, 255, 0, 0.15), inset 0 0 10px rgba(163, 255, 0, 0.05) !important;
        transform: translateY(-4px) !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p {
        font-family: 'Space Grotesk', sans-serif !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
        text-align: left !important;
        width: 100% !important;
        color: #aaaaaa !important;
        line-height: 1.5 !important;
    }
    /* El truco mágico: Las barritas '///' se pintan solas de neón */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p::first-line {
        color: #a3ff00 !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        letter-spacing: 3px !important;
    }

    /* 4. Botón de Login Form */
    div[data-testid="stFormSubmitButton"] > button { 
        background-color: #0a0a0a !important; 
        border: 1px solid #a3ff00 !important; 
        border-radius: 6px !important; 
        transition: all 0.3s ease !important; 
        width: 100% !important; 
        padding: 0.8rem 1rem !important; 
    }
    div[data-testid="stFormSubmitButton"] > button p { 
        color: #a3ff00 !important; 
        font-weight: 600 !important; 
        font-size: 1rem !important; 
        letter-spacing: 1px !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #a3ff00 !important; 
        box-shadow: 0 0 15px rgba(163,255,0,0.3) !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover p { 
        color: #000000 !important; 
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
            background: linear-gradient(145deg, #0a0a0a, #050505) !important;
            padding: 3rem 2.5rem !important; 
            box-shadow: 0 15px 40px rgba(0,0,0,0.9), 0 0 20px rgba(163,255,0,0.05) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <span style='color: #a3ff00; font-size: 3.2rem; font-weight: 800; letter-spacing: 5px;'>HUB <span style="color: #ffffff;">BBO</span></span>
                    <p style='color: #666666; font-size: 0.85rem; letter-spacing: 3px; margin-top: 5px;'>CENTRO DE CONTROL Y MONITOREO</p>
                </div>
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
        <div style='background-color: #080808; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center;'>
            <span style='color: #666666; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;'>Sesión Activa</span><br>
            <span style='color: #a3ff00; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>■ {st.session_state['usuario_actual'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("■ CERRAR SESIÓN"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- ENCABEZADO CENTRAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; margin-bottom: 5px;'>
            <span style='color: #a3ff00; font-size: 4rem; font-weight: 800; letter-spacing: 8px; text-shadow: 0 0 20px rgba(163,255,0,0.3);'>HUB </span>
            <span style='color: #ffffff; font-size: 4rem; font-weight: 800; letter-spacing: 8px;'>BBO</span>
        </div>
        <p style='text-align: center; color: #666666; font-size: 0.95rem; letter-spacing: 4px; margin-bottom: 3.5rem; text-transform: uppercase;'>Centro de Control y Monitoreo</p>
    """, unsafe_allow_html=True)

    # --- CUADRÍCULA DE TARJETAS (TEXTOS LIMPIOS, SIN MARKDOWN) ---
    col1, col2 = st.columns(2)
    
    txt_cc = "///\nCONTROL DE CALIDAD\n\nAnálisis SPC, tendencias, estadía de tanques y resumen de producción mensual."
    txt_elab = "///\nELABORACIÓN\n\nControl de procesos de cocimiento, fermentación y filtración. Mermas y eficiencias."
    txt_env = "///\nENVASADO\n\nSupervisión de líneas de llenado, mermas de empaque y eficiencias de turno (OEE)."
    txt_mant = "///\nMANTENIMIENTO\n\nGestión de órdenes de trabajo, paradas de planta, confiabilidad y repuestos."

    with col1:
        if st.button(txt_cc, use_container_width=True, key="card_cc"):
            st.switch_page("pages/CONTROL_CALIDAD.py")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(163,255,0,0.05); color: #a3ff00; border: 1px solid rgba(163,255,0,0.2); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ MÓDULO ACTIVO</span></div>""", unsafe_allow_html=True)
            
        if st.button(txt_elab, use_container_width=True, key="card_elab"):
            try:
                st.switch_page("pages/ELABORACION.py")
            except:
                st.warning("🚧 Módulo de Elaboración en desarrollo.")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(250,204,21,0.05); color: #facc15; border: 1px solid rgba(250,204,21,0.2); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ EN DESARROLLO</span></div>""", unsafe_allow_html=True)

    with col2:
        if st.button(txt_env, use_container_width=True, key="card_env"):
            try:
                st.switch_page("pages/ENVASADO.py")
            except:
                st.warning("🚧 Módulo de Envasado en desarrollo.")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(250,204,21,0.05); color: #facc15; border: 1px solid rgba(250,204,21,0.2); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ EN DESARROLLO</span></div>""", unsafe_allow_html=True)
            
        if st.button(txt_mant, use_container_width=True, key="card_mant"):
            try:
                st.switch_page("pages/MANTENIMIENTO.py")
            except:
                st.warning("🚧 Módulo de Mantenimiento en desarrollo.")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(250,204,21,0.05); color: #facc15; border: 1px solid rgba(250,204,21,0.2); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ EN DESARROLLO</span></div>""", unsafe_allow_html=True)
        
    st.markdown("<br><hr style='border: 1px solid #1a1a1a; margin-top: 1rem;'><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #444444; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px;'>BBO Cervecería © 2026 - Departamento de Calidad</p>", unsafe_allow_html=True)