import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re

# Configuración del HUB
st.set_page_config(page_title="HUB Calidad BBO", layout="wide", page_icon="🍺")

st.title("🍺 HUB de Control de Calidad")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración y Filtros")

url_ingresada = st.sidebar.text_input(
    "Enlace de Google Sheets:",
    value="https://docs.google.com/spreadsheets/d/1YiYwKJZsR7vBrLjCQBbGxzVxlTQEBRJVZEezJyQK3Yw/edit?pli=1&gid=1587615990#gid=1587615990"
)

PESTANAS = {
    "Cocimiento": "1587615990",
    "Fin de Reposo": "79058483",
    "Filtración": "343087732",
    "Producto Terminado": "181144280"
}

etapa_seleccionada = st.sidebar.selectbox("Selecciona la Etapa del Proceso:", list(PESTANAS.keys()))
gid_actual = PESTANAS[etapa_seleccionada]

def generar_url_csv(url, gid):
    if not url:
        return ""
    if "pub?" in url or "output=csv" in url:
        return url
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        sheet_id = match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return url

URL_CSV = generar_url_csv(url_ingresada, gid_actual)

@st.cache_data(ttl=15)
def cargar_datos(url):
    try:
        df_raw = pd.read_csv(url)
        
        # Convertir todos los nombres de columnas iniciales a texto seguro
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        header_idx = None
        for i, row in df_raw.iterrows():
            # Convertir cada celda de la fila a string seguro
            row_str = [str(val).upper() for val in row.values]
            if any("PRODUCTO" in item or "FECHA" in item or "PH" in item or "LOTE" in item for item in row_str):
                header_idx = i
                break
        
        if header_idx is not None:
            df = pd.read_csv(url, skiprows=header_idx + 1)
            df.columns = [str(col).strip() for col in df.columns]
            return df, None
        return df_raw, None
    except Exception as e:
        return None, str(e)

df, error_msg = cargar_datos(URL_CSV)

if df is not None and not df.empty:
    # Asegurar que todas las columnas sean texto
    df.columns = [str(c).strip() for c in df.columns]
    
    st.success(f"¡Conexión exitosa! Datos cargados para **{etapa_seleccionada}** 🚀")
    
    # Filtro dinámico por Cerveza / Producto
    col_prod = [c for c in df.columns if "PRODUCTO" in str(c).upper()]
    if col_prod:
        lista_productos = ["Todos"] + list(df[col_prod[0]].dropna().astype(str).unique())
        prod_sel = st.sidebar.selectbox("Filtrar por Cerveza:", lista_productos)
        if prod_sel != "Todos":
            df = df[df[col_prod[0]].astype(str) == prod_sel]

    tab_datos, tab_spc = st.tabs(["📋 Datos Brutos", "📊 Control Estadístico (Cp & Cpk)"])

    with tab_datos:
        st.subheader(f"Vista de Datos - {etapa_seleccionada}")
        st.dataframe(df, use_container_width=True)

    with tab_spc:
        st.subheader("Capacidad de Proceso ($C_p$ y $C_{pk}$)")
        
        cols_num = []
        for col in df.columns:
            converted = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
            if converted.notna().sum() > 3:
                cols_num.append(col)

        if cols_num:
            var_analizar = st.selectbox("Selecciona la variable (ej. pH, Amargo, Extracto):", cols_num)
            datos_clean = pd.to_numeric(df[var_analizar].astype(str).str.replace(',', '.'), errors='coerce').dropna()

            if len(datos_clean) > 0:
                col_a, col_b = st.columns(2)
                with col_a:
                    lsl = st.number_input("Límite Inferior (LSL):", value=float(datos_clean.min()))
                with col_b:
                    usl = st.number_input("Límite Superior (USL):", value=float(datos_clean.max()))

                if lsl < usl:
                    media = datos_clean.mean()
                    sigma = datos_clean.std()

                    if sigma > 0:
                        cp = (usl - lsl) / (6 * sigma)
                        cpk_lower = (media - lsl) / (3 * sigma)
                        cpk_upper = (usl - media) / (3 * sigma)
                        cpk = min(cpk_lower, cpk_upper)

                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric("Media (µ)", f"{media:.3f}")
                        k2.metric("Desv. Estándar (σ)", f"{sigma:.3f}")
                        k3.metric("Índice Cp", f"{cp:.2f}")
                        k4.metric("Índice Cpk", f"{cpk:.2f}", delta="OK" if cpk >= 1.33 else "Revisar", delta_color="normal" if cpk >= 1.33 else "inverse")

                        fig = px.histogram(datos_clean, x=var_analizar, nbins=20, title=f"Distribución de {var_analizar}", marginal="box")
                        fig.add_vline(x=lsl, line_dash="dash", line_color="red", annotation_text="LSL")
                        fig.add_vline(x=usl, line_dash="dash", line_color="red", annotation_text="USL")
                        fig.add_vline(x=media, line_color="green", annotation_text="Media")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("La desviación estándar es 0.")
            else:
                st.info("No hay variables numéricas con suficientes datos válidos en esta vista.")
        else:
            st.info("No se detectaron variables numéricas en esta tabla.")

else:
    st.error("⚠️ No se pudieron cargar los datos de Google Sheets.")
    if error_msg:
        st.caption(f"Detalle del error técnico: `{error_msg}`")