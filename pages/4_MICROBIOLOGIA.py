import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.core import aplicar_estilo_neon, generar_url_csv, cargar_datos

# Configuración inicial
st.set_page_config(page_title="Microbiología SPC", layout="wide", initial_sidebar_state="collapsed")
aplicar_estilo_neon()

# --- CSS GLOBAL (INTER + NEÓN + SELECTBOX READONLY) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; background-color: #050505 !important; color: #e0e0e0 !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    
    /* BOTÓN VOLVER PRINCIPAL */
    div[data-testid="stButton"] > button { 
        background-color: transparent !important; border: 1px solid #1a1a1a !important; width: fit-content !important; 
        padding: 6px 16px !important; border-radius: 6px !important; transition: 0.3s !important; margin-bottom: 10px !important;
    }
    div[data-testid="stButton"] > button p { color: #888888 !important; font-weight: 700 !important; font-size: 0.8rem !important; letter-spacing: 1px !important; }
    div[data-testid="stButton"] > button:hover { border-color: #a3ff00 !important; background-color: rgba(163, 255, 0, 0.05) !important; }
    div[data-testid="stButton"] > button:hover p { color: #a3ff00 !important; }
        
    /* ELIMINAR EL FOCO PERMANENTE DESPUÉS DEL CLIC */
    div[data-testid="stButton"] > button:focus { box-shadow: none !important; outline: none !important; border-color: #1a1a1a !important; }
    div[data-testid="stButton"] > button:focus p { color: #888888 !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) { border-color: #1a1a1a !important; background-color: transparent !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) p { color: #888888 !important; }
    
    /* BLOQUEAR ESCRITURA / TECLADO EN DESPLEGABLES */
    div[data-baseweb="select"] input { width: 0px !important; opacity: 0 !important; position: absolute !important; pointer-events: none !important; }
    div[data-baseweb="select"], div[data-baseweb="select"] * { cursor: pointer !important; }
    
    .stSelectbox label, .stRadio label { color: #888888 !important; font-weight: 600 !important; letter-spacing: 1px; font-size: 0.85rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- ESTÁNDARES DE TEMPERATURA (SOLO PROPAGACIÓN) ---
SPECS_TEMP = {
    "Laboratorio": {"target": 25.0, "tol": 0.5, "min": 24.5, "max": 25.5, "color": "#60a5fa", "bg": "rgba(96, 165, 250, 0.06)", "symbol": "circle"},
    "Industrial 1": {"target": 18.0, "tol": 0.5, "min": 17.5, "max": 18.5, "color": "#a3ff00", "bg": "rgba(163, 255, 0, 0.06)", "symbol": "diamond"},
    "Industrial 2": {"target": 16.0, "tol": 0.5, "min": 15.5, "max": 16.5, "color": "#facc15", "bg": "rgba(250, 204, 21, 0.06)", "symbol": "square"},
    "Industrial 3": {"target": 14.0, "tol": 0.5, "min": 13.5, "max": 14.5, "color": "#f97316", "bg": "rgba(249, 115, 22, 0.06)", "symbol": "triangle-up"}
}

# --- ESTÁNDARES SEGREGADOS POR ETAPA MAESTRA ---
SPECS_PARAMETROS = {
    "1. Control de Propagación": {
        "recuento": {"type": "min", "val": 80.0, "label": "> 80 mill. Cel/ml", "unit": "mill. Cel/ml"},
        "extracto original": {"type": "range", "min": 9.9, "max": 11.5, "label": "9.9 - 11.5 °P", "unit": "°P"},
        "alcohol": {"type": "max", "val": 3.0, "label": "< 3 %", "unit": "%"},
        "muerta": {"type": "max", "val": 0.0, "label": "0 %", "unit": "%"},
        "wld": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "aerobio": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "salvaje": {"type": "max", "val": 1.0, "label": "≤ 1 UFC/ml", "unit": "UFC/ml"},
        "ym": {"type": "max", "val": 1.0, "label": "≤ 1 UFC/ml", "unit": "UFC/ml"},
        "anaerobio": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "nbb": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"}
    },
    "4. Fermentación": {
        "wld": {"type": "max", "val": 10.0, "label": "≤ 10 UFC/ml", "unit": "UFC/ml"},
        "aerobio": {"type": "max", "val": 10.0, "label": "≤ 10 UFC/ml", "unit": "UFC/ml"},
        "salvaje": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "ym": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"}
    },
    "6. Envasado": {
        "wld": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "aerobio": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "salvaje": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "ym": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "anaerobio": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"},
        "nbb": {"type": "max", "val": 0.0, "label": "0 UFC/ml", "unit": "UFC/ml"}
    }
}

def obtener_spec_parametro(col_nombre, etapa):
    col_low = col_nombre.lower()
    specs_etapa = SPECS_PARAMETROS.get(etapa, {})
    for key, spec in specs_etapa.items():
        if key in col_low:
            return spec
    return None

def agrupar_por_propagaciones(df):
    if 'FECHA_DT' not in df.columns or df['FECHA_DT'].dropna().empty: return df
    diferencias = df['FECHA_DT'].dt.date.diff().apply(lambda x: x.days if pd.notna(x) else 0)
    df['batch_id'] = (diferencias > 1).cumsum()
    def obtener_etiqueta_rango(sub_df):
        f_min = sub_df['FECHA_DT'].min()
        f_max = sub_df['FECHA_DT'].max()
        meses_es = {1:'ene', 2:'feb', 3:'mar', 4:'abr', 5:'may', 6:'jun', 7:'jul', 8:'ago', 9:'sep', 10:'oct', 11:'nov', 12:'dic'}
        inicio = f"{f_min.day}{meses_es[f_min.month]}"
        fin = f"{f_max.day}{meses_es[f_max.month]}"
        return f"[{inicio}]" if inicio == fin else f"[{inicio}-{fin}]"
    mapa_etiquetas = {b_id: obtener_etiqueta_rango(sub) for b_id, sub in df.groupby('batch_id')}
    df['Propagacion'] = df['batch_id'].map(mapa_etiquetas)
    return df

def clasificar_escala(df):
    col_escala = next((c for c in df.columns if "escala" in c.lower()), None)
    col_etapa = next((c for c in df.columns if "etapa" in c.lower()), None)
    fases = []
    for idx, row in df.iterrows():
        val_escala = str(row[col_escala]).strip().lower() if col_escala and pd.notna(row[col_escala]) else ""
        etapa_num = "1"
        if col_etapa and pd.notna(row[col_etapa]):
            try:
                num = int(float(str(row[col_etapa]).strip().replace(',', '.')))
                if num in [1, 2, 3]: etapa_num = str(num)
            except: pass
        
        if "lab" in val_escala: fases.append("Laboratorio")
        elif "ind" in val_escala or "plant" in val_escala or "tanque" in val_escala: fases.append(f"Industrial {etapa_num}")
        else: fases.append("Laboratorio" if idx < 4 else f"Industrial {etapa_num}")
                
    df['Escala_Fase'] = fases
    return df

def aplicar_semaforo_tabla(row):
    global etapa_seleccionada
    estilos = [''] * len(row)
    
    col_escala = next((c for c in row.index if "escala" in str(c).lower()), None)
    col_etapa = next((c for c in row.index if "etapa" in str(c).lower()), None)
    val_escala = str(row[col_escala]).strip().lower() if col_escala else ""
    val_etapa = str(row[col_etapa]).strip() if col_etapa else ""
    
    fase = "General"
    if 'lab' in val_escala: fase = "Laboratorio"
    elif 'ind' in val_escala or 'plant' in val_escala or 'tanque' in val_escala:
        etapa_num = "".join(filter(str.isdigit, val_etapa))
        fase = f"Industrial {etapa_num}" if etapa_num in ["1", "2", "3"] else "Industrial 1"
        
    for i, col in enumerate(row.index):
        val = row[col]
        if pd.isna(val) or str(val).strip().upper() in ['NONE', 'NAN', 'N/A', '']: continue
            
        es_temperatura = "temp" in str(col).lower()
        spec_gen = obtener_spec_parametro(str(col), etapa_seleccionada) if not es_temperatura else None
        spec_t = SPECS_TEMP.get(fase, None) if etapa_seleccionada == "1. Control de Propagación" else None
        
        cumple, has_spec = True, False
        
        if es_temperatura and spec_t and spec_t.get("min") is not None:
            has_spec = True
            try:
                v = float(str(val).replace(',', '.'))
                if not (spec_t["min"] <= v <= spec_t["max"]): cumple = False
            except: pass
        elif spec_gen:
            has_spec = True
            try:
                v = float(str(val).replace(',', '.'))
                if spec_gen["type"] == "min" and v < spec_gen["val"]: cumple = False
                elif spec_gen["type"] == "max" and v > spec_gen["val"]: cumple = False
                elif spec_gen["type"] == "range" and not (spec_gen["min"] <= v <= spec_gen["max"]): cumple = False
            except: pass
        
        if has_spec:
            estilos[i] = 'background-color: #143324; color: #4ade80;' if cumple else 'background-color: #3b181a; color: #f87171;'
    return estilos

# --- NAV ---
col_b1, col_b2, _ = st.columns([1.5, 1.5, 7])
with col_b1:
    if st.button("◀ VOLVER A CALIDAD"): st.switch_page("pages/CONTROL_CALIDAD.py")
with col_b2:
    if st.button("◀ VOLVER AL INICIO"): st.switch_page("app.py")

st.markdown("<h1 style='color: #a3ff00; font-size: 2.2rem; font-weight: 800; letter-spacing: 2px; margin: 0;'>ANÁLISIS MICROBIOLÓGICOS <span style='color: #ffffff;'>(SPC)</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.95rem; margin-bottom: 2rem;'>Monitoreo estadístico de recuentos celulares y contaminación.</p>", unsafe_allow_html=True)

URL_BASE = "https://docs.google.com/spreadsheets/d/1CHG6Ndce1Hon9nUFikJqY5YIezYHHC1z_GKnWBmBOFQ/edit?pli=1&gid="

GIDS = {
    "1. Control de Propagación": "2050551093",
    "2. Análisis de Levadura": "160101583", 
    "3. Cocimiento": "1413638154",
    "4. Fermentación": "1692699392",
    "5. Filtración": "1258366654",
    "6. Envasado": "1542069577",
    "7. Agua y Materia Prima": "PONER_GID_AQUI"
}

col1, col2 = st.columns([1.2, 2.8])
with col1:
    etapa_seleccionada = st.selectbox("SELECCIONA LA ETAPA A MONITOREAR:", list(GIDS.keys()))

st.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def cargar_y_limpiar_microbiologia(gid):
    if gid == "PONER_GID_AQUI": return None
    url_csv = generar_url_csv(URL_BASE + gid, gid)
    try:
        df = pd.read_csv(url_csv)
        df = df.replace({"Ausencia": 0, "ausencia": 0, "AUSENCIA": 0})
        df = df.replace({"NA": np.nan, "N/A": np.nan, "n/a": np.nan, "-": np.nan, "": np.nan})
        df = df.replace({"DNPC": 300, "dnpc": 300}) 
        
        columnas_fecha = [col for col in df.columns if "fecha" in col.lower() or "semana" in col.lower()]
        for col in columnas_fecha:
            df.loc[df[col].astype(str).str.contains("1900", na=False), col] = np.nan
        if len(columnas_fecha) > 0:
            df = df.dropna(subset=[columnas_fecha[0]])
            
        columnas_excluidas = ['fecha', 'hora', 'semana', 'lote', 'escala', 'etapa', 'analista', 'producto', 'procedencia', 'tipo', 'generación', 'tanque', 'observaciones', 'ft', 'tp', 'muestra', 'sector', 'estado', 'calibre', 'propagacion', 'batch_id', 'fecha_dt', 'escala_fase', 'label_selector']
        for col in df.columns:
            if not any(excl in col.lower() for excl in columnas_excluidas):
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e: return f"Error: {e}"

gid_actual = GIDS[etapa_seleccionada]

if gid_actual == "PONER_GID_AQUI":
    st.info(f"Falta configurar el GID para **{etapa_seleccionada}**. Agrégalo en el código.")
else:
    with st.spinner("Conectando con Google Sheets y estructurando datos..."):
        df_limpio = cargar_y_limpiar_microbiologia(gid_actual)
        
    if isinstance(df_limpio, str):
        st.error(f"Error de conexión: {df_limpio}")
    elif df_limpio is not None and not df_limpio.empty:
        
        col_fecha_orig = next((c for c in df_limpio.columns if "fecha" in c.lower()), None)
        col_hora_str = next((c for c in df_limpio.columns if "hora" in c.lower()), None)
        
        if col_fecha_orig:
            if col_hora_str and col_hora_str in df_limpio.columns:
                df_limpio['FECHA_DT'] = pd.to_datetime(df_limpio[col_fecha_orig].astype(str) + ' ' + df_limpio[col_hora_str].astype(str), errors='coerce', dayfirst=True)
            else:
                df_limpio['FECHA_DT'] = pd.to_datetime(df_limpio[col_fecha_orig], errors='coerce', dayfirst=True)
            df_limpio = df_limpio.dropna(subset=['FECHA_DT']).sort_values('FECHA_DT').reset_index(drop=True)
        else:
            df_limpio['FECHA_DT'] = df_limpio.index

        col_ft = next((c for c in df_limpio.columns if c.strip().lower() == "ft"), None)
        if not col_ft: col_ft = next((c for c in df_limpio.columns if "ft" in c.lower()), None)
        col_lote_ref = next((c for c in df_limpio.columns if "lote" in c.lower() and c.lower() != 'lote'), None)
        if not col_lote_ref: col_lote_ref = next((c for c in df_limpio.columns if "lote" in c.lower()), None)

        # -------------------------------------------------------------------------
        # LÓGICA EXCLUSIVA PARA FERMENTACIÓN (DISEÑO 48H vs 7 DÍAS)
        # -------------------------------------------------------------------------
        if etapa_seleccionada == "4. Fermentación":
            df_limpio['Escala_Fase'] = "General"
            
            if col_ft:
                def limpiar_entero(val):
                    if pd.isna(val): return ""
                    raw = str(val).strip()
                    try: return str(int(float(raw.replace(',', '.'))))
                    except: return raw.upper()

                df_limpio[col_ft] = df_limpio[col_ft].apply(limpiar_entero)
                
                if col_lote_ref:
                    df_limpio[col_lote_ref] = df_limpio[col_lote_ref].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('(?i)nan', '', regex=True).str.replace('(?i)none', '', regex=True)

                # 🔥 1ER DESPLEGABLE: FILTRAR POR FT
                df_valid_ft = df_limpio[~df_limpio[col_ft].isin(["", "NAN", "NONE", "N/A"])]
                fts_unicos = list(dict.fromkeys(df_valid_ft[col_ft].unique()))
                lista_fts = ["Todos los FT"] + fts_unicos
                
                c_filtro1, c_filtro2 = st.columns(2)
                
                with c_filtro1: 
                    ft_sel = st.selectbox("FILTRAR POR FT:", lista_fts)
                
                if ft_sel != "Todos los FT":
                    df_limpio = df_limpio[df_limpio[col_ft] == ft_sel]

                # 🔥 2DO DESPLEGABLE: FILTRAR POR LOTE (Depende del FT seleccionado)
                if col_lote_ref:
                    df_valid_lotes = df_limpio[~df_limpio[col_lote_ref].isin(["", "NAN", "NONE", "N/A"])]
                    lotes_unicos = list(dict.fromkeys(df_valid_lotes[col_lote_ref].unique()))
                    lista_lotes = ["Todos los Lotes"] + lotes_unicos
                    
                    with c_filtro2:
                        lote_sel = st.selectbox("FILTRAR POR LOTE:", lista_lotes)
                    
                    if lote_sel != "Todos los Lotes":
                        df_limpio = df_limpio[df_limpio[col_lote_ref] == lote_sel]
            
            c_opt1, c_opt2 = st.columns(2)
            with c_opt1:
                param_base = st.selectbox("PARÁMETRO BIOLÓGICO:", ["Aerobios WLD", "Levadura Salvaje YM"])
            with c_opt2:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                eje_x_sel = st.radio("ETIQUETAS DEL EJE X:", ["Solo FT", "FT + Lote"], horizontal=True)

            cols_numericas = df_limpio.select_dtypes(include=[np.number]).columns.tolist()
            
            if param_base == "Aerobios WLD":
                col_48h = next((c for c in cols_numericas if "medici" in c.lower() and "wld" in c.lower()), None)
                col_7d = next((c for c in cols_numericas if c.lower().strip() == "aerobio wld"), None)
            else:
                col_48h = next((c for c in cols_numericas if c.lower().strip() == "levadura salvaje ym"), None)
                col_7d = next((c for c in cols_numericas if "lev. salvaje" in c.lower() or "lev salvaje" in c.lower()), None)

            def render_fermentacion_row(col_param, titulo_grafico, titulo_tabla, tipo_fase):
                if not col_param or col_param not in df_limpio.columns:
                    st.info(f"No hay registros de {titulo_grafico} para esta selección.")
                    return
                
                df_fase = df_limpio.dropna(subset=[col_param]).copy()
                if df_fase.empty:
                    st.info(f"Los registros de {titulo_grafico} están vacíos para este lote.")
                    return

                c_graf, c_tab = st.columns([2.5, 1.2])
                
                with c_graf:
                    st.markdown(f"<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ {titulo_grafico}</h3>", unsafe_allow_html=True)
                    
                    fig = go.Figure()
                    spec_gen = obtener_spec_parametro(col_param, etapa_seleccionada)
                    
                    promedio = df_fase[col_param].mean()
                    desviacion = df_fase[col_param].std()
                    lcs = promedio + (3 * desviacion) if pd.notna(desviacion) and desviacion > 0 else promedio

                    if spec_gen:
                        if spec_gen["type"] == "min": fig.add_hline(y=spec_gen["val"], line_dash="dash", line_color="#4ade80", annotation_text=f"Mín: {spec_gen['label']}", annotation_position="top left")
                        elif spec_gen["type"] == "max": fig.add_hline(y=spec_gen["val"], line_dash="dash", line_color="#f87171", annotation_text=f"Máx: {spec_gen['label']}", annotation_position="top left", annotation_font_color="#f87171")
                    else:
                        fig.add_hline(y=promedio, line_dash="dash", line_color="#888888", annotation_text=f"Prom: {promedio:.1f}")
                        if pd.notna(lcs) and lcs > promedio: fig.add_hline(y=lcs, line_dash="dot", line_color="#f87171", annotation_text=f"LCS: {lcs:.1f}", annotation_font_color="#f87171")

                    fig.add_trace(go.Scatter(x=df_fase['FECHA_DT'], y=df_fase[col_param], mode='lines', line=dict(color='rgba(163, 255, 0, 0.35)', width=1.5, dash='dot'), showlegend=False, hoverinfo='none'))

                    colores_puntos, hover_text, tick_text = [], [], []
                    
                    for idx, row in df_fase.iterrows():
                        val = row[col_param]
                        ft_val = row.get(col_ft, 'N/A') if col_ft else 'N/A'
                        lote_val = row.get(col_lote_ref, 'N/A') if col_lote_ref else 'N/A'
                        
                        if eje_x_sel == "FT + Lote": tick_text.append(f"FT {ft_val}<br>L. {lote_val}")
                        else: tick_text.append(f"FT {ft_val}")
                        
                        cumple, std_label_txt = True, ""
                        if spec_gen:
                            std_label_txt = f"STD: {spec_gen['label']}"
                            if pd.notna(val) and float(val) > spec_gen["val"]: cumple = False
                        else:
                            if pd.notna(val) and pd.notna(lcs) and float(val) > lcs:
                                cumple, std_label_txt = False, f"Alerta SPC (LCS: {lcs:.1f})"

                        if cumple:
                            colores_puntos.append('#a3ff00')
                            estado_txt = "<span style='color: #4ade80;'><b>✅ DENTRO DE STD</b></span>" if spec_gen else "<span style='color: #4ade80;'><b>✅ NORMAL</b></span>"
                        else:
                            colores_puntos.append('#f87171')
                            estado_txt = "<span style='color: #f87171;'><b>🚨 FUERA DE STD</b></span>"
                            
                        target_info = f"<br>{std_label_txt}<br>Estado: {estado_txt}" if std_label_txt else ""
                        fecha_val = row[col_fecha_orig] if col_fecha_orig in row else row['FECHA_DT'].strftime('%d-%b')

                        hover_text.append(f"Fecha: {fecha_val}<br>Lote/FT: {lote_val} / FT {ft_val}<br>Valor: <b>{val} {spec_gen['unit'] if spec_gen else ''}</b>{target_info}")

                    fig.add_trace(go.Scatter(
                        x=df_fase['FECHA_DT'], y=df_fase[col_param], mode='lines+markers', name=col_param,
                        hovertext=hover_text, hoverinfo="text", line=dict(color="#a3ff00", width=2),
                        marker=dict(size=9, symbol="circle", color=colores_puntos, line=dict(width=1, color='#050505'))
                    ))

                    fig.update_layout(
                        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="", tickmode='array', tickvals=df_fase['FECHA_DT'], ticktext=tick_text),
                        yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="UFC / ml"), margin=dict(l=0, r=0, t=30, b=0), showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                with c_tab:
                    st.markdown(f"<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ TABLA {titulo_tabla}</h3>", unsafe_allow_html=True)
                    
                    cols_to_show = []
                    for c in df_fase.columns:
                        cl = c.lower()
                        if c in ['FECHA_DT', 'batch_id', 'fase_block', 'Escala_Fase', 'Propagacion', 'LABEL_SELECTOR']: continue
                        
                        is_fecha = "toma" in cl or "lectura" in cl or "fecha" in cl
                        is_contexto = (cl == "ft") or ("lote" in cl)
                        
                        if is_fecha:
                            if tipo_fase == "48" and "48" in cl: cols_to_show.append(c)
                            elif tipo_fase == "7" and ("7" in cl or "7mo" in cl): cols_to_show.append(c)
                        elif is_contexto:
                            cols_to_show.append(c)
                            
                    if col_param not in cols_to_show:
                        cols_to_show.append(col_param)
                        
                    df_tabla = df_fase[cols_to_show].copy()
                    
                    for c in df_tabla.columns:
                        if c.lower() == "ft" or "ft" in c.lower() or "lote" in c.lower():
                            df_tabla[c] = df_tabla[c].apply(lambda x: f"{int(float(x))}" if pd.notna(x) and str(x).strip() != "" and str(x).replace('.','',1).replace('-','',1).isdigit() else ("" if pd.isna(x) else str(x)))

                    st.dataframe(df_tabla.style.apply(aplicar_semaforo_tabla, axis=1).format(precision=2, na_rep=""), use_container_width=True, height=350)

            st.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)
            render_fermentacion_row(col_48h, f"MEDICIÓN A LAS 48 HORAS", "48 HORAS", "48")
            st.markdown("<br><hr style='border: 1px solid #1a1a1a; margin-bottom: 25px;'>", unsafe_allow_html=True)
            render_fermentacion_row(col_7d, f"LECTURA A LOS 7 DÍAS", "7 DÍAS", "7")

        # -------------------------------------------------------------------------
        # LÓGICA ESTÁNDAR PARA PROPAGACIÓN Y DEMÁS ETAPAS (ENVASADO Y OTROS)
        # -------------------------------------------------------------------------
        else:
            if etapa_seleccionada == "1. Control de Propagación":
                df_limpio = agrupar_por_propagaciones(df_limpio)
                df_limpio = clasificar_escala(df_limpio)
                if 'Propagacion' in df_limpio.columns:
                    lista_lotes = ["Todas las Propagaciones"] + list(df_limpio['Propagacion'].unique())
                    c_lote, _ = st.columns([1.5, 2.5])
                    with c_lote: lote_sel = st.selectbox("PROPAGACIÓN / LOTE SELECCIONADO:", lista_lotes)
                    if lote_sel != "Todas las Propagaciones":
                        df_limpio = df_limpio[df_limpio['Propagacion'] == lote_sel]
            
            elif etapa_seleccionada == "6. Envasado":
                df_limpio['Escala_Fase'] = "General"
                
                # --- FILTRO POR PRODUCTO ---
                col_producto = next((c for c in df_limpio.columns if "producto" in c.lower()), None)
                prod_sel = "Todos los Productos"
                
                if col_producto:
                    df_limpio[col_producto] = df_limpio[col_producto].astype(str).str.strip().str.replace(r'(?i)^nan$', 'N/A', regex=True)
                    df_valid_prod = df_limpio[~df_limpio[col_producto].isin(["", "NAN", "NONE", "N/A", "nan", "NaN"])]
                    prods_unicos = list(dict.fromkeys(df_valid_prod[col_producto].unique()))
                    lista_prods = ["Todos los Productos"] + prods_unicos
                    
                    c_prod, _ = st.columns([1.5, 2.5])
                    with c_prod: 
                        prod_sel = st.selectbox("FILTRAR POR PRODUCTO:", lista_prods)
                    
                    if prod_sel != "Todos los Productos":
                        df_limpio = df_limpio[df_limpio[col_producto] == prod_sel]
            else:
                df_limpio['Escala_Fase'] = "General"

            cols_numericas = df_limpio.select_dtypes(include=[np.number]).columns.tolist()
            cols_prohibidas_graf = ['semana', 'lote', 'ft', 'batch_id', 'etapa', 'escala', 'escala_fase', 'hora', 'volumen', 'unnamed', 'procedencia', 'producto', 'analista', 'tipo', 'tanque', 'observaciones', 'tp', 'muestra', 'sector', 'estado', 'calibre']
            cols_graficables = [c for c in cols_numericas if not any(ex in c.lower() for ex in cols_prohibidas_graf)]
            
            col_x_graf = 'FECHA_DT'
            if etapa_seleccionada == "6. Envasado":
                cols_permitidas = []
                for c in cols_graficables:
                    cl = c.lower().strip()
                    # Filtro expandido y seguro para capturar Aerobios, Salvajes y NBB
                    if "aerob" in cl or "salvaje" in cl or "nbb" in cl:
                        cols_permitidas.append(c)
                cols_graficables = cols_permitidas
                
                col_lote_env = next((c for c in df_limpio.columns if "lote" in c.lower()), None)
                if col_lote_env:
                    df_limpio[col_lote_env] = df_limpio[col_lote_env].astype(str).str.replace(r'\.0$', '', regex=True).str.replace('(?i)nan', 'N/A', regex=True)
                    col_x_graf = col_lote_env
            
            col_grafico, col_tabla = st.columns([2.5, 1.2])
            
            with col_grafico:
                st.markdown(f"<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ GRÁFICO DE CONTROL (SPC) {'MULTI-ESCALA' if etapa_seleccionada == '1. Control de Propagación' else ''}</h3>", unsafe_allow_html=True)
                
                if cols_graficables:
                    idx_default = next((i for i, c in enumerate(cols_graficables) if "temp" in c.lower()), 0)
                    parametro_a_graficar = st.selectbox("Selecciona el parámetro a analizar:", cols_graficables, index=idx_default, label_visibility="collapsed")
                    
                    col_fecha_label = col_fecha_orig if col_fecha_orig else "FECHA_DT"
                    es_temperatura = "temp" in parametro_a_graficar.lower()
                    spec_gen = obtener_spec_parametro(parametro_a_graficar, etapa_seleccionada) if not es_temperatura else None
                    
                    promedio_global = df_limpio[parametro_a_graficar].mean()
                    desviacion_global = df_limpio[parametro_a_graficar].std()
                    lcs_global = promedio_global + (3 * desviacion_global) if pd.notna(desviacion_global) and desviacion_global > 0 else promedio_global
                    
                    fig = go.Figure()

                    if spec_gen:
                        if spec_gen["type"] == "min": fig.add_hline(y=spec_gen["val"], line_dash="dash", line_color="#4ade80", annotation_text=f"Mín STD: {spec_gen['label']}", annotation_position="top left")
                        elif spec_gen["type"] == "max": fig.add_hline(y=spec_gen["val"], line_dash="dash", line_color="#f87171", annotation_text=f"Máx STD: {spec_gen['label']}", annotation_position="top left", annotation_font_color="#f87171")
                        elif spec_gen["type"] == "range":
                            fig.add_hline(y=spec_gen["min"], line_dash="dash", line_color="#4ade80", annotation_text=f"LSL: {spec_gen['min']}")
                            fig.add_hline(y=spec_gen["max"], line_dash="dash", line_color="#4ade80", annotation_text=f"USL: {spec_gen['max']}")
                    elif not (es_temperatura and "1. Control de Propagación" in etapa_seleccionada):
                        fig.add_hline(y=promedio_global, line_dash="dash", line_color="#888888", annotation_text=f"Prom: {promedio_global:.1f}")
                        if pd.notna(lcs_global) and lcs_global > promedio_global: fig.add_hline(y=lcs_global, line_dash="dot", line_color="#f87171", annotation_text=f"LCS: {lcs_global:.1f}", annotation_font_color="#f87171")

                    if etapa_seleccionada == "1. Control de Propagación":
                        if 'Escala_Fase' in df_limpio.columns:
                            df_limpio['fase_block'] = (df_limpio['Escala_Fase'] != df_limpio['Escala_Fase'].shift()).cumsum()
                            for _, sub_block in df_limpio.groupby('fase_block'):
                                fase_name = sub_block['Escala_Fase'].iloc[0]
                                spec_info = SPECS_TEMP.get(fase_name, {})
                                x_min = sub_block['FECHA_DT'].min()
                                x_max = sub_block['FECHA_DT'].max()
                                fig.add_vrect(x0=x_min, x1=x_max, fillcolor=spec_info.get('bg', 'rgba(255,255,255,0.02)'), layer="below", line_width=0)
                                if es_temperatura and spec_info.get('min') is not None:
                                    fig.add_shape(type="rect", x0=x_min, x1=x_max, y0=spec_info['min'], y1=spec_info['max'], fillcolor="rgba(74, 222, 128, 0.12)", line=dict(color="rgba(74, 222, 128, 0.3)", width=1), layer="below")
                                    
                        fig.add_trace(go.Scatter(x=df_limpio[col_x_graf], y=df_limpio[parametro_a_graficar], mode='lines', line=dict(color='rgba(255, 255, 255, 0.35)', width=1.5, dash='dot'), showlegend=False, hoverinfo='none'))
                    else:
                        fig.add_trace(go.Scatter(x=df_limpio[col_x_graf], y=df_limpio[parametro_a_graficar], mode='lines', line=dict(color='rgba(163, 255, 0, 0.35)', width=1.5, dash='dot'), showlegend=False, hoverinfo='none'))

                    fases_presentes = ["Laboratorio", "Industrial 1", "Industrial 2", "Industrial 3"] if etapa_seleccionada == "1. Control de Propagación" else ["General"]
                    fases_presentes = [f for f in fases_presentes if f in df_limpio['Escala_Fase'].values]

                    for fase_tipo in fases_presentes:
                        group = df_limpio[df_limpio['Escala_Fase'] == fase_tipo]
                        spec_t = SPECS_TEMP.get(fase_tipo, {"color": "#a3ff00", "symbol": "circle", "target": None, "min": None, "max": None})
                        
                        colores_puntos, hover_text = [], []
                        
                        for idx, row in group.iterrows():
                            val = row[parametro_a_graficar]
                            hora_txt = f" {row[col_hora_str]}" if col_hora_str and pd.notna(row[col_hora_str]) else ""
                            fecha_val = row[col_fecha_label] if col_fecha_label in row else row['FECHA_DT']
                            
                            cumple, std_label_txt = True, ""
                            if es_temperatura and spec_t["min"] is not None and "1. Control de Propagación" in etapa_seleccionada:
                                std_label_txt = f"STD: {spec_t['target']} ± {spec_t['tol']}°C"
                                if pd.notna(val) and not (spec_t["min"] <= float(val) <= spec_t["max"]): cumple = False
                            elif spec_gen:
                                std_label_txt = f"STD: {spec_gen['label']}"
                                if pd.notna(val):
                                    float_v = float(val)
                                    if spec_gen["type"] == "min" and float_v < spec_gen["val"]: cumple = False
                                    elif spec_gen["type"] == "max" and float_v > spec_gen["val"]: cumple = False
                                    elif spec_gen["type"] == "range" and not (spec_gen["min"] <= float_v <= spec_gen["max"]): cumple = False
                            else:
                                if pd.notna(val) and pd.notna(lcs_global) and float(val) > lcs_global:
                                    cumple, std_label_txt = False, f"Alerta SPC (LCS: {lcs_global:.1f})"

                            if cumple:
                                colores_puntos.append(spec_t["color"])
                                estado_txt = "<span style='color: #4ade80;'><b>✅ DENTRO DE STD</b></span>" if (spec_gen or es_temperatura) else "<span style='color: #4ade80;'><b>✅ NORMAL</b></span>"
                            else:
                                colores_puntos.append('#f87171')
                                estado_txt = "<span style='color: #f87171;'><b>🚨 FUERA DE STD</b></span>"
                                
                            target_info = f"<br>{std_label_txt}<br>Estado: {estado_txt}" if std_label_txt else ""
                            
                            if etapa_seleccionada == "6. Envasado":
                                hover_text.append(f"Lote: {row[col_x_graf]}<br>Fecha: {fecha_val}<br>Valor: <b>{val} {spec_gen['unit'] if spec_gen else ''}</b>{target_info}")
                            else:
                                etapa_info = f"Etapa: <b>{fase_tipo}</b><br>" if "1. Control de Propagación" in etapa_seleccionada else ""
                                col_lote_ref_loc = next((c for c in row.index if "lote" in c.lower() and c.lower() != 'lote'), None)
                                if not col_lote_ref_loc: col_lote_ref_loc = next((c for c in row.index if "lote" in c.lower()), None)
                                col_ft_ref_loc = next((c for c in row.index if c.lower() == 'ft'), None)
                                
                                lote_str = row.get(col_lote_ref_loc, '') if col_lote_ref_loc else ''
                                ft_str = row.get(col_ft_ref_loc, '') if col_ft_ref_loc else ''
                                lote_txt = row.get('Propagacion', f"{lote_str} / FT {ft_str}".strip(' /'))

                                hover_text.append(f"Fecha: {fecha_val}{hora_txt}<br>Lote/FT: {lote_txt}<br>{etapa_info}Valor: <b>{val} {spec_gen['unit'] if spec_gen else ''}</b>{target_info}")

                        fig.add_trace(go.Scatter(
                            x=group[col_x_graf], y=group[parametro_a_graficar],
                            mode='lines+markers', name=f"{fase_tipo} ({spec_t['target']}°C)" if (es_temperatura and spec_t['target'] and "1. Control de Propagación" in etapa_seleccionada) else (parametro_a_graficar if fase_tipo == "General" else fase_tipo),
                            hovertext=hover_text, hoverinfo="text", line=dict(color=spec_t["color"], width=2),
                            marker=dict(size=9, symbol=spec_t["symbol"], color=colores_puntos, line=dict(width=1, color='#050505'))
                        ))

                    unit_label = "Temperatura (°C)" if es_temperatura else (f"{parametro_a_graficar} ({spec_gen['unit']})" if spec_gen else "UFC / Medición")
                    
                    xaxis_config = dict(showgrid=True, gridcolor="#1a1a1a", title="")
                    if col_x_graf == 'FECHA_DT': xaxis_config['tickformat'] = "%d-%b"
                    else: xaxis_config['type'] = 'category'

                    fig.update_layout(
                        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=xaxis_config,
                        yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title=unit_label), margin=dict(l=0, r=0, t=30, b=0),
                        showlegend=(etapa_seleccionada == "1. Control de Propagación"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No se encontraron columnas numéricas analizables en esta etapa.")
                    
            with col_tabla:
                st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ REGISTROS DE LA ETAPA</h3>", unsafe_allow_html=True)
                
                if etapa_seleccionada == "6. Envasado":
                    claves_fijas = ['lectura', 'envasado', 'lote']
                    # Ocultar o mostrar Producto dinámicamente
                    if 'prod_sel' in locals() and prod_sel == "Todos los Productos" and col_producto:
                        claves_fijas.append('producto')
                else:
                    claves_fijas = ['fecha', 'hora', 'ft', 'escala', 'etapa', 'lote', 'procedencia', 'tipo', 'tanque']
                    
                cols_fijas = [c for c in df_limpio.columns if any(k in c.lower() for k in claves_fijas)]
                cols_fijas = [c for c in cols_fijas if c not in ['FECHA_DT', 'batch_id', 'fase_block', 'Escala_Fase', 'Propagacion']]
                
                cols_mostrar = cols_fijas.copy()
                if 'parametro_a_graficar' in locals() and parametro_a_graficar not in cols_mostrar:
                    cols_mostrar.append(parametro_a_graficar)
                    
                df_mostrar = df_limpio[cols_mostrar].copy()
                for c in df_mostrar.columns:
                    if "etapa" in c.lower() or (c.lower() == "ft" and etapa_seleccionada != "6. Envasado") or ("ft" in c.lower() and etapa_seleccionada != "6. Envasado"):
                        df_mostrar[c] = df_mostrar[c].apply(lambda x: f"{int(float(x))}" if pd.notna(x) and str(x).strip() != "" and str(x).replace('.','',1).replace('-','',1).isdigit() else ("" if pd.isna(x) else str(x)))
                
                df_tabla_final = df_mostrar if etapa_seleccionada == "1. Control de Propagación" else df_mostrar.tail(15)
                st.dataframe(df_tabla_final.style.apply(aplicar_semaforo_tabla, axis=1).format(precision=2, na_rep=""), use_container_width=True, height=450)
            
    else:
        st.warning("La base de datos se cargó pero está vacía o sin datos válidos.")