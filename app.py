import streamlit as st
import base64
import os
from utils.core import aplicar_estilo_neon

st.set_page_config(page_title="BBO HUB", layout="wide", page_icon="▪️", initial_sidebar_state="collapsed")
aplicar_estilo_neon()

def obtener_imagen_base64(ruta_archivo):
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
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

st.markdown("""
    <div style="margin-top: 2rem; margin-bottom: 2rem;">
        <p style="color: #a3ff00; font-weight: 600; letter-spacing: 2px; margin-bottom: 0;">SISTEMA OPERATIVO CENTRAL</p>
        <h1 style="font-size: 4.5rem; font-weight: 700; margin-bottom: 0; line-height: 1.1; color: #ffffff;">
            Seguridad Primero<br><span style="color: #a3ff00;">Calidad Siempre.</span>
        </h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="grid-container">
        <!-- AQUÍ CAMBIAMOS EL ENLACE A 'CONTROL_CALIDAD' -->
        <a href="CONTROL_CALIDAD" target="_self" class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Control de Calidad</h3>
            <p class="card-desc">Portal de parámetros críticos, ingreso de datos, calculadoras y reportes automatizados.</p>
            <div class="status-badge status-active">■ Módulo Activo</div>
        </a>
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Elaboración</h3>
            <p class="card-desc">Monitoreo de fermentación, maduración, perfiles térmicos y uso de materias primas.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Líneas de Envasado</h3>
            <p class="card-desc">Control de OEE, mermas de empaque, eficiencia de llenadoras y rechazos.</p>
            <div class="status-badge status-dev">■ En Desarrollo</div>
        </div>
        <div class="vercel-card">
            <div class="card-icon">///</div>
            <h3 class="card-title">Mantenimiento</h3>
            <p class="card-desc">Gestión de activos, control de paradas de planta y cumplimiento preventivo.</p>
            <div class="status-badge status-dev">■ Próximamente</div>
        </div>
    </div>
""", unsafe_allow_html=True)

img_b64 = obtener_imagen_base64("BBO.jpeg")

if img_b64:
    st.markdown(f"""
        <div style="
            width: 100%;
            height: 550px;
            margin-top: 1rem;
            border-radius: 12px;
            background-image: 
                linear-gradient(to bottom, #050505 0%, rgba(5,5,5,0) 10%, rgba(5,5,5,0) 90%, #050505 100%),
                linear-gradient(to right, #050505 0%, rgba(5,5,5,0) 10%, rgba(5,5,5,0) 90%, #050505 100%),
                url('data:image/jpeg;base64,{img_b64}');
            background-size: cover;
            background-position: center;
            opacity: 0.85; 
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        "></div>
    """, unsafe_allow_html=True)