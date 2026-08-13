import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.core import aplicar_estilo_neon

# Configuración inicial
st.set_page_config(page_title="Control de Aguas SPC", layout="wide", initial_sidebar_state="collapsed")
aplicar_estilo_neon()

# --- CSS GLOBAL (INTER + NEÓN + DESPLEGABLES BLOQUEADOS) ---
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
    div[data-testid="stButton"] > button:hover { border-color: #00e5ff !important; background-color: rgba(0, 229, 255, 0.05) !important; }
    div[data-testid="stButton"] > button:hover p { color: #00e5ff !important; }
        
    /* BLOQUEAR ESCRITURA EN DESPLEGABLES */
    div[data-baseweb="select"] input { width: 0px !important; opacity: 0 !important; position: absolute !important; pointer-events: none !important; }
    div[data-baseweb="select"], div[data-baseweb="select"] * { cursor: pointer !important; }
    
    .stSelectbox label { color: #888888 !important; font-weight: 600 !important; letter-spacing: 1px; font-size: 0.85rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
col_b1, col_b2, _ = st.columns([1.5, 1.5, 7])
with col_b1:
    if st.button("◀ VOLVER A CALIDAD"): st.switch_page("pages/CONTROL_CALIDAD.py")
with col_b2:
    if st.button("◀ VOLVER AL INICIO"): st.switch_page("app.py")

# TÍTULO (Usando un tono cyan/agua para diferenciarlo del verde de Microbiología)
st.markdown("<h1 style='color: #00e5ff; font-size: 2.2rem; font-weight: 800; letter-spacing: 2px; margin: 0;'>CONTROL DE AGUAS <span style='color: #ffffff;'>(SPC)</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.95rem; margin-bottom: 2rem;'>Monitoreo estadístico de parámetros físico-químicos del agua.</p>", unsafe_allow_html=True)

URL_CSV_AGUAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTfm3KfpLbZ6De9FzJE0rpGZbkB0soLJOCKFl1yjvQQMiMqef43JWcUL6s9OyIGP9hr1e067494EZOo/pub?output=csv"

@st.cache_data(ttl=60)
def cargar_datos_aguas():
    try:
        df = pd.read_csv(URL_CSV_AGUAS)
        # Limpieza básica
        df = df.replace({"NA": np.nan, "N/A": np.nan, "n/a": np.nan, "-": np.nan, "": np.nan})
        
        # Buscar columna de fecha
        col_fecha = next((col for col in df.columns if "fecha" in col.lower()), None)
        if col_fecha:
            df['FECHA_DT'] = pd.to_datetime(df[col_fecha], errors='coerce', dayfirst=True)
            df = df.dropna(subset=['FECHA_DT']).sort_values('FECHA_DT').reset_index(drop=True)
        else:
            df['FECHA_DT'] = df.index

        # Forzar numericas a columnas que no son de contexto
        cols_contexto = ['fecha', 'hora', 'punto', 'sector', 'analista', 'observaciones', 'estado']
        for col in df.columns:
            if not any(excl in col.lower() for excl in cols_contexto) and col != 'FECHA_DT':
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e:
        return f"Error: {e}"

with st.spinner("Conectando con la base de datos de Aguas..."):
    df_limpio = cargar_datos_aguas()

if isinstance(df_limpio, str):
    st.error(f"Error de conexión: {df_limpio}")
elif df_limpio is not None and not df_limpio.empty:
    
    st.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)

    # Identificar numéricas para graficar
    cols_numericas = df_limpio.select_dtypes(include=[np.number]).columns.tolist()
    cols_prohibidas = ['semana', 'año', 'mes', 'dia', 'id', 'fecha_dt']
    cols_graficables = [c for c in cols_numericas if not any(ex in c.lower() for ex in cols_prohibidas)]

    col_grafico, col_tabla = st.columns([2.5, 1.2])

    with col_grafico:
        st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ GRÁFICO DE CONTROL (SPC)</h3>", unsafe_allow_html=True)
        
        if cols_graficables:
            parametro_a_graficar = st.selectbox("Selecciona el parámetro a analizar:", cols_graficables, index=0, label_visibility="collapsed")
            
            df_graf = df_limpio.dropna(subset=[parametro_a_graficar]).copy()
            
            if not df_graf.empty:
                promedio = df_graf[parametro_a_graficar].mean()
                desviacion = df_graf[parametro_a_graficar].std()
                lcs = promedio + (3 * desviacion) if pd.notna(desviacion) and desviacion > 0 else promedio
                lci = promedio - (3 * desviacion) if pd.notna(desviacion) and desviacion > 0 else promedio
                
                fig = go.Figure()

                # Líneas SPC
                fig.add_hline(y=promedio, line_dash="dash", line_color="#888888", annotation_text=f"Prom: {promedio:.2f}")
                if lcs > promedio: fig.add_hline(y=lcs, line_dash="dot", line_color="#f87171", annotation_text=f"LCS: {lcs:.2f}", annotation_font_color="#f87171")
                if lci < promedio: fig.add_hline(y=lci, line_dash="dot", line_color="#f87171", annotation_text=f"LCI: {lci:.2f}", annotation_font_color="#f87171")

                # Línea base
                fig.add_trace(go.Scatter(
                    x=df_graf['FECHA_DT'], y=df_graf[parametro_a_graficar], mode='lines',
                    line=dict(color='rgba(0, 229, 255, 0.35)', width=1.5, dash='dot'), showlegend=False, hoverinfo='none'
                ))

                # Puntos y Alertas
                colores_puntos = []
                hover_text = []
                col_fecha_orig = next((c for c in df_limpio.columns if "fecha" in c.lower()), "FECHA_DT")

                for idx, row in df_graf.iterrows():
                    val = row[parametro_a_graficar]
                    fecha_str = row[col_fecha_orig] if col_fecha_orig in row else row['FECHA_DT'].strftime('%d-%b-%Y')
                    
                    if pd.notna(val) and (val > lcs or val < lci):
                        colores_puntos.append('#f87171')
                        estado = "<span style='color: #f87171;'><b>🚨 ALERTA SPC</b></span>"
                    else:
                        colores_puntos.append('#00e5ff')
                        estado = "<span style='color: #4ade80;'><b>✅ NORMAL</b></span>"

                    hover_text.append(f"Fecha: {fecha_str}<br>Valor: <b>{val}</b><br>Estado: {estado}")

                fig.add_trace(go.Scatter(
                    x=df_graf['FECHA_DT'], y=df_graf[parametro_a_graficar], mode='lines+markers',
                    hovertext=hover_text, hoverinfo="text", line=dict(color="#00e5ff", width=2),
                    marker=dict(size=9, symbol="circle", color=colores_puntos, line=dict(width=1, color='#050505'))
                ))

                fig.update_layout(
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="", tickformat="%d-%b"),
                    yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="Valor"),
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos válidos para graficar este parámetro.")
        else:
            st.warning("No se encontraron columnas numéricas analizables.")

    with col_tabla:
        st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ ÚLTIMOS REGISTROS</h3>", unsafe_allow_html=True)
        
        # Ocultar columnas técnicas
        cols_tabla = [c for c in df_limpio.columns if c not in ['FECHA_DT', 'batch_id']]
        
        # Filtramos para mostrar los últimos 15
        df_mostrar = df_limpio[cols_tabla].tail(15)
        
        # Si elegimos un parámetro, lo ponemos al principio o aseguramos que se vea
        st.dataframe(df_mostrar.style.format(precision=2, na_rep=""), use_container_width=True, height=450)

else:
    st.info("La base de datos está vacía por el momento.")
