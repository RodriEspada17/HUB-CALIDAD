import streamlit as st
import base64
import os
from utils.core import aplicar_estilo_neon

st.set_page_config(page_title="BBO HUB", layout="wide", page_icon="🟢")
aplicar_estilo_neon()

# Función para leer la imagen y convertirla a código para inyectarla en CSS
def obtener_imagen_base64(ruta_archivo):
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

st.markdown("""
    <div style="margin-top: 2rem; margin-bottom: 2rem;">
        <p style="color: #a3ff00; font-weight: 600; letter-spacing: 2px; margin-bottom: 0;">BBO HUB PRESENTATION</p>
        <h1 style="font-size: 5rem; font-weight: 700; margin-bottom: 0; line-height: 1.1; color: #ffffff;">
            Seguridad Primero<br><span style="color: #a3ff00;">Calidad Siempre.</span>
        </h1>
        <p style="color: #888888; font-size: 1.1rem; margin-top: 1.5rem; max-width: 600px; line-height: 1.6;">
            Plataforma integral para el monitoreo de calidad, análisis de parámetros críticos y visualización de datos gerenciales de la planta.
        </p>
    </div>
""", unsafe_allow_html=True)

# Integración de la Imagen con efecto de desvanecimiento (Vignette Fade)
img_b64 = obtener_imagen_base64("BBO.jpeg")

if img_b64:
    st.markdown(f"""
        <div style="
            width: 100%;
            height: 450px;
            margin-top: 3rem;
            border-radius: 12px;
            background-image: 
                linear-gradient(to bottom, #050505 0%, rgba(5,5,5,0) 20%, rgba(5,5,5,0) 80%, #050505 100%),
                linear-gradient(to right, #050505 0%, rgba(5,5,5,0) 15%, rgba(5,5,5,0) 85%, #050505 100%),
                url('data:image/jpeg;base64,{img_b64}');
            background-size: cover;
            background-position: center;
            opacity: 0.85;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        "></div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró la foto. Asegúrate de que 'image_aec8a5.jpg' esté subida a la carpeta principal de tu GitHub.")