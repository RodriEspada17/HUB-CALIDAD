import streamlit as st
import pandas as pd
from utils.core import aplicar_estilo_neon, generar_url_csv, cargar_datos

# Configuración inicial
st.set_page_config(page_title="Estadía de Tanques", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_neon()

# --- CSS AVANZADO: DISEÑO DE DASHBOARD ---
st.markdown("""
    <style>
    /* Estilos del Sidebar Neón */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        background-color: #050505 !important;
        color: #a3ff00 !important;
        border: 1px solid #a3ff00 !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        justify-content: center !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
        background-color: #a3ff00 !important;
        color: #050505 !important;
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] > div {
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
        color: inherit !important; 
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }
    
    /* Tarjetas de Métricas Superiores */
    .metric-card { 
        background-color: #0a0a0a; 
        border: 1px solid #1a1a1a; 
        padding: 24px; 
        border-radius: 8px; 
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #333333;
    }
    .metric-title { 
        color: #888888; 
        font-size: 0.85rem; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        margin-bottom: 10px;
        font-weight: 600;
    }
    .metric-value-green { 
        color: #a3ff00; 
        font-size: 3rem; 
        font-weight: 700; 
        font-family: 'Space Grotesk', sans-serif; 
        line-height: 1;
    }
    .metric-value-red { 
        color: #f87171; 
        font-size: 3rem; 
        font-weight: 700; 
        font-family: 'Space Grotesk', sans-serif; 
        line-height: 1;
    }
    .metric-value-neutral { 
        color: #ffffff; 
        font-size: 3rem; 
        font-weight: 700; 
        font-family: 'Space Grotesk', sans-serif; 
        line-height: 1;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.page_link("app.py", label="< VOLVER AL INICIO")
st.sidebar.page_link("pages/CONTROL_CALIDAD.py", label="< VOLVER A CALIDAD")
st.sidebar.markdown("<br><hr style='border: 1px solid #1a1a1a;'>", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h2 style='text-transform: uppercase; font-size: 1.8rem;'>MÓDULO / <span style='color: #a3ff00;'>ESTADÍA DE TANQUES</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 1rem; margin-bottom: 2rem;'>Monitoreo en tiempo real del tiempo de residencia en tanques clasificado por marca y etapa.</p>", unsafe_allow_html=True)

# --- TARJETAS DE MÉTRICAS (VISUALIZACIÓN INICIAL) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class='metric-card'>
            <div class='metric-title'>Tanques Activos</div>
            <div class='metric-value-green'>--</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class='metric-card'>
            <div class='metric-title'>Alertas de Tiempo Crítico</div>
            <div class='metric-value-red'>--</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class='metric-card'>
            <div class='metric-title'>Promedio Global (Días)</div>
            <div class='metric-value-neutral'>--</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr style='border: 1px solid #1a1a1a;'><br>", unsafe_allow_html=True)

# --- PANEL PRINCIPAL DE CONTROL ---
st.markdown("<h4 style='color: #a3ff00; letter-spacing: 1px; font-size: 1.1rem;'>TABLEROS DE MONITOREO</h4>", unsafe_allow_html=True)

tab_cervezas, tab_malta = st.tabs(["CERVEZAS (Fin de Reposo)", "MALTA REAL (Cocimiento)"])

with tab_cervezas:
    st.markdown("""
        <div style="border-left: 4px solid #333333; padding: 12px 16px; margin-top: 10px; background-color: #0a0a0a;">
            <span style="color: #888888; font-weight: 700; font-family: 'Space Grotesk', sans-serif;">[SISTEMA]</span> 
            <span style="color: #e0e0e0; font-family: 'Space Grotesk', sans-serif; margin-left: 8px;">Interfaz lista. Esperando inyección de lógica de datos para Amstel, Schneider y Capital.</span>
        </div>
    """, unsafe_allow_html=True)

with tab_malta:
    st.markdown("""
        <div style="border-left: 4px solid #333333; padding: 12px 16px; margin-top: 10px; background-color: #0a0a0a;">
            <span style="color: #888888; font-weight: 700; font-family: 'Space Grotesk', sans-serif;">[SISTEMA]</span> 
            <span style="color: #e0e0e0; font-family: 'Space Grotesk', sans-serif; margin-left: 8px;">Interfaz lista. Esperando inyección de lógica de datos y fechas base para Malta Real.</span>
        </div>
    """, unsafe_allow_html=True)
