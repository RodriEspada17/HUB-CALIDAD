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
# 📚 DICCIONARIO MAESTRO SEPARADO POR ETAPAS Exactas
# Formato: (TOL_MIN, TOL_MAX, STD_MIN, STD_MAX)
# =====================================================================

# 1. COCIMIENTO (Solo Extractos)
SPECS_COCIMIENTO_CCR = {"EXTRACTO ORIGINAL": (14.0, 15.0, 14.1, 14.9), "EO": (14.0, 15.0, 14.1, 14.9), "EXTRACTO": (14.0, 15.0, 14.1, 14.9)}
SPECS_COCIMIENTO_MALTA = {"EXTRACTO ORIGINAL": (14.4, 15.3, 14.5, 15.2), "EO": (14.4, 15.3, 14.5, 15.2), "EXTRACTO APARENTE": (14.4, 15.3, 14.5, 15.2), "EA": (14.4, 15.3, 14.5, 15.2)}

# 2. REPOSO (Compartidas Capital, Cordillera, Real)
SPECS_REPOSO_CCR = {
    "EXTRACTO": (14.0, 15.0, 14.1, 14.9), "EO": (14.0, 15.0, 14.1, 14.9), 
    "EA": (2.70, 3.30, 2.80, 3.20), "ALCOHOL": (5.80, 6.40, 5.90, 6.30), "ALC": (5.80, 6.40, 5.90, 6.30),
    "COLOR": (5.90, 8.90, 6.40, 8.40), "AMARGO": (9.50, 13.50, 10.00, 13.00), 
    "PH": (3.95, 4.45, 4.05, 4.35), "TURBIDEZ": (0, 30.0, 0, 30.0), "DIACETILO": (0, 100.0, 0, 100.0)
}
SPECS_REPOSO_MALTA = {
    "EXTRACTO ORIGINAL": (14.4, 15.3, 14.5, 15.2), "EO": (14.4, 15.3, 14.5, 15.2),
    "EXTRACTO APARENTE": (14.4, 15.3, 14.5, 15.2), "EA": (14.4, 15.3, 14.5, 15.2),
    "ALCOHOL": (0, 0.50, 0, 0.20), "COLOR": (108.0, 148.0, 118.0, 138.0), 
    "AMARGO": (7.50, 10.50, 8.00, 10.00), "PH": (4.15, 4.65, 4.25, 4.55)
}

# 3. PT / FILTRACIÓN (Compartidas Capital, Cordillera, Real)
SPECS_PT_CCR = {
    "EXTRACTO ORIGINAL": (10.0, 10.60, 10.10, 10.50), "EO": (10.0, 10.60, 10.10, 10.50),
    "EXTRACTO APARENTE": (1.80, 2.40, 1.90, 2.30), "EA": (1.80, 2.40, 1.90, 2.30),
    "EXTRACTO REAL": (3.30, 3.90, 3.40, 3.80), "ER": (3.30, 3.90, 3.40, 3.80),
    "ALCOHOL EN VOLUMEN": (4.00, 4.60, 4.10, 4.50), "ALCOHOL EN PESO": (3.10, 3.70, 3.20, 3.60),
    "COLOR": (3.00, 6.00, 3.50, 5.50), "AMARGO": (6.00, 10.00, 6.50, 9.50), 
    "PH": (3.95, 4.45, 4.05, 4.35)
}
SPECS_PT_MALTA = {
    "EXTRACTO APARENTE": (12.80, 13.40, 12.90, 13.30), "EA": (12.80, 13.40, 12.90, 13.30),
    "EXTRACTO ORIGINAL": (12.80, 13.40, 12.90, 13.30), "EO": (12.80, 13.40, 12.90, 13.30),
    "AMARGO": (6.50, 9.50, 7.00, 9.00), "PH": (4.15, 4.65, 4.25, 4.55)
}

ESPECIFICACIONES = {
    "COCIMIENTO": {
        "AMSTEL": {"EXTRACTO ORIGINAL": (10.8, 11.8, 10.9, 11.7), "EO": (10.8, 11.8, 10.9, 11.7)},
        "SCHNEIDER": {"EXTRACTO ORIGINAL": (11.3, 12.1, 11.4, 12.0), "EO": (11.3, 12.1, 11.4, 12.0)},
        "MALTA REAL": SPECS_COCIMIENTO_MALTA, "MALTA": SPECS_COCIMIENTO_MALTA,
        "CAPITAL": SPECS_COCIMIENTO_CCR, "CORDILLERA": SPECS_COCIMIENTO_CCR, "REAL": SPECS_COCIMIENTO_CCR
    },
    "FIN_REPOSO": {
        "AMSTEL": {
            "EXTRACTO ORIGINAL": (10.8, 11.8, 10.9, 11.7), "EO": (10.8, 11.8, 10.9, 11.7),
            "EXTRACTO APARENTE": (1.80, 2.40, 1.90, 2.30), "EA": (1.80, 2.40, 1.90, 2.30),
            "ALCOHOL": (4.80, 5.40, 4.90, 5.30), "COLOR": (5.60, 8.60, 6.10, 8.10), 
            "AMARGO": (10.20, 14.20, 10.70, 13.70), "PH": (4.15, 4.65, 4.25, 4.55)
        },
        "SCHNEIDER": {
            "EXTRACTO ORIGINAL": (11.3, 12.1, 11.4, 12.0), "EO": (11.3, 12.1, 11.4, 12.0),
            "EXTRACTO APARENTE": (1.70, 2.30, 1.80, 2.20), "EA": (1.70, 2.30, 1.80, 2.20),
            "ALCOHOL": (4.90, 5.40, 4.95, 5.35), "COLOR": (7.20, 9.20, 7.70, 8.70), 
            "AMARGO": (12.00, 16.00, 13.00, 15.00), "PH": (4.00, 4.70, 4.00, 4.60)
        },
        "MALTA REAL": SPECS_REPOSO_MALTA, "MALTA": SPECS_REPOSO_MALTA,
        "CAPITAL": SPECS_REPOSO_CCR, "CORDILLERA": SPECS_REPOSO_CCR, "REAL": SPECS_REPOSO_CCR
    },
    "FILTRACION_PT": {
        "AMSTEL": {
            "EXTRACTO ORIGINAL": (9.90, 10.50, 10.0, 10.40), "EO": (9.90, 10.50, 10.0, 10.40),
            "EXTRACTO APARENTE": (1.60, 2.20, 1.70, 2.10), "EA": (1.60, 2.20, 1.70, 2.10),
            "EXTRACTO REAL": (3.20, 3.80, 3.30, 3.70), "ER": (3.20, 3.80, 3.30, 3.70),
            "COLOR": (4.00, 7.00, 4.50, 6.50), "AMARGO": (9.00, 13.00, 9.50, 12.50), 
            "PH": (4.15, 4.65, 4.25, 4.55)
        },
        "SCHNEIDER": {
            "EXTRACTO ORIGINAL": (10.70, 11.00, 10.70, 10.90), "EO": (10.70, 11.00, 10.70, 10.90),
            "EXTRACTO APARENTE": (1.52, 2.12, 1.62, 2.02), "EA": (1.52, 2.12, 1.62, 2.02),
            "EXTRACTO REAL": (3.20, 3.90, 3.30, 3.80), "ER": (3.20, 3.90, 3.30, 3.80),
            "COLOR": (6.00, 7.50, 6.00, 7.00), "AMARGO": (11.00, 15.00, 12.00, 14.00), 
            "PH": (4.00, 4.70, 4.00, 4.60)
        },
        "MALTA REAL": SPECS_PT_MALTA, "MALTA": SPECS_PT_MALTA,
        "CAPITAL": SPECS_PT_CCR, "CORDILLERA": SPECS_PT_CCR, "REAL": SPECS_PT_CCR
    }
}

def normalizar_texto(texto):
    texto = str(texto).upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def obtener_limites(etapa, producto, parametro):
    if etapa == "Cocimiento":
        diccionario_etapa = ESPECIFICACIONES["COCIMIENTO"]
    elif etapa == "Fin de Reposo":
        diccionario_etapa = ESPECIFICACIONES["FIN_REPOSO"]
    else:
        diccionario_etapa = ESPECIFICACIONES["FILTRACION_PT"]

    prod_norm = normalizar_texto(producto)
    param_norm = normalizar_texto(parametro)
    
    prod_key = next((k for k in diccionario_etapa.keys() if k == prod_norm or k in prod_norm), None)
    if prod_key:
        for key_param, limites in diccionario_etapa[prod_key].items():
            if key_param == param_norm or key_param in param_norm:
                lsl, usl = limites[0], limites[1]
                std_l = limites[2] if len(limites) > 2 else None
                std_u = limites[3] if len(limites) > 3 else None
                return lsl, usl, std_l, std_u
    return None, None, None, None

# --- CARGA DE DATOS ---
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
        prod_sel = st.sidebar.selectbox("2. Filtrar por Producto:", lista_productos)
        if prod_sel != "Todos":
            df = df[df[col_prod[0]].astype(str) == prod_sel]
            producto_actual = prod_sel

    # --- LÓGICA DE 3 COLORES ---
    def pintar_celdas(val, lsl, usl, std_l, std_u):
        try:
            v = float(str(val).replace(',', '.'))
            if lsl is not None and usl is not None:
                if v < lsl or v > usl: 
                    return 'background-color: #ffcccc; color: #990000;' # ROJO (Fuera TOL)
                elif std_l is not None and std_u is not None:
                    if std_l <= v <= std_u:
                        return 'background-color: #ccffcc; color: #006600;' # VERDE (Dentro STD)
                    else:
                        return 'background-color: #fff2cc; color: #997300;' # AMARILLO (Dentro TOL, pero Fuera de STD)
                else:
                    return 'background-color: #fff2cc; color: #997300;' # AMARILLO (Si solo tiene TOL, no tiene STD)
        except: pass
        return ''

    def aplicar_semaforo(row):
        estilos = [''] * len(row)
        prod_fila = producto_actual
        if prod_fila == "Todos":
            col_p = next((c for c in row.index if "PRODUCTO" in str(c).upper()), None)
            if col_p: prod_fila = str(row[col_p])
            else: return estilos
                
        for i, col in enumerate(row.index):
            lsl, usl, std_l, std_u = obtener_limites(etapa_seleccionada, prod_fila, col)
            if lsl is not None: 
                estilos[i] = pintar_celdas(row[col], lsl, usl, std_l, std_u)
        return estilos

    tab_datos, tab_spc, tab_tendencias = st.tabs(["📋 Datos Brutos", "📊 Cp / Cpk", "📈 Control de Desviaciones"])

    with tab_datos:
        st.subheader(f"Vista de Datos | {etapa_seleccionada} - {producto_actual}")
        st.dataframe(df.style.apply(aplicar_semaforo, axis=1), use_container_width=True)
        st.caption("🟢 Verde: En Estándar (STD) | 🟡 Amarillo: En Tolerancia (TOL) | 🔴 Rojo: Fuera de Tolerancia")

    cols_num = [col for col in df.columns if pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').notna().sum() > 3]

    with tab_spc:
        st.subheader(f"Análisis de Capacidad | {etapa_seleccionada} ({producto_actual})")
        if cols_num:
            var_analizar = st.selectbox("3. Parámetro a analizar:", cols_num, key="spc_var")
            st.caption("💡 *Las casillas se autocompletan con la Tolerancia, pero puedes editarlas para hacer simulaciones.*")
            
            datos_clean = pd.to_numeric(df[var_analizar].astype(str).str.replace(',', '.'), errors='coerce').dropna()
            lsl_auto, usl_auto, _, _ = obtener_limites(etapa_seleccionada, producto_actual, var_analizar) if producto_actual != "Todos" else (None, None, None, None)
            
            col_a, col_b = st.columns(2)
            with col_a: lsl = st.number_input("LSL (Límite Inferior TOL):", value=float(lsl_auto if lsl_auto is not None else datos_clean.min()))
            with col_b: usl = st.number_input("USL (Límite Superior TOL):", value=float(usl_auto if usl_auto is not None else datos_clean.max()))

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

                    fig_hist = px.histogram(datos_clean, x=var_analizar, nbins=20, title=f"Distribución de {var_analizar}")
                    fig_hist.add_vline(x=lsl, line_dash="dash", line_color="red", annotation_text="LSL")
                    fig_hist.add_vline(x=usl, line_dash="dash", line_color="red", annotation_text="USL")
                    st.plotly_chart(fig_hist, use_container_width=True)

    with tab_tendencias:
        st.subheader(f"Control de Desviaciones | {etapa_seleccionada} ({producto_actual})")
        if cols_num:
            var_tend = st.selectbox("3. Parámetro para Gráfico:", cols_num, key="tend_var")
            
            # --- EJE X INTELIGENTE (Prioriza "Fecha de Análisis") ---
            posibles_x = [c for c in df.columns if "FECHA DE AN" in str(c).upper() or "FECHA" in str(c).upper()]
            if not posibles_x: # Si no hay fecha, busca lote
                posibles_x = [c for c in df.columns if "LOTE" in str(c).upper()]
            
            eje_x = st.selectbox("Eje X (Tiempo):", posibles_x if posibles_x else df.columns, index=0)

            df_trend = df.copy()
            df_trend[var_tend] = pd.to_numeric(df_trend[var_tend].astype(str).str.replace(',', '.'), errors='coerce')
            df_trend = df_trend.dropna(subset=[var_tend])
            
            lsl_auto, usl_auto, std_l, std_u = obtener_limites(etapa_seleccionada, producto_actual, var_tend) if producto_actual != "Todos" else (None, None, None, None)

            if len(df_trend) > 0:
                fig_trend = px.line(df_trend, x=eje_x, y=var_tend, markers=True, title=f"Tendencia: {var_tend}")
                
                if lsl_auto is not None and usl_auto is not None:
                    fig_trend.add_hline(y=usl_auto, line_dash="solid", line_color="red", annotation_text="TOL Máx")
                    fig_trend.add_hline(y=lsl_auto, line_dash="solid", line_color="red", annotation_text="TOL Mín")
                    
                    if std_u is not None and std_l is not None:
                        fig_trend.add_hline(y=std_u, line_dash="dash", line_color="orange", annotation_text="STD Máx")
                        fig_trend.add_hline(y=std_l, line_dash="dash", line_color="orange", annotation_text="STD Mín")

                    texto_info = f"<b>Especificación: {producto_actual}</b><br>TOL: {lsl_auto} a {usl_auto}"
                    if std_u is not None:
                        texto_info += f"<br>STD: {std_l} a {std_u}"

                    fig_trend.add_annotation(
                        x=0.02, y=0.98, xref="paper", yref="paper",
                        text=texto_info, showarrow=False, align="left",
                        bgcolor="rgba(255, 255, 255, 0.9)", bordercolor="black", borderwidth=1
                    )
                else:
                    st.info("⚠️ No hay especificación para este parámetro. Mostrando límites de control natural (3 Sigma).")

                fig_trend.update_traces(line=dict(color="royalblue", width=2), marker=dict(size=8))
                st.plotly_chart(fig_trend, use_container_width=True)

else:
    st.error("⚠️ No se pudieron cargar los datos.")