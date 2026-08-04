import streamlit as st
from utils.core import aplicar_estilo_neon

st.set_page_config(page_title="BBO HUB", layout="wide", page_icon="🟢")
aplicar_estilo_neon()

# Título principal replicando el diseño de la imagen de referencia
st.markdown("""
    <div style="margin-top: 4rem; margin-bottom: 4rem;">
        <p style="color: #a3ff00; font-weight: 600; letter-spacing: 2px; margin-bottom: 0;">HUB BBO</p>
        <h1 style="font-size: 5rem; font-weight: 700; margin-bottom: 0; line-height: 1.1; color: #ffffff;">
            Seguridad Primero<br><span style="color: #a3ff00;">Calidad Siempre.</span>
        </h1>
        <p style="color: #888888; font-size: 1.1rem; margin-top: 1.5rem; max-width: 600px; line-height: 1.6;">
            Plataforma integral para el monitoreo de calidad, análisis de parámetros críticos y visualización de datos gerenciales de la planta.
        </p>
    </div>
""", unsafe_allow_html=True)

st.info("💡 Utiliza el menú lateral izquierdo para acceder a los módulos activos. Haz clic en **1 Parametros** para comenzar.")

st.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 3rem; margin-bottom: 3rem;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("<h3 style='color: #ffffff;'>📈 Waterfall Charts</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888888;'>Control de mermas y balances de volumen a lo largo del proceso. <i>(Próximamente)</i></p>", unsafe_allow_html=True)
with col2:
    st.markdown("<h3 style='color: #ffffff;'>📊 Dashboards Gerenciales</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888888;'>Resumen consolidado de KPIs para toma de decisiones directivas. <i>(Próximamente)</i></p>", unsafe_allow_html=True)