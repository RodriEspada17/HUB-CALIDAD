import streamlit as st
from utils.core import aplicar_estilo_neon

# Forzamos que la barra lateral empiece COLAPSADA
st.set_page_config(page_title="Control de Calidad", layout="wide", page_icon="▪️", initial_sidebar_state="collapsed")
aplicar_estilo_neon()

# --- CSS AVANZADO ---
# 1. Ocultamos la barra lateral completamente en este lobby
# 2. Hacemos las tarjetas más pequeñas y compactas
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 1.5rem; margin-bottom: 3rem; }
    .vercel-card { background-color: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 10px; padding: 18px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; text-decoration: none !important; display: flex; flex-direction: column; gap: 8px; min-height: 150px; cursor: pointer; }
    .vercel-card:hover { border-color: #a3ff00; box-shadow: 0 8px 30px -10px rgba(163, 255, 0, 0.3); transform: translateY(-3px); }
    .card-icon { color: #a3ff00; font-size: 1rem; font-weight: 800; letter-spacing: 2px; font-family: monospace; }
    .card-title { color: #ffffff; font-size: 1.1rem; font-weight: 700; margin: 0; font-family: 'Space Grotesk', sans-serif; }
    .card-desc { color: #888888; font-size: 0.85rem; margin: 0; line-height: 1.5; }
    .status-badge { display: inline-block; padding: 4px 10px; border-radius: 15px; font-size: 0.7rem; font-weight: 700; margin-top: auto; width: fit-content; letter-spacing: 0.5px; text-transform: uppercase; }
    .status-active { background-color: rgba(74, 222, 128, 0.1); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.2); }
    .status-dev { background-color: rgba(250, 204, 21, 0.05); color: #888888; border: 1px solid rgba(250, 204, 21, 0.2); }
    </style>
""", unsafe_allow_html=True)

# Botón de regreso nativo en la página principal (ya no en la sidebar)
st.page_link("app.py", label="◀ VOLVER AL INICIO")

st.markdown("<h2 style='text-transform: uppercase; font-size: 2.2rem; color: #ffffff; margin-top: 1rem;'>DEPARTAMENTO / <span style='color: #a3ff00;'>CONTROL DE CALIDAD</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 1rem; margin-bottom: 2rem;'>Selecciona la herramienta o módulo que deseas operar:</p>", unsafe_allow_html=True)

# --- HTML COMPRIMIDO PARA EVITAR EL ERROR ---
st.markdown("""
    <div class="grid-container">
        <a href="PARAMETROS_CRITICOS" target="_self" class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Control de Parámetros Críticos</h3>
            <p class="card-desc">Análisis SPC, tendencias y resumen de producción mensual.</p>
            <div class="status-badge status-active">■ Módulo Activo</div>
        </a>
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Ingreso de Datos al HUB</h3>
            <p class="card-desc">Carga directa de variables fisicoquímicas sin usar Google Sheets.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Calculadora de Diacetilo</h3>
            <p class="card-desc">Herramienta predictiva y de ajuste analítico para tiempos de reposo.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Reportes por WhatsApp</h3>
            <p class="card-desc">Envío automatizado de alarmas SPC y resúmenes diarios a gerencia.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
    </div>
""", unsafe_allow_html=True)