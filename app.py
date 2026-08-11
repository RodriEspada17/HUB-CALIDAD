import streamlit as st
import datetime
from utils.core import aplicar_estilo_neon

# Configuración inicial de la página
st.set_page_config(page_title="HUB BBO CALIDAD", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Fecha actual para la última actualización (Zona Horaria Bolivia GMT-4)
bolivia_tz = datetime.timezone(datetime.timedelta(hours=-4))
fecha_actual = datetime.datetime.now(bolivia_tz).strftime("%d-%b-%Y %H:%M")

# Aplica la tipografía y el fondo base
aplicar_estilo_neon()

# --- CSS GLOBAL: DARK NEÓN + UX AVANZADA ---
st.markdown("""
    <style>
    /* 1. TIPOGRAFÍA Y FONDOS NEÓN */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap');
    html, body, [class*="css"], .stApp {
        font-family: 'Space Grotesk', sans-serif !important;
        background-color: #050505 !important;
        color: #e0e0e0 !important;
    }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* 2. SIDEBAR Y PERFIL */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #1a1a1a !important;
    }
    
    /* Botón de Cerrar Sesión (Pequeño y centrado bajo el perfil) */
    div[data-testid="stSidebar"] div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        margin-top: 10px !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background-color: transparent !important;
        border: 1px solid #1a1a1a !important;
        width: fit-content !important; 
        padding: 4px 16px !important;
        border-radius: 4px !important;
        transition: 0.3s !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
        color: #555555 !important;
        font-size: 0.7rem !important;
        margin: 0 !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #f87171 !important;
        background-color: rgba(248, 113, 113, 0.1) !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p {
        color: #f87171 !important;
    }

    /* 3. HERRAMIENTAS FLOTANTES (FABs) NEÓN */
    .floating-tools {
        position: fixed;
        right: 0;
        top: 35%;
        display: flex;
        flex-direction: column;
        gap: 8px;
        z-index: 9999;
    }
    .tool-btn {
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-right: none;
        color: #888888;
        padding: 16px 8px;
        border-radius: 8px 0 0 8px;
        text-decoration: none !important;
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        text-align: center;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: -2px 2px 15px rgba(0,0,0,0.5);
    }
    .tool-btn:hover {
        color: #050505 !important;
        background-color: #a3ff00;
        border-color: #a3ff00;
        box-shadow: -5px 0 20px rgba(163, 255, 0, 0.3);
    }

    /* =========================================================
       4. EXTERMINIO DEL CUADRO VERDE Y SUPERPOSICIÓN PERFECTA 
       ========================================================= */
       
    /* Altura fija de la tarjeta para que coincida matemáticamente con el botón */
    .card-module {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        padding: 24px;
        border-radius: 12px;
        height: 260px !important; /* Altura estricta */
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }
    
    /* El Hover visual reacciona al pasar el ratón por la columna entera */
    div[data-testid="column"]:hover .card-module {
        border-color: #a3ff00 !important;
        box-shadow: 0 0 20px rgba(163, 255, 0, 0.15) !important;
        transform: translateY(-4px) !important;
    }

    /* EL BOTÓN CRISTAL INVISIBLE (Cero bordes, cero asco) */
    div[data-testid="column"] div[data-testid="stButton"] {
        margin-top: -260px !important; /* Lo jala hacia arriba EXACTAMENTE el tamaño de la tarjeta */
        height: 260px !important;
        width: 100% !important;
        z-index: 999 !important;
    }
    div[data-testid="column"] div[data-testid="stButton"] > button {
        height: 100% !important;
        width: 100% !important;
        background: transparent !important; /* Sin fondo */
        border: none !important; /* EXTERMINA EL BORDE VERDE */
        box-shadow: none !important;
        color: transparent !important;
        cursor: pointer !important;
    }
    div[data-testid="column"] div[data-testid="stButton"] > button:hover,
    div[data-testid="column"] div[data-testid="stButton"] > button:active,
    div[data-testid="column"] div[data-testid="stButton"] > button:focus {
        background: transparent !important;
        border: none !important; /* EXTERMINA EL BORDE AL HACER CLIC */
        box-shadow: none !important;
        outline: none !important;
        color: transparent !important;
    }
    div[data-testid="column"] div[data-testid="stButton"] > button p {
        display: none !important; /* Desaparece cualquier texto interno */
    }

    /* Estética interna de los textos de la tarjeta */
    .card-slashes { color: #a3ff00; font-weight: 800; font-size: 1.2rem; letter-spacing: 2px; margin-bottom: 12px; }
    .card-title-text { color: #ffffff; font-size: 1.35rem; font-weight: 700; margin-bottom: 12px; line-height: 1.2; }
    .card-desc-text { color: #888888; font-size: 0.9rem; line-height: 1.5; margin-bottom: 25px; }
    .pill-activo { background-color: rgba(163, 255, 0, 0.1); color: #a3ff00; border: 1px solid rgba(163, 255, 0, 0.3); padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; display: inline-block; }
    .pill-desarrollo { background-color: rgba(250, 204, 21, 0.1); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.3); padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; display: inline-block; }

    /* 5. BOTÓN DE LOGIN (Este sí mantiene su estilo verde) */
    div[data-testid="stFormSubmitButton"] > button { 
        background-color: #050505 !important; 
        border: 1px solid #a3ff00 !important; 
        border-radius: 6px !important; 
        width: 100% !important; 
        padding: 0.8rem !important; 
        transition: 0.3s !important;
    }
    div[data-testid="stFormSubmitButton"] > button p { color: #a3ff00 !important; font-weight: 700 !important; letter-spacing: 1px !important; }
    div[data-testid="stFormSubmitButton"] > button:hover { background-color: #a3ff00 !important; box-shadow: 0 0 15px rgba(163,255,0,0.3) !important; }
    div[data-testid="stFormSubmitButton"] > button:hover p { color: #050505 !important; }
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
        [data-testid="stForm"] { border: 1px solid #1a1a1a !important; border-radius: 12px !important; background-color: #0a0a0a !important; padding: 3rem 2.5rem !important; box-shadow: 0 20px 50px rgba(0,0,0,0.8) !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("""
                <div style='text-align: center; margin-bottom: 30px;'>
                    <span style='color: #a3ff00; font-size: 3rem; font-weight: 800; letter-spacing: 5px;'>HUB <span style="color: #ffffff;">BBO</span></span>
                    <p style='color: #888888; font-size: 0.85rem; letter-spacing: 2px; margin-top: 5px;'>INGRESO SEGURO AL SISTEMA</p>
                </div>
            """, unsafe_allow_html=True)
            
            usuario = st.text_input("Usuario corporativo")
            password = st.text_input("Contraseña", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("INICIAR SESIÓN")
            
            if submit:
                try:
                    if usuario in st.secrets["passwords"] and st.secrets["passwords"][usuario] == password:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_actual'] = usuario
                        st.rerun() 
                    else:
                        st.error("Credenciales incorrectas.")
                except Exception as e:
                    st.error("Error: Bóveda de Secretos no configurada.")

# ==========================================
# 🟢 DASHBOARD PRINCIPAL (NEÓN + UX)
# ==========================================
else:
    # --- MENÚ LATERAL ---
    st.sidebar.markdown(f"""
        <div style='text-align: center; margin-bottom: 5px;'>
            <div style='background-color: #0a0a0a; height: 60px; width: 60px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; border: 2px solid #a3ff00; box-shadow: 0 0 10px rgba(163,255,0,0.2);'>
                <span style='font-size: 1.5rem;'>👤</span>
            </div>
            <p style='color: #ffffff; font-weight: 700; margin-top: 12px; margin-bottom: 0; letter-spacing: 1px;'>{st.session_state['usuario_actual'].upper()}</p>
            <span style='color: #a3ff00; font-size: 0.75rem; letter-spacing: 2px;'>GERENCIA</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("■ CERRAR SESIÓN"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- HERRAMIENTAS FLOTANTES (FAB UX) ---
    st.markdown("""
        <div class="floating-tools">
            <a href="#" class="tool-btn"><span>🔍 EXPLORAR</span></a>
            <a href="#" class="tool-btn"><span>🤖 JARVIS</span></a>
            <a href="#" class="tool-btn"><span>📄 PDF</span></a>
        </div>
    """, unsafe_allow_html=True)

    # --- ENCABEZADO ---
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid #1a1a1a; padding-bottom: 15px; margin-bottom: 30px; margin-top: 10px;'>
            <div>
                <h1 style='color: #a3ff00; font-size: 2rem; font-weight: 800; letter-spacing: 4px; margin: 0;'>HUB <span style='color: #ffffff;'>BBO</span></h1>
                <span style='color: #888888; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase;'>Centro de Control y Monitoreo</span>
            </div>
            <div style='color: #555555; font-size: 0.75rem; display: flex; align-items: center; gap: 5px; font-weight: 600;'>
                <span>ÚLTIMA ACTUALIZACIÓN: {fecha_actual}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- SIMULACIÓN DE TABS LIMPIA ---
    st.markdown("""
        <div style='display: flex; gap: 30px; margin-bottom: 30px;'>
            <span style='color: #a3ff00; border-bottom: 2px solid #a3ff00; padding-bottom: 5px; font-size: 0.9rem; font-weight: 700; letter-spacing: 1px;'>■ MÓDULOS</span>
        </div>
    """, unsafe_allow_html=True)

    # --- CUADRÍCULA DE MÓDULOS EN 4 COLUMNAS ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
            <div class="card-module">
                <div>
                    <div class="card-slashes">///</div>
                    <div class="card-title-text">Control de Calidad</div>
                    <div class="card-desc-text">Análisis SPC, tendencias y resumen de producción mensual.</div>
                </div>
                <div><span class="pill-activo">■ MÓDULO ACTIVO</span></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("btn_cc_invisible", key="btn_cc"):
            st.switch_page("pages/CONTROL_CALIDAD.py")

    with col2:
        st.markdown("""
            <div class="card-module">
                <div>
                    <div class="card-slashes">///</div>
                    <div class="card-title-text">Mantenimiento</div>
                    <div class="card-desc-text">Gestión de órdenes de trabajo, paradas de planta, confiabilidad y repuestos.</div>
                </div>
                <div><span class="pill-desarrollo">■ EN DESARROLLO</span></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("btn_mant_invisible", key="btn_mant"):
            try: st.switch_page("pages/MANTENIMIENTO.py")
            except: st.toast("🚧 Módulo de Mantenimiento en desarrollo.", icon="🚧")

    with col3:
        st.markdown("""
            <div class="card-module">
                <div>
                    <div class="card-slashes">///</div>
                    <div class="card-title-text">Elaboración</div>
                    <div class="card-desc-text">Control de procesos de cocimiento, fermentación y filtración. Mermas y eficiencias.</div>
                </div>
                <div><span class="pill-desarrollo">■ EN DESARROLLO</span></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("btn_elab_invisible", key="btn_elab"):
            try: st.switch_page("pages/ELABORACION.py")
            except: st.toast("🚧 Módulo de Elaboración en desarrollo.", icon="🚧")

    with col4:
        st.markdown("""
            <div class="card-module">
                <div>
                    <div class="card-slashes">///</div>
                    <div class="card-title-text">Envasado</div>
                    <div class="card-desc-text">Supervisión de líneas de llenado, mermas de empaque y eficiencias (OEE).</div>
                </div>
                <div><span class="pill-desarrollo">■ EN DESARROLLO</span></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("btn_env_invisible", key="btn_env"):
            try: st.switch_page("pages/ENVASADO.py")
            except: st.toast("🚧 Módulo de Envasado en desarrollo.", icon="🚧")

    st.markdown("<br><hr style='border: 1px solid #1a1a1a;'><br>", unsafe_allow_html=True)