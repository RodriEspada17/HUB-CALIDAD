import streamlit as st
import pandas as pd

# Configuración básica de la página
st.set_page_config(page_title="HUB Calidad", layout="wide")

st.title("📊 HUB de Calidad - Panel Principal")

# --- CONEXIÓN A GOOGLE SHEETS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQCriJBdoyfoDXqQmV0HYZoP1HVETaWLfu009TCGx_x20Ya_DyzOatYAVzM4fBk2vg8vOHx4kn6G1wj/pub?output=csv" 

@st.cache_data(ttl=60) # Actualiza los datos cada 60 segundos
def cargar_datos(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        return None

df = cargar_datos(URL_CSV)

if df is not None:
    st.success("¡Conexión exitosa! Tus datos de Google Sheets están en línea. 🚀")
    
    # Mostramos una tabla con los datos
    st.subheader("Vista previa de los datos:")
    st.dataframe(df)

    st.write("---")
    st.info("Siguiente paso: Aquí irán los gráficos Waterfall, Histogramas y cálculo de Cp/Cpk.")
else:
    st.error("Error al cargar los datos. Revisa que el enlace sea el correcto.")