import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from PIL import Image
from utils.core import aplicar_estilo_neon

# --- CONFIGURACIÓN DE FAVICON PRO ---
ruta_logo = "LogoBBO2.png" 
if os.path.exists(ruta_logo):
    icono = Image.open(ruta_logo)
else:
    icono = "💧"

# Configuración inicial
st.set_page_config(page_title="Control de Aguas SPC", page_icon=icono, layout="wide", initial_sidebar_state="collapsed")
aplicar_estilo_neon()

# ... (sigue tu CSS y el resto del código) ...

# --- CSS GLOBAL (INTER + NEÓN + DESPLEGABLES BLOQUEADOS + COMPRESIÓN VERTICAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; background-color: #050505 !important; color: #e0e0e0 !important; overflow-y: hidden !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; height: 0px !important; }
    
    /* COMPRESIÓN DE MÁRGENES PARA EVITAR SCROLL */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* BOTÓN VOLVER PRINCIPAL */
    div[data-testid="stButton"] > button { 
        background-color: transparent !important; border: 1px solid #1a1a1a !important; width: fit-content !important; 
        padding: 4px 12px !important; border-radius: 6px !important; transition: 0.3s !important; margin-bottom: 0px !important;
    }
    div[data-testid="stButton"] > button p { color: #888888 !important; font-weight: 700 !important; font-size: 0.75rem !important; letter-spacing: 1px !important; }
    div[data-testid="stButton"] > button:hover { border-color: #a3ff00 !important; background-color: rgba(163, 255, 0, 0.05) !important; }
    div[data-testid="stButton"] > button:hover p { color: #a3ff00 !important; }
        
    /* ELIMINAR EL FOCO PERMANENTE DESPUÉS DEL CLIC */
    div[data-testid="stButton"] > button:focus { box-shadow: none !important; outline: none !important; border-color: #1a1a1a !important; }
    div[data-testid="stButton"] > button:focus p { color: #888888 !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) { border-color: #1a1a1a !important; background-color: transparent !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) p { color: #888888 !important; }
    
    /* BLOQUEAR ESCRITURA EN DESPLEGABLES */
    div[data-baseweb="select"] input { width: 0px !important; opacity: 0 !important; position: absolute !important; pointer-events: none !important; }
    div[data-baseweb="select"], div[data-baseweb="select"] * { cursor: pointer !important; }
    
    .stSelectbox label { color: #888888 !important; font-weight: 600 !important; letter-spacing: 1px; font-size: 0.8rem !important; margin-bottom: 2px !important; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
col_b1, col_b2, _ = st.columns([1.5, 1.5, 7])
with col_b1:
    if st.button("◀ VOLVER A CALIDAD"): st.switch_page("pages/CONTROL_CALIDAD.py")
with col_b2:
    if st.button("◀ VOLVER AL INICIO"): st.switch_page("app.py")

# TÍTULO (Márgenes reducidos al máximo)
st.markdown("<h1 style='color: #a3ff00; font-size: 1.8rem; font-weight: 800; letter-spacing: 2px; margin: 0; margin-top: 5px;'>CONTROL DE AGUAS <span style='color: #ffffff;'>(SPC)</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.85rem; margin-bottom: 0.5rem;'>Monitoreo estadístico de parámetros físico-químicos del agua.</p>", unsafe_allow_html=True)

URL_CSV_AGUAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTfm3KfpLbZ6De9FzJE0rpGZbkB0soLJOCKFl1yjvQQMiMqef43JWcUL6s9OyIGP9hr1e067494EZOo/pub?output=csv&gid=1373914293"

# --- MATRIZ DE TANQUES Y ESTÁNDARES ---
TANQUES_AGUAS = {
    "POZO DE AGUA": {
        "Cloro": {"keys": ["cloro", "pozo"], "std": {"type": "range", "min": 0.1, "max": 0.5, "label": "0.1 - 0.5 ppm", "unit": "ppm"}},
    },
    "FILTRO DE ARENA": {
        "Dureza total": {"keys": ["arena", "dureza"], "std": {"type": "max", "val": 200, "label": "≤ 200 ppm", "unit": "ppm"}},
        "pH": {"keys": ["arena", "ph"], "std": {"type": "range", "min": 6.0, "max": 7.5, "label": "6.0 - 7.5", "unit": ""}},
        "Conductividad [uS/cm]": {"keys": ["arena", "us/cm"], "std": {"type": "max", "val": 1500, "label": "≤ 1500 uS/cm", "unit": "uS/cm"}},
        "Conductividad [ppm]": {"keys": ["arena", "ppm"], "std": {"type": "max", "val": 1000, "label": "≤ 1000 ppm", "unit": "ppm"}},
        "Alcalinidad Carbonatos": {"keys": ["arena", "carbonatos"], "exclude": ["bi", "bicarbonatos"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "Alcalinidad Bicarbonatos": {"keys": ["arena", "bicarbonatos"], "std": {"type": "max", "val": 370, "label": "≤ 370 ppm", "unit": "ppm"}},
    },
    "ABLANDADOR": {
        "Dureza total": {"keys": ["ablandador", "dureza"], "std": {"type": "max", "val": 5, "label": "≤ 5 ppm", "unit": "ppm"}},
        "pH": {"keys": ["ablandador", "ph"], "std": {"type": "range", "min": 6.0, "max": 7.5, "label": "6.0 - 7.5", "unit": ""}},
        "Conductividad [uS/cm]": {"keys": ["ablandador", "us/cm"], "std": {"type": "max", "val": 700, "label": "≤ 700 uS/cm", "unit": "uS/cm"}},
        "Conductividad [ppm]": {"keys": ["ablandador", "ppm"], "std": {"type": "max", "val": 350, "label": "≤ 350 ppm", "unit": "ppm"}},
        "Alcalinidad Carbonatos": {"keys": ["ablandador", "carbonatos"], "exclude": ["bi", "bicarbonatos"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "Alcalinidad Bicarbonatos": {"keys": ["ablandador", "bicarbonatos"], "std": {"type": "max", "val": 370, "label": "≤ 370 ppm", "unit": "ppm"}},
    },
    "DESALCALINIZADOR": {
        "Dureza total": {"keys": ["desalcalinizador", "dureza"], "std": {"type": "max", "val": 180, "label": "≤ 180 ppm", "unit": "ppm"}},
        "pH": {"keys": ["desalcalinizador", "ph"], "std": {"type": "range", "min": 6.0, "max": 7.5, "label": "6.0 - 7.5", "unit": ""}},
        "Conductividad [uS/cm]": {"keys": ["desalcalinizador", "us/cm"], "std": {"type": "max", "val": 700, "label": "≤ 700 uS/cm", "unit": "uS/cm"}},
        "Conductividad [ppm]": {"keys": ["desalcalinizador", "ppm"], "std": {"type": "max", "val": 350, "label": "≤ 350 ppm", "unit": "ppm"}},
        "Alcalinidad Carbonatos": {"keys": ["desalcalinizador", "carbonatos"], "exclude": ["bi", "bicarbonatos"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "Alcalinidad Bicarbonatos": {"keys": ["desalcalinizador", "bicarbonatos"], "std": {"type": "max", "val": 120, "label": "≤ 120 ppm", "unit": "ppm"}},
    },
    "FILTRO CARBON": {
        "Dureza total": {"keys": ["carbon", "dureza"], "std": {"type": "max", "val": 180, "label": "≤ 180 ppm", "unit": "ppm"}},
        "Cloro": {"keys": ["carbon", "cloro"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "pH": {"keys": ["carbon", "ph"], "std": {"type": "range", "min": 6.0, "max": 7.5, "label": "6.0 - 7.5", "unit": ""}},
        "Conductividad [uS/cm]": {"keys": ["carbon", "us/cm"], "std": {"type": "max", "val": 700, "label": "≤ 700 uS/cm", "unit": "uS/cm"}},
        "Conductividad [ppm]": {"keys": ["carbon", "ppm"], "std": {"type": "max", "val": 350, "label": "≤ 350 ppm", "unit": "ppm"}},
        "Alcalinidad Carbonatos": {"keys": ["carbon", "carbonatos"], "exclude": ["bi", "bicarbonatos"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "Alcalinidad Bicarbonatos": {"keys": ["carbon", "bicarbonatos"], "std": {"type": "max", "val": 120, "label": "≤ 120 ppm", "unit": "ppm"}},
    },
    "TK AGUA TRATADA": {
        "Dureza total": {"keys": ["tratada", "dureza"], "std": {"type": "max", "val": 180, "label": "≤ 180 ppm", "unit": "ppm"}},
        "pH": {"keys": ["tratada", "ph"], "std": {"type": "range", "min": 6.0, "max": 7.5, "label": "6.0 - 7.5", "unit": ""}},
        "Conductividad [uS/cm]": {"keys": ["tratada", "us/cm"], "std": {"type": "max", "val": 700, "label": "≤ 700 uS/cm", "unit": "uS/cm"}},
        "Conductividad [ppm]": {"keys": ["tratada", "ppm"], "std": {"type": "max", "val": 350, "label": "≤ 350 ppm", "unit": "ppm"}},
        "Alcalinidad Carbonatos": {"keys": ["tratada", "carbonatos"], "exclude": ["bi", "bicarbonatos"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "Alcalinidad Bicarbonatos": {"keys": ["tratada", "bicarbonatos"], "std": {"type": "max", "val": 120, "label": "≤ 120 ppm", "unit": "ppm"}},
    },
    "TK AGUA CALIENTE": {
        "Dureza total": {"keys": ["caliente", "dureza"], "std": {"type": "max", "val": 180, "label": "≤ 180 ppm", "unit": "ppm"}},
        "pH": {"keys": ["caliente", "ph"], "std": {"type": "range", "min": 6.0, "max": 7.5, "label": "6.0 - 7.5", "unit": ""}},
        "Conductividad [uS/cm]": {"keys": ["caliente", "us/cm"], "std": {"type": "max", "val": 700, "label": "≤ 700 uS/cm", "unit": "uS/cm"}},
        "Conductividad [ppm]": {"keys": ["caliente", "ppm"], "std": {"type": "max", "val": 350, "label": "≤ 350 ppm", "unit": "ppm"}},
        "Alcalinidad Carbonatos": {"keys": ["caliente", "carbonatos"], "exclude": ["bi", "bicarbonatos"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "Alcalinidad Bicarbonatos": {"keys": ["caliente", "bicarbonatos"], "std": {"type": "max", "val": 120, "label": "≤ 120 ppm", "unit": "ppm"}},
    },
    "TK AGUA FRIA F11": {
        "Dureza total": {"keys": ["fria", "dureza"], "std": {"type": "max", "val": 180, "label": "≤ 180 ppm", "unit": "ppm"}},
        "pH": {"keys": ["fria", "ph"], "std": {"type": "range", "min": 6.0, "max": 7.5, "label": "6.0 - 7.5", "unit": ""}},
        "Conductividad [uS/cm]": {"keys": ["fria", "us/cm"], "std": {"type": "max", "val": 700, "label": "≤ 700 uS/cm", "unit": "uS/cm"}},
        "Conductividad [ppm]": {"keys": ["fria", "ppm"], "std": {"type": "max", "val": 350, "label": "≤ 350 ppm", "unit": "ppm"}},
        "Alcalinidad Carbonatos": {"keys": ["fria", "carbonatos"], "exclude": ["bi", "bicarbonatos"], "std": {"type": "max", "val": 0, "label": "0 ppm", "unit": "ppm"}},
        "Alcalinidad Bicarbonatos": {"keys": ["fria", "bicarbonatos"], "std": {"type": "max", "val": 120, "label": "≤ 120 ppm", "unit": "ppm"}},
    }
}

@st.cache_data(ttl=60)
def cargar_datos_aguas():
    try:
        df = pd.read_csv(URL_CSV_AGUAS)
        
        # Limpieza básica y eliminación de "NSC" (No Se Controló)
        df = df.replace({"NA": np.nan, "N/A": np.nan, "n/a": np.nan, "-": np.nan, "": np.nan, "NSC": np.nan, "nsc": np.nan})
        
        # Buscar columna de fecha principal
        col_fecha = next((col for col in df.columns if "fecha" in col.lower()), None)
        if col_fecha:
            # 🔥 TRADUCTOR ESPAÑOL -> INGLÉS PARA QUE PYTHON ENTIENDA LOS MESES
            diccionario_meses = {
                "ene": "jan", "abr": "apr", "ago": "aug", "dic": "dec",
                "Ene": "Jan", "Abr": "Apr", "Ago": "Aug", "Dic": "Dec",
                "ENE": "JAN", "ABR": "APR", "AGO": "AUG", "DIC": "DEC"
            }
            df[col_fecha] = df[col_fecha].astype(str).replace(diccionario_meses, regex=True)
            
            df['FECHA_DT'] = pd.to_datetime(df[col_fecha], errors='coerce', dayfirst=True)
            df = df.dropna(subset=['FECHA_DT']).sort_values('FECHA_DT').reset_index(drop=True)
        else:
            df['FECHA_DT'] = df.index

        # Forzar numéricas a columnas que no son de contexto
        cols_contexto = ['fecha', 'hora', 'semana', 'punto', 'sector', 'analista', 'observaciones', 'estado']
        for col in df.columns:
            if not any(excl in col.lower() for excl in cols_contexto) and col != 'FECHA_DT':
                df[col] = df[col].astype(str).str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e:
        return f"Error: {e}"

def buscar_columna(df, keys, exclude=[]):
    """Busca exacto con palabras clave"""
    for c in df.columns:
        cl = c.lower().replace('\n', ' ').strip()
        if all(k in cl for k in keys) and not any(e in cl for e in exclude):
            return c
    return None

with st.spinner("Conectando con la base de datos de Aguas..."):
    df_limpio = cargar_datos_aguas()

if isinstance(df_limpio, str):
    st.error(f"Error de conexión: {df_limpio}")
elif df_limpio is not None and not df_limpio.empty:
    
    st.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 0px; margin-bottom: 10px;'>", unsafe_allow_html=True)

    # --- MENÚS ---
    c_filtro1, c_filtro2 = st.columns(2)
    with c_filtro1:
        tanque_sel = st.selectbox("SELECCIONA EL TANQUE / EQUIPO:", list(TANQUES_AGUAS.keys()))
    with c_filtro2:
        lista_params = list(TANQUES_AGUAS[tanque_sel].keys())
        param_sel = st.selectbox("SELECCIONA EL ANÁLISIS A MONITOREAR:", lista_params)

    st.markdown("<br>", unsafe_allow_html=True)

    col_real = buscar_columna(df_limpio, TANQUES_AGUAS[tanque_sel][param_sel].get("keys", []), TANQUES_AGUAS[tanque_sel][param_sel].get("exclude", []))

    col_grafico, col_tabla = st.columns([2.5, 1.2])

    with col_grafico:
        st.markdown("<h3 style='color: #ffffff; font-size: 1rem; margin-bottom: 10px; margin-top: -10px;'>■ GRÁFICO DE CONTROL (SPC)</h3>", unsafe_allow_html=True)
        
        if col_real and col_real in df_limpio.columns:
            df_graf = df_limpio.dropna(subset=[col_real]).copy()
            
            if not df_graf.empty:
                spec = TANQUES_AGUAS[tanque_sel][param_sel]["std"]
                unit_label = spec.get("unit", "")
                
                promedio = df_graf[col_real].mean()
                desviacion = df_graf[col_real].std()
                lcs = promedio + (3 * desviacion) if pd.notna(desviacion) and desviacion > 0 else promedio
                lci = promedio - (3 * desviacion) if pd.notna(desviacion) and desviacion > 0 else promedio
                
                fig = go.Figure()

                # Líneas de STD
                if spec["type"] == "min":
                    fig.add_hline(y=spec["val"], line_dash="dash", line_color="#4ade80", annotation_text=f"Mín STD: {spec['label']}", annotation_position="top left", annotation_font_color="#4ade80")
                elif spec["type"] == "max":
                    fig.add_hline(y=spec["val"], line_dash="dash", line_color="#f87171", annotation_text=f"Máx STD: {spec['label']}", annotation_position="top left", annotation_font_color="#f87171")
                elif spec["type"] == "range":
                    fig.add_hline(y=spec["min"], line_dash="dash", line_color="#4ade80", annotation_text=f"LSL: {spec['min']}")
                    fig.add_hline(y=spec["max"], line_dash="dash", line_color="#4ade80", annotation_text=f"USL: {spec['max']}")

                fig.add_trace(go.Scatter(
                    x=df_graf['FECHA_DT'], y=df_graf[col_real], mode='lines',
                    line=dict(color='rgba(163, 255, 0, 0.35)', width=1.5, dash='dot'), showlegend=False, hoverinfo='none'
                ))

                colores_puntos = []
                hover_text = []
                col_fecha_orig = next((c for c in df_limpio.columns if "fecha" in c.lower()), "FECHA_DT")

                for idx, row in df_graf.iterrows():
                    val = row[col_real]
                    fecha_str = row[col_fecha_orig] if col_fecha_orig in row else row['FECHA_DT'].strftime('%d-%b-%Y')
                    
                    cumple = True
                    if pd.notna(val):
                        v = float(val)
                        if spec["type"] == "min" and v < spec["val"]: cumple = False
                        elif spec["type"] == "max" and v > spec["val"]: cumple = False
                        elif spec["type"] == "range" and not (spec["min"] <= v <= spec["max"]): cumple = False

                    if cumple:
                        colores_puntos.append('#a3ff00')
                        estado = "<span style='color: #4ade80;'><b>✅ DENTRO DE STD</b></span>"
                    else:
                        colores_puntos.append('#f87171')
                        estado = "<span style='color: #f87171;'><b>🚨 FUERA DE STD</b></span>"

                    hover_text.append(f"Fecha: {fecha_str}<br>Valor: <b>{val} {unit_label}</b><br>Estado: {estado}<br>STD: {spec['label']}")

                fig.add_trace(go.Scatter(
                    x=df_graf['FECHA_DT'], y=df_graf[col_real], mode='lines+markers', name=param_sel,
                    hovertext=hover_text, hoverinfo="text", line=dict(color="#a3ff00", width=2),
                    marker=dict(size=9, symbol="circle", color=colores_puntos, line=dict(width=1, color='#050505'))
                ))

                # Ajustar la altura máxima del gráfico para evitar scroll vertical
                fig.update_layout(
                    height=320,
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="", tickformat="%d-%b"),
                    yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title=f"{param_sel} {f'({unit_label})' if unit_label else ''}"),
                    margin=dict(l=0, r=0, t=20, b=0), showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Los registros de este análisis están vacíos (o todos son NSC).")
        else:
            st.warning(f"No se encontró la columna para **{param_sel}** en el Excel.")

    with col_tabla:
        st.markdown("<h3 style='color: #ffffff; font-size: 1rem; margin-bottom: 10px; margin-top: -10px;'>■ ÚLTIMOS REGISTROS</h3>", unsafe_allow_html=True)
        
        def semaforo_aguas(row):
            estilos = [''] * len(row)
            for i, col in enumerate(row.index):
                if col == col_real:
                    val = row[col]
                    if pd.notna(val) and str(val).strip() != "":
                        cumple = True
                        try:
                            v = float(val)
                            spec = TANQUES_AGUAS[tanque_sel][param_sel]["std"]
                            if spec["type"] == "min" and v < spec["val"]: cumple = False
                            elif spec["type"] == "max" and v > spec["val"]: cumple = False
                            elif spec["type"] == "range" and not (spec["min"] <= v <= spec["max"]): cumple = False
                        except: pass
                        
                        if cumple: estilos[i] = 'background-color: #143324; color: #4ade80;'
                        else: estilos[i] = 'background-color: #3b181a; color: #f87171;'
            return estilos

        cols_contexto = []
        for c in df_limpio.columns:
            cl = c.lower()
            if "fecha" in cl and c != "FECHA_DT": cols_contexto.append(c)
            elif "semana" in cl: cols_contexto.append(c)

        if col_real and col_real in df_limpio.columns:
            cols_contexto.append(col_real)
            
        df_mostrar = df_limpio.dropna(subset=[col_real]) if col_real else df_limpio
        df_mostrar = df_mostrar[cols_contexto].tail(15)
        
        # Reducir la altura de la tabla para matar la barra de scroll (de 450 a 320)
        if not df_mostrar.empty and col_real:
            st.dataframe(df_mostrar.style.apply(semaforo_aguas, axis=1).format(precision=2, na_rep=""), use_container_width=True, height=320)
        else:
            st.dataframe(df_mostrar.style.format(precision=2, na_rep=""), use_container_width=True, height=320)

else:
    st.info("La base de datos está vacía por el momento.")