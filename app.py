import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re
import unicodedata

# Configuración del HUB
st.set_page_config(page_title="HUB Calidad BBO", layout="wide", page_icon="🍺")

st.title("🍺 HUB de Control de Calidad Avanzado")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Control Maestro")
url_ingresada = st.sidebar.text_input("Enlace de Google Sheets:", value="https://docs.google.com/spreadsheets/d/1YiYwKJZsR7vBrLjCQBbGxzVxlTQEBRJVZEezJyQK3Yw/edit?pli=1&gid=1990898193#gid=1990898193")

PESTANAS = {
    "Cocimiento": "1587615990",
    "Fin de Reposo": "79058483",
    "Filtración": "343087732",
    "Producto Terminado": "181144280"
}
etapa_seleccionada = st.sidebar.selectbox("1. Selecciona la Etapa:", list(PESTANAS.keys()))
gid_actual = PESTANAS[etapa_seleccionada]

# =====================================================================
# 📚 DICCIONARIO MAESTRO POR ETAPAS (Con excepciones de Planta)
# =====================================================================

SPECS_CCR_REPOSO = {
    "EXTRACTO": (14.0, 15.0), "EO": (14.0, 15.0), "EXTRACTO ORIGINAL": (14.0, 15.0),
    "EA": (2.70, 3.30), "EXTRACTO APARENTE": (2.70, 3.30),
    "ALCOHOL": (5.80, 6.40), "ALC": (5.80, 6.40),
    "COLOR": (5.90, 8.90), "AMARGO": (9.50, 13.50), "PH": (3.95, 4.45),
    "TURBIDEZ": (0, 30.0), "DIACETILO": (0, 100.0)
}

SPECS_CCR_PT = {
    "EXTRACTO ORIGINAL": (10.0, 10.60), "EO": (10.0, 10.60),
    "EXTRACTO APARENTE": (1.80, 2.40), "EA": (1.80, 2.40),
    "EXTRACTO REAL": (3.30, 3.90), "ER": (3.30, 3.90),
    "ALCOHOL EN VOLUMEN": (4.00, 4.60), "ALCOHOL EN PESO": (3.10, 3.70),
    "COLOR": (3.00, 6.00), "AMARGO": (6.00, 10.00), "PH": (3.95, 4.45),
    "TURBIDEZ": (0, 3.50), "DIACETILO": (0, 50.0), "FAN": (0, 90.0),
    "HIERRO": (0, 0.20), "ESPUMA": (205, 999), "CARBONATACION": (4.80, 5.40),
    "OXIGENO": (0, 40), "TPO": (0, 100), "PASTEURIZACION": (10, 50)
}

# EXCEPCIÓN MALTA REAL: El EO en cocimiento anota el valor de EA.
SPECS_MALTA_REPOSO = {
    "EXTRACTO ORIGINAL": (14.4, 15.3), "EO": (14.4, 15.3), "EXTRACTO": (14.4, 15.3),
    "EXTRACTO APARENTE": (14.4, 15.3), "EA": (14.4, 15.3),
    "ALCOHOL": (0, 0.50), "ALC": (0, 0.50), "COLOR": (108.0, 148.0), 
    "AMARGO": (7.50, 10.50), "PH": (4.15, 4.65), "TURBIDEZ": (0, 50.0)
}

SPECS_MALTA_PT = {
    "EXTRACTO APARENTE": (12.80, 13.40), "EA": (12.80, 13.40),
    "EXTRACTO ORIGINAL": (12.80, 13.40), "EO": (12.80, 13.40), # Por si usan la misma maña en PT
    "ALCOHOL EN VOLUMEN": (0, 0.50), "COLOR": (100.0, 140.0), "AMARGO": (6.50, 9.50), 
    "PH": (4.15, 4.65), "HIERRO": (0, 0.20), "ESPUMA": (180, 999), "CARBONATACION": (4.80, 5.40),
    "OXIGENO": (0, 120), "TPO": (0, 300), "PASTEURIZACION": (35, 80)
}

ESPECIFICACIONES = {
    "COCIMIENTO_REPOSO": {
        "AMSTEL": {
            "EXTRACTO": (10.8, 11.8), "EO": (10.8, 11.8), "EXTRACTO ORIGINAL": (10.8, 11.8),
            "EA": (1.80, 2.40), "EXTRACTO APARENTE": (1.80, 2.40),
            "ALCOHOL": (4.80, 5.40), "ALC": (4.80, 5.40), "COLOR": (5.60, 8.60), 
            "AMARGO": (10.20, 14.20), "PH": (4.15, 4.65), "TURBIDEZ": (0, 30.0), "DIACETILO": (0, 50.0)
        },
        "SCHNEIDER": {
            "EXTRACTO": (11.3, 12.1), "EO": (11.3, 12.1), "EXTRACTO ORIGINAL": (11.3, 12.1),
            "EA": (1.70, 2.30), "EXTRACTO APARENTE": (1.70, 2.30),
            "ALCOHOL": (4.90, 5.40), "ALC": (4.90, 5.40), "COLOR": (7.20, 9.20), 
            "AMARGO": (12.00, 16.00), "PH": (4.00, 4.70), "TURBIDEZ": (0, 30.0), "DIACETILO": (0, 50.0)
        },
        "MALTA REAL": SPECS_MALTA_REPOSO,
        "MALTA": SPECS_MALTA_REPOSO, # Alias para abarcar ambos nombres
        "CAPITAL": SPECS_CCR_REPOSO,
        "CORDILLERA": SPECS_CCR_REPOSO,
        "REAL": SPECS_CCR_REPOSO
    },
    "FILTRACION_PT": {
        "AMSTEL": {
            "EXTRACTO ORIGINAL": (9.90, 10.50), "EO": (9.90, 10.50),
            "EXTRACTO APARENTE": (1.60, 2.20), "EA": (1.60, 2.20),
            "EXTRACTO REAL": (3.20, 3.80), "ER": (3.20, 3.80),
            "ALCOHOL EN VOLUMEN": (4.30, 4.90), "ALCOHOL EN PESO": (3.30, 3.90),
            "COLOR": (4.00, 7.00), "AMARGO": (9.00, 13.00), "PH": (4.15, 4.65),
            "TURBIDEZ": (0, 3.50), "DIACETILO": (0, 40.0), "FAN": (0, 90.0),
            "HIERRO": (0, 0.20), "ESPUMA": (225, 999), "CARBONATACION": (4.80, 5.40),
            "OXIGENO": (0, 40), "TPO": (0, 100), "PASTEURIZACION": (10, 50)
        },
        "SCHNEIDER": {
            "EXTRACTO ORIGINAL": (10.70, 11.00), "EO": (10.70, 11.00),
            "EXTRACTO APARENTE": (1.52, 2.12), "EA": (1.52, 2.12),
            "EXTRACTO REAL": (3.20, 3.90), "ER": (3.20, 3.90),
            "ALCOHOL EN VOLUMEN": (4.49, 4.99), "ALCOHOL EN PESO": (3.42, 4.02),
            "COLOR": (6.00, 7.50), "AMARGO": (11.00, 15.00), "PH": (4.00, 4.70),
            "TURBIDEZ": (0, 3.50), "DIACETILO": (0, 40.0), "FAN": (0, 90.0),
            "HIERRO": (0, 0.20), "ESPUMA": (205, 999), "CARBONATACION": (4.80, 5.40),
            "OXIGENO": (0, 40), "TPO": (0, 100), "PASTEURIZACION": (10, 50)
        },
        "MALTA REAL": SPECS_MALTA_PT,
        "MALTA": SPECS_MALTA_PT,
        "CAPITAL": SPECS_CCR_PT,
        "CORDILLERA": SPECS_CCR_PT,
        "REAL": SPECS_CCR_PT
    }
}

def normalizar_texto(texto):
    texto = str(texto).upper().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def obtener_limites(etapa, producto, parametro):
    if etapa in ["Cocimiento", "Fin de Reposo"]:
        diccionario_etapa = ESPECIFICACIONES["COCIMIENTO_REPOSO"]
    else:
        diccionario_etapa = ESPECIFICACIONES["FILTRACION_PT"]

    prod_norm = normalizar_texto(producto)
    param_norm = normalizar_texto(parametro)
    
    prod_key = next((k for k in diccionario_etapa.keys() if k == prod_norm or k in prod_norm), None)
    if prod_key:
        for key_param, limites in diccionario_etapa[prod_key].items():
            if key_param == param_norm or key_param in param_norm:
                return limites[0], limites[1]
    return None, None

# --- FUNCIONES DE CARGA Y LIMPIEZA ---
def generar_url_csv(url, gid):
    if not url: return ""
    if "pub?" in url or "output=csv" in url: return url
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match: return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv&gid={gid}"
    return url

URL_CSV = generar_url_csv(url_ingresada, gid_actual)

@st.cache_data(ttl=15)
def cargar_datos(url):
    try:
        df_raw = pd.read_csv(url)
        header_idx = None
        for i, row in df_raw.iterrows():
            if any("PRODUCTO" in str(val).upper() or "LOTE" in str(val).upper() for val in row.values):
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
producto_actual = "Todos"

if df is not None and not df.empty:
    col_prod = [c for c in df.columns if "PRODUCTO" in str(c).upper()]
    if col_prod:
        lista_productos = ["Todos"] + list(df[col_prod[0]].dropna().astype(str).unique())
        prod_sel = st.sidebar.selectbox("2. Filtrar por Producto (Mosto):", lista_productos)
        if prod_sel != "Todos":
            df = df[df[col_prod[0]].astype(str) == prod_sel]
            producto_actual = prod_sel

    # --- FUNCIÓN DE SEMAFORIZACIÓN PARA LA TABLA ---
    def pintar_celdas(val, lsl, usl):
        try:
            v = float(str(val).replace(',', '.'))
            if lsl is not None and usl is not None:
                if v < lsl or v > usl:
                    return 'background-color: #ffcccc; color: #990000;'
                else:
                    return 'background-color: #ccffcc; color: #006600;'
        except:
            pass
        return ''

    def aplicar_semaforo(row):
        estilos = [''] * len(row)
        if producto_actual != "Todos":
            for i, col in enumerate(row.index):
                lsl, usl = obtener_limites(etapa_seleccionada, producto_actual, col)
                if lsl is not None:
                    estilos[i] = pintar_celdas(row[col], lsl, usl)
        return estilos

    tab_datos, tab_spc, tab_tendencias = st.tabs(["📋 Datos Brutos", "📊 Cp / Cpk", "📈 Control de Desviaciones"])

    with tab_datos:
        st.subheader(f"Vista de Datos | {etapa_seleccionada} - {producto_actual}")
        if producto_actual != "Todos":
            df_styled = df.style.apply(aplicar_semaforo, axis=1)
            st.dataframe(df_styled, use_container_width=True)
            st.caption("🟢 Verde: Dentro de Especificación | 🔴 Rojo: Fuera de Especificación")
        else:
            st.dataframe(df, use_container_width=True)
            st.info("💡 Selecciona un Producto específico en la barra lateral para ver la semaforización por colores.")

    cols_num = [col for col in df.columns if pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').notna().sum() > 3]

    with tab_spc:
        st.subheader(f"Análisis de Capacidad | {etapa_seleccionada} ({producto_actual})")
        if cols_num:
            var_analizar = st.selectbox("3. Parámetro a analizar:", cols_num, key="spc_var")
            datos_clean = pd.to_numeric(df[var_analizar].astype(str).str.replace(',', '.'), errors='coerce').dropna()
            
            lsl_auto, usl_auto = obtener_limites(etapa_seleccionada, producto_actual, var_analizar) if producto_actual != "Todos" else (None, None)
            
            col_a, col_b = st.columns(2)
            with col_a:
                lsl = st.number_input("LSL:", value=float(lsl_auto if lsl_auto is not None else datos_clean.min()))
            with col_b:
                usl = st.number_input("USL:", value=float(usl_auto if usl_auto is not None else datos_clean.max()))

            if lsl < usl and len(datos_clean) > 0:
                media, sigma = datos_clean.mean(), datos_clean.std()
                if sigma > 0:
                    cp = (usl - lsl) / (6 * sigma)
                    cpk = min((media - lsl) / (3 * sigma), (usl - media) / (3 * sigma))
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Media", f"{media:.3f}")
                    c2.metric("Sigma", f"{sigma:.3f}")
                    c3.metric("Cp", f"{cp:.2f}")
                    c4.metric("Cpk", f"{cpk:.2f}", delta="OK" if cpk >= 1.33 else "Bajo Proceso", delta_color="normal" if cpk >= 1.33 else "inverse")

                    fig_hist = px.histogram(datos_clean, x=var_analizar, nbins=20, title=f"Distribución de {var_analizar}", marginal="box")
                    fig_hist.add_vline(x=lsl, line_dash="dash", line_color="red", annotation_text="LSL")
                    fig_hist.add_vline(x=usl, line_dash="dash", line_color="red", annotation_text="USL")
                    st.plotly_chart(fig_hist, use_container_width=True)

    with tab_tendencias:
        st.subheader(f"Control de Desviaciones | {etapa_seleccionada} ({producto_actual})")
        if cols_num:
            var_tend = st.selectbox("3. Parámetro para Gráfico:", cols_num, key="tend_var")
            posibles_x = [c for c in df.columns if "LOTE" in str(c).upper() or "FECHA" in str(c).upper()]
            eje_x = st.selectbox("Eje X:", posibles_x if posibles_x else df.columns, index=0 if posibles_x else 0)

            df_trend = df.copy()
            df_trend[var_tend] = pd.to_numeric(df_trend[var_tend].astype(str).str.replace(',', '.'), errors='coerce')
            df_trend = df_trend.dropna(subset=[var_tend])
            
            lsl_auto, usl_auto = obtener_limites(etapa_seleccionada, producto_actual, var_tend) if producto_actual != "Todos" else (None, None)

            if len(df_trend) > 0:
                fig_trend = px.line(df_trend, x=eje_x, y=var_tend, markers=True, title=f"Tendencia: {var_tend}")
                fig_trend.add_hline(y=df_trend[var_tend].mean(), line_color="green", annotation_text="Media")
                
                if lsl_auto is not None and usl_auto is not None:
                    fig_trend.add_hline(y=usl_auto, line_dash="dot", line_color="red", annotation_text="Spec Máx (USL)")
                    fig_trend.add_hline(y=lsl_auto, line_dash="dot", line_color="red", annotation_text="Spec Mín (LSL)")
                else:
                    st.info("Mostrando límites de control natural (3 Sigma) por falta de especificación manual.")
                    fig_trend.add_hline(y=df_trend[var_tend].mean() + 3*df_trend[var_tend].std(), line_dash="dot", line_color="orange")
                    fig_trend.add_hline(y=df_trend[var_tend].mean() - 3*df_trend[var_tend].std(), line_dash="dot", line_color="orange")

                st.plotly_chart(fig_trend, use_container_width=True)

else:
    st.error("⚠️ No se pudieron cargar los datos.")