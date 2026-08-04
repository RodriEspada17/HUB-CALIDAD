import streamlit as st
import pandas as pd
import plotly.express as px
from utils.core import aplicar_estilo_neon, obtener_limites, generar_url_csv, cargar_datos

st.set_page_config(page_title="Parámetros Críticos", layout="wide", page_icon="▪️")
aplicar_estilo_neon()

# --- SIDEBAR: FILTROS LIMPIOS ---
st.sidebar.markdown("<h3 style='color: #a3ff00; font-size: 1.1rem; letter-spacing: 1px;'>⯈ FILTROS DE DATOS</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 0.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

URL_BASE = "https://docs.google.com/spreadsheets/d/1YiYwKJZsR7vBrLjCQBbGxzVxlTQEBRJVZEezJyQK3Yw/edit?pli=1&gid="

PESTANAS = {"Cocimiento": "1587615990", "Fin de Reposo": "79058483", "Filtración": "343087732", "Producto Terminado": "181144280"}
etapa_seleccionada = st.sidebar.selectbox("Etapa del Proceso", list(PESTANAS.keys()))
gid_actual = PESTANAS[etapa_seleccionada]
url_completa = URL_BASE + gid_actual

st.markdown(f"<h2 style='text-transform: uppercase; font-size: 1.8rem;'>MODULE / PARÁMETROS CRÍTICOS / <span style='color: #a3ff00;'>{etapa_seleccionada}</span></h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

df, _ = cargar_datos(generar_url_csv(url_completa, gid_actual))
producto_actual = "Todos"

if df is not None and not df.empty:

    # 1. ORDENAR DATOS: Voltear la tabla para ver lo más reciente arriba
    df = df.iloc[::-1].reset_index(drop=True)

    # 2. PURGA GENERAL: Destruir columnas basura "Unnamed" de Pandas
    cols_unnamed = [c for c in df.columns if "UNNAMED" in str(c).upper()]
    df = df.drop(columns=cols_unnamed, errors='ignore')

    # 3. PURGA ESPECÍFICA: Filtro de Cocimiento
    if etapa_seleccionada == "Cocimiento":
        cols_blacklist = [
            "EXTRACTO ORIGINAL FT A LAS 3HRS", "SO2", "FAN", "CALCIO",
            "YODO MACERADO", "YODO MOSTO FRIO", "TBZ CALDERA LENA", "TBZ CALDERA LLENA",
            "TBZ FIN DE HERVIDO", "TBZ MOSTO FRIO", "ATENUACION LIMITE"
        ]
        cols_a_borrar = [c for c in df.columns if any(b in c.upper() for b in cols_blacklist)]
        df = df.drop(columns=cols_a_borrar, errors='ignore')

    # 4. PURGA AUTOMÁTICA: Eliminar columnas 100% vacías o llenas de 'None'
    cols_validas = []
    for col in df.columns:
        vals_check = df[col].astype(str).str.strip().str.upper()
        if not vals_check.isin(['NONE', 'NAN', 'N/A', '', 'NONE.1']).all():
            cols_validas.append(col)
    df = df[cols_validas]

    # --- FILTRADO DE PRODUCTO Y GRUPOS ---
    col_prod = [c for c in df.columns if "PRODUCTO" in str(c).upper()]
    if col_prod:
        productos_limpios = df[col_prod[0]].astype(str).str.strip().str.upper()
        
        # Unificamos el filtro para Cocimiento Y Fin de Reposo
        if etapa_seleccionada in ["Cocimiento", "Fin de Reposo"]:
            lista_productos = ["Todos", "Amstel", "Schneider", "Capital", "Malta Real"]
        else:
            raw_unique = productos_limpios.unique()
            formatted_unique = sorted(list(set([p.title() for p in raw_unique])))
            lista_productos = ["Todos"] + formatted_unique

        prod_sel = st.sidebar.selectbox("Filtrar Producto", lista_productos)
        
        if prod_sel != "Todos":
            if prod_sel.upper() == "CAPITAL":
                df = df[productos_limpios.isin(["CAPITAL", "CORDILLERA", "REAL"])]
            elif prod_sel.upper() in ["MALTA REAL", "MALTA"]:
                df = df[productos_limpios.isin(["MALTA REAL", "MALTA"])]
            else:
                df = df[productos_limpios == prod_sel.upper()]
                
            producto_actual = prod_sel

    # --- SEMAFORIZACIÓN ELEGANTE (DARK PASTELS) ---
    def pintar_celdas(val, lsl, usl, std_l, std_u):
        # Seguro contra celdas vacías o "None"
        if pd.isna(val) or str(val).strip().upper() in ['NONE', 'NAN', 'N/A', '']:
            return ''
            
        try:
            v = float(str(val).replace(',', '.'))
            if lsl is not None and usl is not None:
                if v < lsl or v > usl: 
                    return 'background-color: #3b181a; color: #f87171;' 
                elif std_l is not None and std_u is not None:
                    if std_l <= v <= std_u: 
                        return 'background-color: #143324; color: #4ade80;' 
                    else: 
                        return 'background-color: #332d14; color: #facc15;' 
                else: 
                    return 'background-color: #332d14; color: #facc15;'
        except: pass
        return ''

    def aplicar_semaforo(row):
        estilos = [''] * len(row)
        prod_fila = producto_actual
        if prod_fila == "Todos":
            col_p = next((c for c in row.index if "PRODUCTO" in str(c).upper()), None)
            if col_p: 
                prod_fila = str(row[col_p]).strip().upper()
            else: 
                return estilos
                
        for i, col in enumerate(row.index):
            # Excepción: No pintar ciertas columnas si estamos en Cocimiento
            if etapa_seleccionada == "Cocimiento":
                cols_excluidas = ["ATENUACION", "EXTRACTO ORIGINAL AT", "EXTRACTO APARENTE", "EXTRACTO REAL", "ALCOHOL"]
                if any(ex in str(col).upper() for ex in cols_excluidas):
                    continue # Salta esta columna y la deja sin color
            
            lsl, usl, std_l, std_u = obtener_limites(etapa_seleccionada, prod_fila, col)
            if lsl is not None: 
                estilos[i] = pintar_celdas(row[col], lsl, usl, std_l, std_u)
        return estilos

    tab_datos, tab_spc, tab_tendencias = st.tabs(["DATASET", "SPC ANALYSIS", "TRENDS"])

    with tab_datos:
        st.dataframe(df.style.apply(aplicar_semaforo, axis=1), use_container_width=True)
        st.markdown("""
            <p style='font-size: 0.85rem; color: #888888; font-family: "Space Grotesk", sans-serif;'>
                <span style="color: #4ade80;">■</span> Estándar &nbsp;&nbsp;&nbsp; 
                <span style="color: #facc15;">■</span> Tolerancia &nbsp;&nbsp;&nbsp; 
                <span style="color: #f87171;">■</span> Fuera de Rango
            </p>
        """, unsafe_allow_html=True)

    cols_num = [col for col in df.columns if pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').notna().sum() > 3]

    with tab_spc:
        if cols_num:
            var_analizar = st.selectbox("Métrica a analizar:", cols_num, key="spc_var")
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
                    c4.metric("Cpk", f"{cpk:.2f}") 

                    fig_hist = px.histogram(datos_clean, x=var_analizar, nbins=20, template="plotly_dark", color_discrete_sequence=['#143324'])
                    fig_hist.update_traces(marker=dict(line=dict(width=1, color='#4ade80')))
                    fig_hist.add_vline(x=lsl, line_dash="dash", line_color="#f87171", annotation_text="LSL")
                    fig_hist.add_vline(x=usl, line_dash="dash", line_color="#f87171", annotation_text="USL")
                    st.plotly_chart(fig_hist, use_container_width=True)

    with tab_tendencias:
        if cols_num:
            var_tend = st.selectbox("Parámetro de Seguimiento:", cols_num, key="tend_var")
            posibles_x = [c for c in df.columns if "FECHA DE AN" in str(c).upper() or "FECHA" in str(c).upper()]
            if not posibles_x: posibles_x = [c for c in df.columns if "LOTE" in str(c).upper()]
            eje_x = st.selectbox("Eje Temporal:", posibles_x if posibles_x else df.columns, index=0)

            df_trend = df.copy()
            df_trend = df_trend.iloc[::-1].reset_index(drop=True)
            df_trend[var_tend] = pd.to_numeric(df_trend[var_tend].astype(str).str.replace(',', '.'), errors='coerce')
            df_trend = df_trend.dropna(subset=[var_tend])
            lsl_auto, usl_auto, std_l, std_u = obtener_limites(etapa_seleccionada, producto_actual, var_tend) if producto_actual != "Todos" else (None, None, None, None)

            if len(df_trend) > 0:
                fig_trend = px.line(df_trend, x=eje_x, y=var_tend, markers=True, template="plotly_dark", color_discrete_sequence=['#a3ff00'])
                if lsl_auto is not None and usl_auto is not None:
                    fig_trend.add_hline(y=usl_auto, line_dash="solid", line_color="#f87171")
                    fig_trend.add_hline(y=lsl_auto, line_dash="solid", line_color="#f87171")
                    if std_u is not None and std_l is not None:
                        fig_trend.add_hline(y=std_u, line_dash="dash", line_color="#4ade80")
                        fig_trend.add_hline(y=std_l, line_dash="dash", line_color="#4ade80")
                        
                    texto_info = f"<b>{producto_actual}</b><br>TOL: {lsl_auto} - {usl_auto}<br>STD: {std_l} - {std_u}"
                    fig_trend.add_annotation(x=0.01, y=0.99, xref="paper", yref="paper", text=texto_info, showarrow=False, align="left", bgcolor="#0f0f0f", bordercolor="#333", borderwidth=1)
                
                fig_trend.update_traces(line=dict(width=2), marker=dict(size=6, color="#a3ff00"))
                st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.error("Error de conexión de datos. Verifique la estructura del origen.")