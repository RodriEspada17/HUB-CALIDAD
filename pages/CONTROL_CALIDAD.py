import streamlit as st
from utils.core import aplicar_estilo_neon

# Configuración inicial
st.set_page_config(page_title="Control de Calidad", layout="wide", initial_sidebar_state="expanded")

# Verificar sesión
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en el HUB principal.")
    st.stop()

aplicar_estilo_neon()

# --- CSS GLOBAL DE ALTA GAMA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Space Grotesk', sans-serif !important; background-color: #050505 !important; color: #e0e0e0 !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }
    
    /* TARJETAS MÓDULOS */
    .card-module {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        padding: 24px;
        border-radius: 12px;
        text-decoration: none !important;
        min-height: 250px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .card-module:hover {
        border-color: #a3ff00;
        box-shadow: 0 0 20px rgba(163, 255, 0, 0.15);
        transform: translateY(-4px);
    }
    .card-slashes { color: #a3ff00; font-weight: 800; font-size: 1.2rem; letter-spacing: 2px; margin-bottom: 12px; }
    .card-title-text { color: #ffffff; font-size: 1.35rem; font-weight: 700; margin-bottom: 12px; line-height: 1.2; }
    .card-desc-text { color: #888888; font-size: 0.9rem; line-height: 1.5; margin-bottom: 25px; }
    .pill-activo { background-color: rgba(163, 255, 0, 0.1); color: #a3ff00; border: 1px solid rgba(163, 255, 0, 0.3); padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; display: inline-block; }
    .pill-desarrollo { background-color: rgba(250, 204, 21, 0.1); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.3); padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; display: inline-block; }
    
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: transparent !important; border: none !important; padding: 0 !important; width: 100% !important;
    }
    
    /* Botón volver */
    .btn-volver {
        color: #888888 !important; font-size: 0.85rem !important; text-decoration: none !important; font-weight: 700 !important; letter-spacing: 1px !important; transition: 0.3s !important;
    }
    .btn-volver:hover { color: #a3ff00 !important; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown(f"""
    <div style='background-color: #050505; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 25px;'>
        <span style='color: #888888; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;'>Sesión Activa</span><br>
        <span style='color: #a3ff00; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>■ {st.session_state.get('usuario_actual', 'USER').upper()}</span>
    </div>
""", unsafe_allow_html=True)
st.sidebar.page_link("app.py", label="◀ VOLVER AL INICIO")

# --- ENCABEZADO ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #ffffff; font-size: 2.2rem; font-weight: 800; letter-spacing: 2px; margin: 0;'>DEPARTAMENTO / <span style='color: #a3ff00;'>CONTROL DE CALIDAD</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.95rem; margin-bottom: 3rem;'>Selecciona la herramienta o módulo que deseas operar:</p>", unsafe_allow_html=True)

# --- CUADRÍCULA DE HERRAMIENTAS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <a href="1_PARAMETROS_CRITICOS" target="_self" class="card-module">
            <div>
                <div class="card-slashes">///</div>
                <div class="card-title-text">Parámetros Fisicoquímicos</div>
                <div class="card-desc-text">Análisis SPC, Cp/Cpk y resumen de producción.</div>
            </div>
            <div><span class="pill-activo">■ MÓDULO ACTIVO</span></div>
        </a>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <a href="3_ESTADIA_TANQUES" target="_self" class="card-module">
            <div>
                <div class="card-slashes">///</div>
                <div class="card-title-text">Control de Estadía</div>
                <div class="card-desc-text">Monitoreo logístico y alertas tempranas en tanques.</div>
            </div>
            <div><span class="pill-activo">■ MÓDULO ACTIVO</span></div>
        </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <a href="4_MICROBIOLOGIA" target="_self" class="card-module" style="border-color: #a3ff00; box-shadow: 0 0 15px rgba(163,255,0,0.1);">
            <div>
                <div class="card-slashes">///</div>
                <div class="card-title-text">Análisis Microbiológicos</div>
                <div class="card-desc-text">SPC para recuento de levaduras, bacterias y aerobios totales.</div>
            </div>
            <div><span class="pill-activo">■ NUEVO MÓDULO</span></div>
        </a>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="card-module">
            <div>
                <div class="card-slashes">///</div>
                <div class="card-title-text">Ingreso de Datos</div>
                <div class="card-desc-text">Carga directa de variables desde el HUB.</div>
            </div>
            <div><span class="pill-desarrollo">■ EN DESARROLLO</span></div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="card-module">
            <div>
                <div class="card-slashes">///</div>
                <div class="card-title-text">Exportar Reportes</div>
                <div class="card-desc-text">Búsqueda rápida de lotes y envío vía WhatsApp.</div>
            </div>
            <div><span class="pill-activo">■ MÓDULO ACTIVO</span></div>
        </div>
    """, unsafe_allow_html=True)