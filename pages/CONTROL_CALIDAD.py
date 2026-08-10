import streamlit as st
import pandas as pd
import plotly.express as px
from utils.core import aplicar_estilo_neon, obtener_limites, generar_url_csv, cargar_datos

# Forzamos que la barra lateral empiece EXPANDIDA
st.set_page_config(page_title="Parámetros Críticos", layout="wide", page_icon="▪️", initial_sidebar_state="expanded")
aplicar_estilo_neon()

# --- SIDEBAR: NAVEGACIÓN Y FILTROS ---
# Ahora te damos dos botones para navegar fácilmente por los menús
st.sidebar.page_link("app.py", label="INICIO")
st.sidebar.page_link("pages/CONTROL_CALIDAD.py", label="◀ VOLVER A CALIDAD")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='color: #a3ff00; font-size: 1.1rem; letter-spacing: 1px;'>⯈ FILTROS DE DATOS</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 0.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

st.markdown("""
    <style>
    .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-top: 2rem; margin-bottom: 3rem; }
    .vercel-card { background-color: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 12px; padding: 24px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; text-decoration: none !important; display: flex; flex-direction: column; gap: 12px; min-height: 200px; cursor: pointer; }
    .vercel-card:hover { border-color: #a3ff00; box-shadow: 0 10px 40px -10px rgba(163, 255, 0, 0.3); transform: translateY(-4px); }
    .card-icon { color: #a3ff00; font-size: 1.2rem; font-weight: 800; letter-spacing: 3px; font-family: monospace; }
    .card-title { color: #ffffff; font-size: 1.3rem; font-weight: 700; margin: 0; font-family: 'Space Grotesk', sans-serif; }
    .card-desc { color: #888888; font-size: 0.95rem; margin: 0; line-height: 1.6; }
    .status-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-top: auto; width: fit-content; letter-spacing: 0.5px; text-transform: uppercase; }
    .status-active { background-color: rgba(74, 222, 128, 0.1); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.2); }
    .status-dev { background-color: rgba(250, 204, 21, 0.05); color: #888888; border: 1px solid rgba(250, 204, 21, 0.2); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-transform: uppercase; font-size: 2.2rem; color: #ffffff;'>DEPARTAMENTO / <span style='color: #a3ff00;'>CONTROL DE CALIDAD</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 1.1rem; margin-bottom: 2rem;'>Selecciona la herramienta o módulo que deseas operar:</p>", unsafe_allow_html=True)

st.markdown("""
    <div class="grid-container">
        <!-- 1. Enlace al módulo de Parámetros que ya creamos -->
        <a href="PARAMETROS_CRITICOS" target="_self" class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Control de Parámetros Críticos</h3>
            <p class="card-desc">Análisis SPC, tendencias y resumen de producción mensual.</p>
            <div class="status-badge status-active">■ Módulo Activo</div>
        </a>
        
        <!-- 2. Futuro: Ingreso de Datos -->
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Ingreso de Datos al HUB</h3>
            <p class="card-desc">Carga directa de variables fisicoquímicas sin usar Google Sheets.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
        
        <!-- 3. Futuro: Calculadora -->
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Calculadora de Diacetilo</h3>
            <p class="card-desc">Herramienta predictiva y de ajuste analítico para tiempos de reposo.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
        
        <!-- 4. Futuro: WhatsApp -->
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Reportes por WhatsApp</h3>
            <p class="card-desc">Envío automatizado de alarmas SPC y resúmenes diarios a gerencia.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
    </div>
""", unsafe_allow_html=True)
