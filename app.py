import streamlit as st

# Configuración inicial de la página
st.set_page_config(page_title="HUB BBO CALIDAD", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- CSS GLOBAL DE ALTA GAMA (CLON EXACTO DE LOBBY CALIDAD) ---
st.markdown("""
    <style>
    /* Tipografía Global */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif !important;
        background-color: #050505 !important;
        color: #e0e0e0 !important;
    }
    .stApp { background-color: #050505 !important; }

    /* 1. Destructor total del menú feo por defecto de Streamlit */
    [data-testid="stSidebarNav"] {display: none !important;}
    
    /* 2. FORZAR BOTÓN DE CERRAR SESIÓN ABAJO EN EL SIDEBAR */
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
        background-color: transparent !important;
        border: 1px solid #1a1a1a !important;
        width: auto !important;
        padding: 6px 14px !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
        color: #555555 !important;
        font-size: 0.75rem !important;
        margin: 0 !important;
        font-weight: bold !important;
        letter-spacing: 1px;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #f87171 !important;
        background-color: rgba(248, 113, 113, 0.1) !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p {
        color: #f87171 !important;
    }

    /* 3. ESTILO DE TARJETAS IDÉNTICO AL LOBBY DE CALIDAD */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #0a0a0a !important;
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
        transition: all 0.3s ease !important;
        box-shadow: none !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        border-color: #a3ff00 !important;
        background-color: #0d0d0d !important;
        box-shadow: 0 0 20px rgba(163, 255, 0, 0.15) !important;
        transform: translateY(-3px) !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p {
        font-family: 'Space Grotesk', sans-serif !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
        text-align: left !important;
        width: 100% !important;
    }

    /* 4. Botón de Login Form */
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
        font-size: 1rem !important; 
    }
    div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #a3ff00 !important; 
    }
    div[data-testid="stFormSubmitButton"] > button:hover p { 
        color: #050505 !important; 
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
            st.markdown("""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <span style='color: #a3ff00; font-size: 3rem; font-weight: 800; letter-spacing: 5px;'>HUB <span style="color: #ffffff;">BBO</span></span>
                    <p style='color: #888888; font-size: 0.85rem; letter-spacing: 2px; margin-top: 5px;'>CENTRO DE CONTROL Y MONITOREO</p>
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
        <div style='background-color: #050505; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center;'>
            <span style='color: #888888; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;'>Sesión Activa</span><br>
            <span style='color: #a3ff00; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>■ {st.session_state['usuario_actual'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("■ CERRAR SESIÓN"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- ENCABEZADO CENTRAL (HUB BBO TEXTO PURO) ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; margin-bottom: 5px;'>
            <span style='color: #a3ff00; font-size: 4rem; font-weight: 800; letter-spacing: 8px;'>HUB </span>
            <span style='color: #ffffff; font-size: 4rem; font-weight: 800; letter-spacing: 8px;'>BBO</span>
        </div>
        <p style='text-align: center; color: #888888; font-size: 0.95rem; letter-spacing: 3px; margin-bottom: 3.5rem; text-transform: uppercase;'>Centro de Control y Monitoreo</p>
    """, unsafe_allow_html=True)

    # --- CUADRÍCULA DE TARJETAS TIPO LOBBY CALIDAD ---
    col1, col2 = st.columns(2)
    
    # ESTRUCTURA DE TEXTO CON FORMATO HTML INTEGRADO
    txt_cc = ":green[///]\n\n### **Control de Calidad**\n\n:gray[Análisis SPC, tendencias, estadía de tanques y resumen de producción.]\n\n"
    txt_elab = ":green[///]\n\n### **Elaboración**\n\n:gray[Control de procesos de cocimiento, fermentación y filtración. Mermas y eficiencias.]\n\n"
    txt_env = ":green[///]\n\n### **Envasado**\n\n:gray[Supervisión de líneas de llenado, mermas de empaque y eficiencias de turno (OEE).]\n\n"
    txt_mant = ":green[///]\n\n### **Mantenimiento**\n\n:gray[Gestión de órdenes de trabajo, paradas de planta, confiabilidad y repuestos.]\n\n"

    with col1:
        # MÓDULO 1: CONTROL DE CALIDAD
        if st.button(txt_cc, use_container_width=True, key="card_cc"):
            st.switch_page("pages/CONTROL_CALIDAD.py")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(163,255,0,0.1); color: #a3ff00; border: 1px solid rgba(163,255,0,0.3); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ MÓDULO ACTIVO</span></div>""", unsafe_allow_html=True)
            
        # MÓDULO 3: ELABORACIÓN
        if st.button(txt_elab, use_container_width=True, key="card_elab"):
            try:
                st.switch_page("pages/ELABORACION.py")
            except:
                st.warning("🚧 Módulo de Elaboración en desarrollo.")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(250,204,21,0.1); color: #facc15; border: 1px solid rgba(250,204,21,0.3); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ EN DESARROLLO</span></div>""", unsafe_allow_html=True)

    with col2:
        # MÓDULO 2: ENVASADO
        if st.button(txt_env, use_container_width=True, key="card_env"):
            try:
                st.switch_page("pages/ENVASADO.py")
            except:
                st.warning("🚧 Módulo de Envasado en desarrollo.")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(250,204,21,0.1); color: #facc15; border: 1px solid rgba(250,204,21,0.3); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ EN DESARROLLO</span></div>""", unsafe_allow_html=True)
            
        # MÓDULO 4: MANTENIMIENTO
        if st.button(txt_mant, use_container_width=True, key="card_mant"):
            try:
                st.switch_page("pages/MANTENIMIENTO.py")
            except:
                st.warning("🚧 Módulo de Mantenimiento en desarrollo.")
        st.markdown("""<div style='margin-top: -55px; margin-left: 25px; margin-bottom: 40px; pointer-events: none;'><span style='background-color: rgba(250,204,21,0.1); color: #facc15; border: 1px solid rgba(250,204,21,0.3); padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;'>■ EN DESARROLLO</span></div>""", unsafe_allow_html=True)
        
    st.markdown("<br><hr style='border: 1px solid #1a1a1a; margin-top: 1rem;'><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #333333; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'>BBO Cervecería © 2026 - Departamento de Calidad</p>", unsafe_allow_html=True)