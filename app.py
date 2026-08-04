import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re

# Configuración del HUB
st.set_page_config(page_title="HUB Calidad BBO", layout="wide", page_icon="🍺")

st.title("🍺 HUB de Control de Calidad")

# -----------------------------------------------------------------------------
# 🔗 PEGA AQUÍ LA URL COMPLETA DE TU GOOGLE SHEETS (la de la barra del navegador)
# -----------------------------------------------------------------------------
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1YYwKl7sR7vBrJcQBbGxVxITQE8RlV7EezlyQK3Yw/edit"

# Extractor automático del ID
def extraer_sheet_id(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else url

SHEET_ID = extraer_sheet_id(URL_GOOGLE_SHEETS)

# Diccionario con las pestañas y sus GIDs exactos
PESTANAS = {
    "Cocimiento": "1587615990",
    "Fin de Reposo": "79058483",
    "Filtración": "343087732",
    "Producto Terminado": "181144280"
}

# --- BARRA LATERAL ---
st.sidebar.header("🔍 Navegación y Filtros")
etapa_seleccionada = st.sidebar.selectbox("Selecciona la Etapa del Proceso:", list(PESTANAS.keys()))

gid = PESTANAS[etapa_seleccionada]
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

# --- FUNCIÓN PARA CARGAR Y LIMPIAR DATOS ---
@st.cache_data(ttl=30)
def cargar_y_limpiar_datos(url):
    try:
        df_raw = pd.read_csv(url)
        
        # Buscar la fila donde están los nombres reales de las columnas
        header_row_idx = None
        for i, row in df_raw.iterrows():
            row_str = row.astype(str).str.upper().values
            if any("PRODUCTO" in item or "FECHA" in item or "PH" in item or "LOTE" in item for item in row_str):
                header_row_idx = i
                break
        
        if header_row_idx is not None:
            df = pd.read_csv(url, skiprows=header_row_idx + 1)
            df.columns = [str(col).strip() for col in df.columns]
            return df
        return df_raw
    except Exception as e:
        st.error(f"Error al cargar la pestaña: {e}")
        return None

df = cargar_y_limpiar_datos(URL_CSV)

if df is not None and not df.empty:
    # Filtro dinámico por cerveza / producto si existe la columna
    col_producto = [c for c in df.columns if "PRODUCTO" in c.upper()]
    if col_producto:
        productos = ["Todos"] + list(df[col_producto[0]].dropna().unique())
        prod_selected = st.sidebar.selectbox("Filtrar por Cerveza / Producto:", productos)
        if prod_selected != "Todos":
            df = df[df[col_producto[0]] == prod_selected]

    # --- PESTAÑAS DEL DASHBOARD ---
    tab_datos, tab_spc = st.tabs(["📋 Datos Brutos", "📊 Control Estadístico (Cp & Cpk)"])

    with tab_datos:
        st.subheader(f"Datos Registrados - {etapa_seleccionada}")
        st.dataframe(df, use_container_width=True)

    with tab_spc:
        st.subheader("Cálculo de Capacidad de Proceso ($C_p$ y $C_{pk}$)")
        
        # Identificar columnas numéricas
        cols_numericas = []
        for col in df.columns:
            converted = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
            if converted.notna().sum() > 3:
                cols_numericas.append(col)

        if cols_numericas:
            col_analizar = st.selectbox("Selecciona la variable a analizar:", cols_numericas)
            
            serie_datos = pd.to_numeric(df[col_analizar].astype(str).str.replace(',', '.'), errors='coerce').dropna()

            col_input1, col_input2 = st.columns(2)
            with col_input1:
                lsl = st.number_input("Límite Inferior (LSL):", value=float(serie_datos.min()))
            with col_input2:
                usl = st.number_input("Límite Superior (USL):", value=float(serie_datos.max()))

            if lsl < usl and len(serie_datos) > 0:
                media = serie_datos.mean()
                sigma = serie_datos.std()

                if sigma > 0:
                    cp = (usl - lsl) / (6 * sigma)
                    cpk_lower = (media - lsl) / (3 * sigma)
                    cpk_upper = (usl - media) / (3 * sigma)
                    cpk = min(cpk_lower, cpk_upper)

                    # Indicadores
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Media", f"{media:.3f}")
                    m2.metric("Desv. Estándar", f"{sigma:.3f}")
                    m3.metric("Índice Cp", f"{cp:.2f}")
                    m4.metric("Índice Cpk", f"{cpk:.2f}", delta="OK" if cpk >= 1.33 else "Revisar", delta_color="normal" if cpk >= 1.33 else "inverse")

                    # Gráfica interactiva
                    fig = px.histogram(serie_datos, x=col_analizar, nbins=20, title=f"Distribución de {col_analizar}", marginal="box")
                    fig.add_vline(x=lsl, line_dash="dash", line_color="red", annotation_text="LSL")
                    fig.add_vline(x=usl, line_dash="dash", line_color="red", annotation_text="USL")
                    fig.add_vline(x=media, line_color="green", annotation_text="Media")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Desviación estándar es 0.")
        else:
            st.info("No hay columnas numéricas detectadas en esta vista.")

else:
    st.error("No se pudieron extraer datos de la hoja seleccionada. Verifica el enlace del Google Sheet.")