import streamlit as st
from utils.core import aplicar_estilo_neon

st.set_page_config(page_title="BBO N30N HUB", layout="wide", page_icon="⚡")
aplicar_estilo_neon()

st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-top: 20px;'>⚡ BBO N30N HUB ⚡</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ff00ff; font-size: 1.2rem; margin-bottom: 50px;'>SISTEMA CENTRAL DE CONTROL Y GESTIÓN DE CALIDAD</p>", unsafe_allow_html=True)

st.info("👈 Utiliza el menú lateral izquierdo para acceder a los módulos activos. Haz clic en **1 Parametros** para comenzar.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🚧 Próximamente: Waterfall Charts")
    st.caption("Control de mermas y balances de volumen a lo largo del proceso.")
with col2:
    st.markdown("### 🚧 Próximamente: Dashboards Gerenciales")
    st.caption("Resumen consolidado de KPIs para toma de decisiones.")
