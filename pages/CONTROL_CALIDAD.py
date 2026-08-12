import streamlit as st
from utils.core import aplicar_estilo_neon

st.set_page_config(page_title="Control de Calidad", layout="wide", initial_sidebar_state="expanded")

# --- APLICAR CSS GLOBAL PRIMERO ---
aplicar_estilo_neon()
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp { 
        font-family: 'Inter', sans-serif !important; 
        background-color: #050505 !important; 
        color: #e0e0e0 !important; 
    }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }
    
    /* BOTÓN VOLVER PRINCIPAL (Afecta solo a los botones fuera de columnas) */
    div[data-testid="stButton"] > button { 
        background-color: transparent !important; 
        border: 1px solid #1a1a1a !important; 
        width: fit-content !important; 
        padding: 6px 16px !important; 
        border-radius: 6px !important; 
        transition: 0.3s !important; 
        margin-bottom: 10px !important;
    }
    div[data-testid="stButton"] > button p { 
        color: #888888 !important; 
        font-weight: 700 !important; 
        font-size: 0.8rem !important; 
        letter-spacing: 1px !important; 
    }
    div[data-testid="stButton"] > button:hover { 
        border-color: #a3ff00 !important; 
        background-color: rgba(163, 255, 0, 0.05) !important; 
    }
    div[data-testid="stButton"] > button:hover p { 
        color: #a3ff00 !important; 
    }
    
    /* =======================================================
       TARJETAS GIGANTES NATIVAS (ALTURA FIJA Y CERO TRUCOS)
       ======================================================= */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        padding: 24px !important;
        border-radius: 12px !important;
        height: 270px !important; /* Altura estricta para alinear pastillas */
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        text-align: left !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5) !important;
        margin-bottom: 0 !important;
    }

    /* Aseguramos que el texto por dentro no tenga márgenes rebeldes */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button div[data-testid="stMarkdownContainer"] {
        width: 100% !important; text-align: left !important;
    }

    div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
        border-color: #a3ff00 !important;
        box-shadow: 0 0 20px rgba(163, 255, 0, 0.15) !important;
        transform: translateY(-4px) !important;
    }
    
    /* Estilos para el texto interno del botón */
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p {
        color: #888888 !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        font-family: 'Inter', sans-serif !important;
        white-space: pre-wrap !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p strong:nth-of-type(1) {
        color: #a3ff00 !important;
        font-size: 1.15rem !important;
        letter-spacing: 2px !important;
        margin-bottom: 5px !important;
        display: inline-block !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p strong:nth-of-type(2) {
        color: #ffffff !important;
        font-size: 1.35rem !important;
        display: block !important;
        margin-top: 15px !important;
        margin-bottom: 10px !important;
        letter-spacing: -0.5px !important;
    }

    /* PASTILLAS PERFECTAMENTE ALINEADAS */
    .pill-container { 
        margin-top: -70px !important; 
        margin-left: 24px !important; 
        margin-bottom: 30px !important; 
        pointer-events: none !important; 
        position: relative !important; 
        z-index: 10 !important; 
        font-family: 'Inter', sans-serif !important;
        transition: transform 0.3s ease !important; 
    }
    .pill-activo { background-color: rgba(163, 255, 0, 0.1); color: #a3ff00; border: 1px solid rgba(163, 255, 0, 0.3); padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; display: inline-block; }
    .pill-desarrollo { background-color: rgba(250, 204, 21, 0.1); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.3); padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; letter-spacing: 1px; display: inline-block; }
                
    /* MAGIA: Solo levanta la pastilla de la tarjeta específica que estás tocando */
    div.element-container:has(button:hover) + div.element-container .pill-container {
        transform: translateY(-4px) !important;
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

st.markdown("<br>", unsafe_allow_html=True)

# --- NUEVO BOTÓN DE VOLVER ---
if st.button("◀ VOLVER AL INICIO"):
    st.switch_page("app.py")

st.markdown("<h1 style='color: #ffffff; font-size: 2.2rem; font-weight: 800; letter-spacing: 2px; margin: 0;'>DEPARTAMENTO / <span style='color: #a3ff00;'>CONTROL DE CALIDAD</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.95rem; margin-bottom: 3rem;'>Selecciona la herramienta o módulo que deseas operar:</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Textos Nativos limpios
txt_fq = "**///**\n\n**PARÁMETROS FISICOQUÍMICOS**\n\nAnálisis SPC, Cp/Cpk y resumen de producción mensual."
txt_est = "**///**\n\n**CONTROL DE TANQUES**\n\nMonitoreo logístico y alertas tempranas en tanques."
txt_mic = "**///**\n\n**ANÁLISIS MICROBIOLÓGICOS**\n\nSPC para recuento de levaduras, bacterias y aerobios totales."
txt_ing = "**///**\n\n**INGRESO DE DATOS**\n\nCarga directa de variables desde el HUB sin usar Google Sheets."
txt_exp = "**///**\n\n**EXPORTAR REPORTES**\n\nBúsqueda rápida de lotes y envío automatizado vía WhatsApp."

with col1:
    if st.button(txt_fq, use_container_width=True, key="btn_fq"): st.switch_page("pages/1_PARAMETROS_CRITICOS.py")
    st.markdown("<div class='pill-container'><span class='pill-activo'>■ MÓDULO ACTIVO</span></div>", unsafe_allow_html=True)
    
    if st.button(txt_est, use_container_width=True, key="btn_est"): st.switch_page("pages/3_ESTADIA_TANQUES.py")
    st.markdown("<div class='pill-container'><span class='pill-activo'>■ MÓDULO ACTIVO</span></div>", unsafe_allow_html=True)

with col2:
    if st.button(txt_mic, use_container_width=True, key="btn_mic"):
        st.switch_page("pages/4_MICROBIOLOGIA.py") 
    st.markdown("<div class='pill-container'><span class='pill-activo'>■ NUEVO MÓDULO</span></div>", unsafe_allow_html=True)
    
    if st.button(txt_ing, use_container_width=True, key="btn_ing"): 
        pass
    st.markdown("<div class='pill-container'><span class='pill-desarrollo'>■ EN DESARROLLO</span></div>", unsafe_allow_html=True)

with col3:
    if st.button(txt_exp, use_container_width=True, key="btn_exp"): 
        st.switch_page("pages/2_EXPORTAR_DATOS.py") 
    st.markdown("<div class='pill-container'><span class='pill-activo'>■ MÓDULO ACTIVO</span></div>", unsafe_allow_html=True)
    
st.markdown("<br><br>", unsafe_allow_html=True)