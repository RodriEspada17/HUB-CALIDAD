import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuración del HUB
st.set_page_config(page_title="HUB Calidad BBO", layout="wide", page_icon="🍺")

st.title("🍺 HUB de Control de Calidad")

# ID de tu documento de Google Sheets
SHEET_ID = "1YYwKl7sR7vBrJcQBbGxVxITQE8RlV7EezlyQK3Yw"

# Diccionario con las pestañas y sus GIDs
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
@st.cache_data(ttl=60)
def cargar_y_limpiar_datos(url):
    try:
        # Leemos el CSV
        df_raw = pd.read_csv(url)
        
        # Buscamos la fila donde realmente empiezan los encabezados (donde dice 'Producto' o 'Fecha')
        header_row_idx = None
        for i, row in df_raw.iterrows():
            row_str = row.astype(str).str.upper().values
            if any("PRODUCTO" in item or "FECHA" in item or "PH" in item for item in row_str):
                header_row_idx = i
                break
        
        if header_row_idx is not None:
            # Reasignamos los encabezados
            df = pd.read_csv(url, skiprows=header_row_idx + 1)
            df.columns = [str(col).strip() for col in df.columns]
            return df
        return df_raw
    except Exception as e:
        st.error(f"Error al cargar la pestaña: {e}")
        return None

df = cargar_y_limpiar_datos(URL_CSV)

if df is not None and not df.empty:
    # Filtro por Producto si la columna existe
    col_producto = [c for c in df.columns if "PRODUCTO" in c.upper()]
    if col_producto:
        productos = ["Todos"] + list(df[col_producto[0]].dropna().unique())
        prod_selected = st.sidebar.selectbox("Filtrar por Cerveza / Producto:", productos)
        if prod_selected != "Todos":
            df = df[df[col_producto[0]] == prod_selected]

    # --- PESTAÑAS PRINCIPALES DEL DASHBOARD ---
    tab_datos, tab_spc = st.tabs(["📋 Datos Brutos", "📊 Control Estadístico (Cp & Cpk)"])

    with tab_datos:
        st.subheader(f"Datos Registrados - {etapa_seleccionada}")
        st.dataframe(df, use_container_width=True)

    with tab_spc:
        st.subheader("Cálculo de Capacidad de Proceso ($C_p$ y $C_{pk}$)")
        
        # Filtrar solo columnas numéricas para análisis
        cols_numericas = []
        for col in df.columns:
            # Intentar convertir a número
            converted = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
            if converted.notna().sum() > 5: # Si tiene al menos 5 valores numéricos válidos
                cols_numericas.append(col)

        if cols_numericas:
            col_analizar = st.selectbox("Selecciona la variable a analizar (ej. pH, Amargo, Extracto):", cols_numericas)
            
            # Limpieza de valores numéricos
            serie_datos = pd.to_numeric(df[col_analizar].astype(str).str.replace(',', '.'), errors='coerce').dropna()

            col_input1, col_input2 = st.columns(2)
            with col_input1:
                lsl = st.number_input("Límite Inferior de Especificación (LSL):", value=float(serie_datos.min()))
            with col_input2:
                usl = st.number_input("Límite Superior de Especificación (USL):", value=float(serie_datos.max()))

            if lsl < usl and len(serie_datos) > 0:
                media = serie_datos.mean()
                sigma = serie_datos.std()

                if sigma > 0:
                    cp = (usl - lsl) / (6 * sigma)
                    cpk_lower = (media - lsl) / (3 * sigma)
                    cpk_upper = (usl - media) / (3 * sigma)
                    cpk = min(cpk_lower, cpk_upper)

                    # Mostrar Métricas en Cajas
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Media ($\mu$)", f"{media:.3f}")
                    m2.metric("Desv. Estándar ($\sigma$)", f"{sigma:.3f}")
                    m3.metric("Índice $C_p$", f"{cp:.2f}")
                    m4.metric("Índice $C_{pk}$", f"{cpk:.2f}", delta="OK" if cpk >= 1.33 else "Bajo Proceso", delta_color="normal" if cpk >= 1.33 else "inverse")

                    # Gráfico de Histogramas y Límites
                    fig = px.histogram(serie_datos, x=col_analizar, nbins=20, title=f"Distribución y Control de {col_analizar}", marginal="box")
                    fig.add_vline(x=lsl, line_dash="dash", line_color="red", annotation_text="LSL")
                    fig.add_vline(x=usl, line_dash="dash", line_color="red", annotation_text="USL")
                    fig.add_vline(x=media, line_color="green", annotation_text="Media")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("La desviación estándar es 0. No se pueden calcular Cp y Cpk.")
        else:
            st.info("No se detectaron columnas numéricas continuas en esta sección.")

else:
    st.error("No se pudieron extraer datos de la hoja seleccionada.")