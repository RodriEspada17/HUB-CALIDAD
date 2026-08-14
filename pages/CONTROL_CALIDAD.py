import streamlit as st
import os
from PIL import Image  # 🔥 NUEVO: Librería para procesar la imagen
from utils.core import aplicar_estilo_neon
# ... (aquí van tus otros imports como pandas, numpy, etc) ...

# ==========================================
# 🔥 CONFIGURACIÓN PRO DE LA PÁGINA Y FAVICON
# ==========================================
# Buscamos el logo. Si no existe, usamos un ícono por defecto para que no explote.
ruta_logo = "LogoBBO.png" 
if os.path.exists(ruta_logo):
    icono = Image.open(ruta_logo)
else:
    icono = "⚙️" # Ícono de respaldo

# Esto SIEMPRE debe ser el primer comando de Streamlit
st.set_page_config(
    page_title="Control de Calidad", # Cambia esto según la página (ej. "Control de Aguas")
    page_icon=icono, 
    layout="wide", 
    initial_sidebar_state="expanded" # O "collapsed" según la página
)

# --- APLICAR CSS GLOBAL PRIMERO ---
aplicar_estilo_neon()
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp { 
        font-family: 'Inter', sans-serif !important; 
        background-color: #050505 !important; 
        color: #e0e0e0 !important; 
        overflow-y: hidden !important; /* 🔥 BLOQUEA EL SCROLL VERTICAL */
    }
    header[data-testid="stHeader"] { background-color: transparent !important; height: 0px !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }
    
    /* COMPRESIÓN DE MÁRGENES PARA EVITAR SCROLL */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* BOTÓN VOLVER PRINCIPAL */
    div[data-testid="stButton"] > button { 
        background-color: transparent !important; 
        border: 1px solid #1a1a1a !important; 
        width: fit-content !important; 
        padding: 4px 12px !important; 
        border-radius: 6px !important; 
        transition: 0.3s !important; 
        margin-bottom: 0px !important;
    }
    div[data-testid="stButton"] > button p { 
        color: #888888 !important; font-weight: 700 !important; font-size: 0.75rem !important; letter-spacing: 1px !important; 
    }
    div[data-testid="stButton"] > button:hover { 
        border-color: #a3ff00 !important; background-color: rgba(163, 255, 0, 0.05) !important; 
    }
    div[data-testid="stButton"] > button:hover p { 
        color: #a3ff00 !important; 
    }
    
    /* ELIMINAR EL FOCO PERMANENTE DESPUÉS DEL CLIC */
    div[data-testid="stButton"] > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }
    div[data-testid="stButton"] > button:focus:not(:hover) {
        border-color: #1a1a1a !important;
        background-color: transparent !important;
    }
    div[data-testid="stButton"] > button:focus:not(:hover) p {
        color: #888888 !important;
    }
    
    /* =======================================================
       TARJETAS GIGANTES NATIVAS (COMPRIMIDAS)
       ======================================================= */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        position: relative !important; 
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        padding: 20px !important; /* Padding ligeramente menor */
        border-radius: 12px !important;
        height: 220px !important; /* 🔥 ALTURA REDUCIDA PARA QUE ENTREN LAS 2 FILAS */
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        text-align: left !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5) !important;
    }

    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        border-color: #a3ff00 !important;
        box-shadow: 0 0 20px rgba(163, 255, 0, 0.15) !important;
        transform: translateY(-4px) !important;
    }
    
    /* Estilos del texto */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p {
        color: #888888 !important; font-size: 0.85rem !important; line-height: 1.4 !important; font-family: 'Inter', sans-serif !important; white-space: pre-wrap !important; width: 100% !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p strong:nth-of-type(1) {
        color: #a3ff00 !important; font-size: 1.05rem !important; letter-spacing: 2px !important; margin-bottom: 2px !important; display: inline-block !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p strong:nth-of-type(2) {
        color: #ffffff !important; font-size: 1.25rem !important; display: block !important; margin-top: 10px !important; margin-bottom: 8px !important; letter-spacing: -0.5px !important;
    }

    /* 🔥 LA MAGIA: PASTILLA VERDE */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button code {
        position: absolute !important;
        bottom: 20px !important; 
        left: 20px !important;   
        background-color: rgba(163, 255, 0, 0.1) !important;
        color: #a3ff00 !important;
        border: 1px solid rgba(163, 255, 0, 0.3) !important;
        padding: 4px 10px !important;
        border-radius: 4px !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        font-family: 'Inter', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🟢 LOBBY CALIDAD
# ==========================================
st.sidebar.markdown(f"""
    <div style='background-color: #050505; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 25px;'>
        <span style='color: #888888; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;'>Sesión Activa</span><br>
        <span style='color: #a3ff00; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>■ {st.session_state.get('usuario_actual', 'USER').upper()}</span>
    </div>
""", unsafe_allow_html=True)

# --- BOTÓN DE VOLVER ---
if st.button("◀ VOLVER AL INICIO"):
    st.switch_page("app.py")

# TÍTULOS (Márgenes ajustados)
st.markdown("<h1 style='color: #ffffff; font-size: 2rem; font-weight: 800; letter-spacing: 2px; margin: 0; margin-top: 10px;'>DEPARTAMENTO / <span style='color: #a3ff00;'>CONTROL DE CALIDAD</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.95rem; margin-bottom: 1.5rem;'>Selecciona la herramienta o módulo que deseas operar:</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# 🔥 TEXTOS DE TARJETAS 
txt_fq = "**///**\n\n**PARÁMETROS FISICOQUÍMICOS**\n\nAnálisis SPC, Cp/Cpk y resumen de producción mensual.\n\n`■ MÓDULO ACTIVO`"
txt_est = "**///**\n\n**CONTROL DE TANQUES**\n\nMonitoreo logístico y alertas tempranas en tanques.\n\n`■ MÓDULO ACTIVO`"
txt_mic = "**///**\n\n**ANÁLISIS MICROBIOLÓGICOS**\n\nSPC para recuento de levaduras, bacterias y aerobios totales.\n\n`■ MÓDULO ACTIVO`"
txt_ing = "**///**\n\n**CONTROL DE AGUAS**\n\nGestión y SPC físico-químico del agua de planta.\n\n`■ MÓDULO ACTIVO`"
txt_exp = "**///**\n\n**EXPORTAR REPORTES**\n\nBúsqueda rápida de lotes y envío automatizado vía WhatsApp.\n\n`■ MÓDULO ACTIVO`"

# CÓDIGO PYTHON SÚPER LIMPIO
with col1:
    if st.button(txt_fq, use_container_width=True, key="btn_fq"): st.switch_page("pages/1_PARAMETROS_CRITICOS.py")
    if st.button(txt_est, use_container_width=True, key="btn_est"): st.switch_page("pages/3_ESTADIA_TANQUES.py")

with col2:
    if st.button(txt_mic, use_container_width=True, key="btn_mic"): st.switch_page("pages/4_MICROBIOLOGIA.py") 
    if st.button(txt_ing, use_container_width=True, key="btn_ing"): st.switch_page("pages/5_CONTROL_AGUAS.py")

with col3:
    if st.button(txt_exp, use_container_width=True, key="btn_exp"): st.switch_page("pages/2_EXPORTAR_DATOS.py")