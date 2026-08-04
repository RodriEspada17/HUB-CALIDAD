import streamlit as st
import pandas as pd
import plotly.express as px
from utils.core import aplicar_estilo_neon, obtener_limites, generar_url_csv, cargar_datos

st.set_page_config(page_title="Parámetros Críticos", layout="wide", page_icon="⚡")
aplicar_estilo_neon()

st.sidebar.header("⚙️ Configuración")
url_ingresada = st.sidebar.text_input("Data Source (URL):", value="https://docs.google.com/spreadsheets/d/1YiYwKJZsR7vBrLjCQBbGxzVxlTQEBRJVZEezJyQK3Yw/edit?pli=1&gid=1990898193#gid=1990898193")

PESTANAS = {"Cocimiento": "1587615990", "Fin de Reposo": "79058483", "Filtración": "343087732", "Producto Terminado": "181144280"}
etapa_seleccionada = st.sidebar.selectbox("1. Etapa del Proceso:", list(PESTANAS.keys()))
gid_actual = PESTANAS[etapa_seleccionada]

st.title(f"⚡ MÓDULO: Parámetros Críticos - {etapa_seleccionada}")

df, _ = cargar_datos(generar_url_csv(url_ingresada, gid_actual))
producto_actual = "Todos"

if df is not None and not df.empty:
    col_prod = [c for c in df.columns if "PRODUCTO" in str(c).upper()]
    if col_prod:
        lista_productos = ["Todos"] + list(df[col_prod[0]].dropna().astype(str).unique())
        prod_sel = st.sidebar.selectbox("2. Filtrar Producto:", lista_productos)
        if prod_sel != "Todos":
            df = df[df[col_prod[0]].astype(str) == prod_sel]
            producto_actual = prod_sel

    def pintar_celdas(val, lsl, usl, std_l, std_u):
        try:
            v = float(str(val).replace(',', '.'))
            if lsl is not None and usl is not None:
                if v < lsl or v > usl: return 'background-color: #ff003c; color: #ffffff;'
                elif std_l is not None and std_u is not None:
                    if std_l <= v <= std_u: return 'background-color: #00ff00; color: #000000;'
                    else: return 'background-color: #ffea00; color: #000000;'
                else: return 'background-color: #ffea00; color: #000000;'
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
            if lsl is not None: estilos[i] = pintar_celdas(row[col], lsl, usl, std_l, std_u)
        return estilos

    tab_datos, tab_spc, tab_tendencias = st.tabs(["📋 Datos Brutos", "📊 SPC (Cp/Cpk)", "📈 Control en Vivo"])

    with tab_datos:
        st.dataframe(df.style.apply(aplicar_semaforo, axis=1), use_container_width=True)
        st.caption("🟢 Estándar | 🟡 Tolerancia | 🔴 Fuera de Rango")

    cols_num = [col for col in df.columns if pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').notna().sum() > 3]

    with tab_spc:
        if cols_num:
            var_analizar = st.selectbox("3. Métrica:", cols_num, key="spc_var")
            datos_clean = pd.to_numeric(df[var_analizar].astype(str).str.replace(',', '.'), errors='coerce').dropna()
            lsl_auto, usl_auto, _, _ = obtener_limites(etapa_seleccionada, producto_actual, var_analizar) if producto_actual != "Todos" else (None, None, None, None)
            
            col_a, col_b = st.columns(2)
            with col_a: lsl = st.number_input("LSL (Mín):", value=float(lsl_auto if lsl_auto is not None else datos_clean.min()))
            with col_b: usl = st.number_input("USL (Máx):", value=float(usl_auto if usl_auto is not None else datos_clean.max()))

            if lsl < usl and len(datos_clean) > 0:
                media, sigma = datos_clean.mean(), datos_clean.std()
                if sigma > 0:
                    cp = (usl - lsl) / (6 * sigma)
                    cpk = min((media - lsl) / (3 * sigma), (usl - media) / (3 * sigma))
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Media", f"{media:.3f}")
                    c2.metric("Sigma", f"{sigma:.3f}")
                    c3.metric("Cp", f"{cp:.2f}")
                    c4.metric("Cpk", f"{cpk:.2f}", delta="ÓPTIMO" if cpk >= 1.33 else "CRÍTICO", delta_color="normal" if cpk >= 1.33 else "inverse")

                    fig_hist = px.histogram(datos_clean, x=var_analizar, nbins=20, template="plotly_dark", color_discrete_sequence=['#00f3ff'])
                    fig_hist.add_vline(x=lsl, line_dash="dash", line_color="#ff00ff", annotation_text="LSL")
                    fig_hist.add_vline(x=usl, line_dash="dash", line_color="#ff00ff", annotation_text="USL")
                    st.plotly_chart(fig_hist, use_container_width=True)

    with tab_tendencias:
        if cols_num:
            var_tend = st.selectbox("3. Parámetro de Seguimiento:", cols_num, key="tend_var")
            posibles_x = [c for c in df.columns if "FECHA DE AN" in str(c).upper() or "FECHA" in str(c).upper()]
            if not posibles_x: posibles_x = [c for c in df.columns if "LOTE" in str(c).upper()]
            eje_x = st.selectbox("Eje Tiempo:", posibles_x if posibles_x else df.columns, index=0)

            df_trend = df.copy()
            df_trend[var_tend] = pd.to_numeric(df_trend[var_tend].astype(str).str.replace(',', '.'), errors='coerce')
            df_trend = df_trend.dropna(subset=[var_tend])
            lsl_auto, usl_auto, std_l, std_u = obtener_limites(etapa_seleccionada, producto_actual, var_tend) if producto_actual != "Todos" else (None, None, None, None)

            if len(df_trend) > 0:
                fig_trend = px.line(df_trend, x=eje_x, y=var_tend, markers=True, template="plotly_dark", color_discrete_sequence=['#00f3ff'])
                if lsl_auto is not None and usl_auto is not None:
                    fig_trend.add_hline(y=usl_auto, line_dash="solid", line_color="#ff003c")
                    fig_trend.add_hline(y=lsl_auto, line_dash="solid", line_color="#ff003c")
                    if std_u is not None and std_l is not None:
                        fig_trend.add_hline(y=std_u, line_dash="dash", line_color="#00ff00")
                        fig_trend.add_hline(y=std_l, line_dash="dash", line_color="#00ff00")
                        
                    texto_info = f"<b>{producto_actual}</b><br>TOL: {lsl_auto} - {usl_auto}<br>STD: {std_l} - {std_u}"
                    fig_trend.add_annotation(x=0.01, y=0.99, xref="paper", yref="paper", text=texto_info, showarrow=False, align="left", bgcolor="#11141c", bordercolor="#ff00ff", borderwidth=1)
                
                fig_trend.update_traces(line=dict(width=3), marker=dict(size=10, color="#ff00ff"))
                st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.error("⚠️ Error de conexión de datos.")
