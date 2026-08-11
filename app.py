import streamlit as st
import os
import datetime

# Configuración inicial de la página
st.set_page_config(page_title="HUB BBO CALIDAD", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Fecha actual para simular el "Última actualización" del dashboard
fecha_actual = datetime.datetime.now().strftime("%d-%b-%Y %H:%M")

# --- CSS GLOBAL: NUEVA ESTÉTICA "SLATE DARK MODE" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. FONDOS Y TEXTOS (Estilo Azul Pizarra / Slate) */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #11151c !important; /* Fondo principal */
        color: #e0e4eb !important;
    }
    
    /* 2. OCULTAR ELEMENTOS NATIVOS FEOS */
    [data-testid="stSidebarNav"] {display: none !important;}
    header[data-testid="stHeader"] {background-color: transparent !important;}
    
    /* 3. SIDEBAR (Cerrar Sesión al fondo) */
    section[data-testid="stSidebar"] {
        background-color: #181c25 !important;
        border-right: 1px solid #2a2f3d !important;
    }
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
        border: 1px solid #2a2f3d !important;
        width: 100% !important;
        padding: 8px !important;
        border-radius: 6px !important;
        transition: 0.3s !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
        color: #838a9b !important;
        font-size: 0.8rem !important;
        margin: 0 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: #ff007a !important;
        background-color: rgba(255, 0, 122, 0.1) !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover p {
        color: #ff007a !important;
    }

    /* 4. TARJETAS DE MÓDULOS (Estilo KPI Dashboard) */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #1a1e29 !important;
        border: 1px solid #2a2f3d !important;
        border-radius: 8px !important;
        padding: 24px !important;
        min-height: 160px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        background-color: #212634 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.4) !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p {
        font-family: 'Inter', sans-serif !important;
        margin: 0 !important;
        white-space: pre-wrap !important;
        text-align: left !important;
        width: 100% !important;
        color: #838a9b !important;
        line-height: 1.4 !important;
        font-size: 0.85rem !important;
    }
    /* Primera línea (Títulos) con colores dinámicos */
    div[data-testid="stColumn"]:nth-child(1) div[data-testid="stButton"] > button p::first-line {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    /* 5. HERRAMIENTAS FLOTANTES (Right Sidebar UX) */
    .floating-tools {
        position: fixed;
        right: 0;
        top: 40%;
        display: flex;
        flex-direction: column;
        gap: 8px;
        z-index: 9999;
    }
    .tool-btn {
        background-color: #181c25;
        border: 1px solid #2a2f3d;
        border-right: none;
        color: #838a9b;
        padding: 15px 6px;
        border-radius: 8px 0 0 8px;
        text-decoration: none;
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        text-align: center;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 2px;
        transition: 0.3s;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: -2px 2px 10px rgba(0,0,0,0.3);
    }
    .tool-btn:hover {
        color: #ffffff;
        background-color: #212634;
    }
    .tool-jarvis { border-left: 2px solid #ff007a; }
    .tool-jarvis:hover { border-color: #ff007a; color: #ff007a; }
    
    .tool-pdf { border-left: 2px solid #00e5ff; }
    .tool-pdf:hover { border-color: #00e5ff; color: #00e5ff; }
    
    .tool-explore { border-left: 2px solid #ff9100; }
    .tool-explore:hover { border-color: #ff9100; color: #ff9100; }
    
    /* 6. BOTÓN LOGIN */
    div[data-testid="stFormSubmitButton"] > button { 
        background-color: #ff007a !important; 
        border: none !important; 
        border-radius: 6px !important; 
        width: 100% !important; 
        padding: 0.8rem !important; 
    }
    div[data-testid="stFormSubmitButton"] > button p { 
        color: #ffffff !important; 
        font-weight: 600 !important; 
    }
    div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #d60066 !important; 
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
            border: 1px solid #2a2f3d !important; 
            border-radius: 12px !important; 
            background-color: #181c25 !important; 
            padding: 3rem 2.5rem !important; 
            box-shadow: 0 20px 50px rgba(0,0,0,0.5) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("""
                <div style='text-align: center; margin-bottom: 30px;'>
                    <span style='color: #ffffff; font-size: 2.5rem; font-weight: 700; letter-spacing: 2px;'>Panel de Control <span style="color: #ff007a;">BBO</span></span>
                    <p style='color: #838a9b; font-size: 0.85rem; margin-top: 5px;'>INGRESO SEGURO AL SISTEMA</p>
                </div>
            """, unsafe_allow_html=True)
            
            usuario = st.text_input("Usuario corporativo")
            password = st.text_input("Contraseña", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Iniciar Sesión")
            
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
# 🟢 DASHBOARD PRINCIPAL (NUEVA UI)
# ==========================================
else:
    # --- MENÚ LATERAL ---
    st.sidebar.markdown(f"""
        <div style='text-align: center; margin-bottom: 25px;'>
            <div style='background-color: #212634; height: 60px; width: 60px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; border: 2px solid #ff007a;'>
                <span style='font-size: 1.5rem;'>👤</span>
            </div>
            <p style='color: #ffffff; font-weight: 600; margin-top: 10px; margin-bottom: 0;'>{st.session_state['usuario_actual'].upper()}</p>
            <span style='color: #838a9b; font-size: 0.75rem;'>Operador Certificado</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- ENCABEZADO ESTILO DASHBOARD ---
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid #2a2f3d; padding-bottom: 15px; margin-bottom: 30px; margin-top: 10px;'>
            <div>
                <h1 style='color: #ffffff; font-size: 1.8rem; font-weight: 600; margin: 0;'>Panel de Control de Calidad</h1>
                <span style='color: #838a9b; font-size: 0.85rem;'>Métricas de rendimiento, procesos y tiempos de residencia.</span>
            </div>
            <div style='color: #838a9b; font-size: 0.75rem; display: flex; align-items: center; gap: 5px;'>
                <span>🔄 Última actualización: {fecha_actual}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- SIMULACIÓN DE TABS Y FILTROS RAPIDOS ---
    st.markdown("""
        <div style='display: flex; gap: 20px; margin-bottom: 25px;'>
            <span style='color: #ff007a; border-bottom: 2px solid #ff007a; padding-bottom: 5px; font-size: 0.9rem; font-weight: 600; cursor: pointer;'>📊 Dashboard</span>
            <span style='color: #838a9b; font-size: 0.9rem; font-weight: 500; cursor: pointer;'>📝 Reportes</span>
            <span style='color: #838a9b; font-size: 0.9rem; font-weight: 500; cursor: pointer;'>⚙️ Configuración</span>
        </div>
    """, unsafe_allow_html=True)

    # --- HERRAMIENTAS FLOTANTES (FAB UX) ---
    st.markdown("""
        <div class="floating-tools">
            <a href="#" class="tool-btn tool-explore">
                <span>EXPLORAR</span>
            </a>
            <a href="#" class="tool-btn tool-jarvis">
                <span>🤖 JARVIS</span>
            </a>
            <a href="#" class="tool-btn tool-pdf">
                <span>📄 PDF</span>
            </a>
        </div>
    """, unsafe_allow_html=True)

    # --- CUADRÍCULA DE MÓDULOS (KPI CARDS) ---
    st.markdown("<p style='color: #ffffff; font-size: 0.9rem; font-weight: 600; margin-bottom: 15px; letter-spacing: 1px;'>MÓDULOS PRINCIPALES</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)

    # Usamos inyección de CSS directo a los botones para darle los bordes de colores (verde, rojo, naranja, azul)
    with col1:
        st.markdown('<style>div[data-testid="stColumn"]:nth-child(1) div[data-testid="stButton"] > button { border-top: 3px solid #00e676 !important; }</style>', unsafe_allow_html=True)
        if st.button("🔬 Control de Calidad\n\nAnálisis SPC, tendencias y resumen de producción.\n\n▲ Estado: Óptimo", use_container_width=True, key="card_cc"):
            st.switch_page("pages/CONTROL_CALIDAD.py")

    with col2:
        st.markdown('<style>div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] > button { border-top: 3px solid #ff9100 !important; }</style>', unsafe_allow_html=True)
        if st.button("⏳ Control de Estadía\n\nTiempos de residencia y alertas tempranas.\n\n▼ 2 Alertas activas", use_container_width=True, key="card_est"):
            st.switch_page("pages/3_ESTADIA_TANQUES.py")

    with col3:
        st.markdown('<style>div[data-testid="stColumn"]:nth-child(3) div[data-testid="stButton"] > button { border-top: 3px solid #00e5ff !important; }</style>', unsafe_allow_html=True)
        if st.button("🏭 Elaboración\n\nCocimiento, fermentación y mermas.\n\n▶ En desarrollo", use_container_width=True, key="card_elab"):
            try: st.switch_page("pages/ELABORACION.py")
            except: st.warning("Módulo en desarrollo.")

    with col4:
        st.markdown('<style>div[data-testid="stColumn"]:nth-child(4) div[data-testid="stButton"] > button { border-top: 3px solid #ff007a !important; }</style>', unsafe_allow_html=True)
        if st.button("📦 Envasado\n\nLíneas de llenado y eficiencias (OEE).\n\n▶ En desarrollo", use_container_width=True, key="card_env"):
            try: st.switch_page("pages/ENVASADO.py")
            except: st.warning("Módulo en desarrollo.")
            
    st.markdown("<br><hr style='border: 1px solid #2a2f3d;'><br>", unsafe_allow_html=True)