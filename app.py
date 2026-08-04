import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re

# Configuración del HUB
st.set_page_config(page_title="HUB Calidad BBO", layout="wide", page_icon="🍺")

st.title("🍺 HUB de Control de Calidad")

# --- BARRA LATERAL (CONTROL MAESTRO) ---
st.sidebar.header("⚙️ Control Maestro")

url_ingresada = st.sidebar.text_input(
    "Enlace de Google Sheets:",
    value="https://docs.google.com/spreadsheets/d/1YiYwKJZsR7vBrLjCQBbGxzVxlTQEBRJVZEezJyQK3Yw/edit?pli=1&gid=1990898193#gid=1990898193"
)

PESTANAS = {
    "Cocimiento": "1587615990",
    "Fin de Reposo": "79058483",
    "Filtración": "343087732",
    "Producto Terminado": "181144280"
}

etapa_seleccionada = st.sidebar.selectbox("1. Selecciona la Etapa (Hoja):", list(PESTANAS.keys()))
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
    if not url:
        return None, "No hay URL válida"
    try:
        df_raw = pd.read_csv(url)
        df_raw.columns = [str(col).strip() for col in df_raw.columns]
        
        header_idx = None
        for i, row in df_raw.iterrows():
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

# Variable para saber qué producto estamos viendo
producto_actual = "Todos los productos"

if df is not None and not df.empty:
    df.columns = [str(c).strip() for c in df.columns]
    
    # 2. Filtro dinámico por Cerveza / Producto (Afecta a todo el HUB)
    col_prod = [c for c in df.columns if "PRODUCTO" in str(c).upper()]
    if col_prod:
        lista_productos = ["Todos"] + list(df[col_prod[0]].dropna().astype(str).unique())
        prod_sel = st.sidebar.selectbox("2. Filtrar por Producto (Mosto):", lista_productos)
        if prod_sel != "Todos":
            df = df[df[col_prod[0]].astype(str) == prod_sel]
            producto_actual = prod_sel

    # --- PESTAÑAS PRINCIPALES ---
    tab_datos, tab_spc, tab_tendencias = st.tabs([
        "📋 Datos Brutos", 
        "📊 Cp / Cpk", 
        "📈 Control de Desviaciones"
    ])

    with tab_datos:
        st.subheader(f"Vista de Datos | {etapa_seleccionada} - {producto_actual}")
        st.dataframe(df, use_container_width=True)

    cols_num = []
    for col in df.columns:
        converted = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        if converted.notna().sum() > 3:
            cols_num.append(col)

    with tab_spc:
        st.subheader(f"Análisis de Capacidad | {etapa_seleccionada} ({producto_actual})")
        if cols_num:
            var_analizar = st.selectbox("3. Selecciona el Parámetro a analizar:", cols_num, key="spc_var")
            datos_clean = pd.to_numeric(df[var_analizar].astype(str).str.replace(',', '.'), errors='coerce').dropna()

            if len(datos_clean) > 0:
                col_a, col_b = st.columns(2)
                with col_a:
                    lsl = st.number_input("Límite Inferior (LSL):", value=float(datos_clean.min()), key="spc_lsl")
                with col_b:
                    usl = st.number_input("Límite Superior (USL):", value=float(datos_clean.max()), key="spc_usl")

                if lsl < usl:
                    media = datos_clean.mean()
                    sigma = datos_clean.std()
                    if sigma > 0:
                        cp = (usl - lsl) / (6 * sigma)
                        cpk = min((media - lsl) / (3 * sigma), (usl - media) / (3 * sigma))

                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric("Media (µ)", f"{media:.3f}")
                        k2.metric("Desv. Estándar (σ)", f"{sigma:.3f}")
                        k3.metric("Índice Cp", f"{cp:.2f}")
                        k4.metric("Índice Cpk", f"{cpk:.2f}", delta="OK" if cpk >= 1.33 else "Revisar", delta_color="normal" if cpk >= 1.33 else "inverse")

                        # TÍTULO DINÁMICO
                        titulo_spc = f"Distribución de {var_analizar} en {etapa_seleccionada} ({producto_actual})"
                        fig_hist = px.histogram(datos_clean, x=var_analizar, nbins=20, title=titulo_spc, marginal="box")
                        fig_hist.add_vline(x=lsl, line_dash="dash", line_color="red", annotation_text="LSL")
                        fig_hist.add_vline(x=usl, line_dash="dash", line_color="red", annotation_text="USL")
                        fig_hist.add_vline(x=media, line_color="green", annotation_text="Media")
                        st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Faltan datos válidos.")
        else:
            st.info("No hay columnas numéricas.")

    with tab_tendencias:
        st.subheader(f"Control de Desviaciones por Lote | {etapa_seleccionada} ({producto_actual})")
        if cols_num:
            var_tend = st.selectbox("3. Selecciona el Parámetro para Gráfico de Control:", cols_num, key="tend_var")
            
            posibles_x = [c for c in df.columns if "LOTE" in str(c).upper() or "FECHA" in str(c).upper()]
            eje_x = st.selectbox("Eje X (Lote/Fecha):", posibles_x if posibles_x else df.columns, index=0 if posibles_x else 0)

            df_trend = df.copy()
            df_trend[var_tend] = pd.to_numeric(df_trend[var_tend].astype(str).str.replace(',', '.'), errors='coerce')
            df_trend = df_trend.dropna(subset=[var_tend])

            if len(df_trend) > 0:
                media_t = df_trend[var_tend].mean()
                sigma_t = df_trend[var_tend].std()
                
                ucl = media_t + (3 * sigma_t)
                lcl = media_t - (3 * sigma_t)

                # TÍTULO DINÁMICO
                titulo_tendencia = f"Control Lote a Lote: {var_tend} - {etapa_seleccionada} ({producto_actual})"
                fig_trend = px.line(df_trend, x=eje_x, y=var_tend, markers=True, title=titulo_tendencia)
                
                fig_trend.add_hline(y=media_t, line_color="green", annotation_text="Media Central")
                fig_trend.add_hline(y=ucl, line_dash="dot", line_color="red", annotation_text="Límite Superior +3σ")
                fig_trend.add_hline(y=lcl, line_dash="dot", line_color="red", annotation_text="Límite Inferior -3σ")

                fig_trend.update_traces(line=dict(color="royalblue", width=2), marker=dict(size=8))
                
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning("No hay suficientes datos válidos para graficar.")
        else:
            st.info("No hay columnas numéricas.")

else:
    st.error("⚠️ No se pudieron cargar los datos de Google Sheets. Verifica el enlace.")