import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.core import aplicar_estilo_neon, generar_url_csv, cargar_datos

# Configuración inicial
st.set_page_config(page_title="Microbiología SPC", layout="wide", initial_sidebar_state="collapsed")
aplicar_estilo_neon()

# --- CSS GLOBAL (INTER + NEÓN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; background-color: #050505 !important; color: #e0e0e0 !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    
    /* BOTÓN VOLVER PRINCIPAL */
    div[data-testid="stButton"] > button { 
        background-color: transparent !important; 
        border: 1px solid #1a1a1a !important; 
        width: fit-content !important; 
        padding: 6px 16px !important; 
        border-radius: 6px !important; 
        transition: 0.3s !important; 
        margin-bottom: 10px !important;
    }
    div[data-testid="stButton"] > button p { 
        color: #888888 !important; font-weight: 700 !important; font-size: 0.8rem !important; letter-spacing: 1px !important; 
    }
    div[data-testid="stButton"] > button:hover { 
        border-color: #a3ff00 !important; background-color: rgba(163, 255, 0, 0.05) !important; 
    }
    div[data-testid="stButton"] > button:hover p { 
        color: #a3ff00 !important; 
    }
        
    /* ELIMINAR EL FOCO PERMANENTE DESPUÉS DEL CLIC */
    div[data-testid="stButton"] > button:focus,
    div[data-testid="stButton"] > button:active {
        box-shadow: none !important;
        outline: none !important;
        border-color: #1a1a1a !important;
    }
    div[data-testid="stButton"] > button:focus p {
        color: #888888 !important;
    }

    div[data-testid="stButton"] > button:focus:not(:hover) {
        border-color: #1a1a1a !important;
        background-color: transparent !important;
    }
    div[data-testid="stButton"] > button:focus:not(:hover) p {
        color: #888888 !important;
    }
    
    /* Cajas y Selectores */
    .stSelectbox label { color: #888888 !important; font-weight: 600 !important; letter-spacing: 1px; font-size: 0.85rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN INTELIGENTE: AGRUPAR PROPAGACIONES POR DÍAS CONSECUTIVOS ---
def agrupar_por_propagaciones(df):
    col_fecha = next((c for c in df.columns if "fecha" in c.lower()), None)
    if not col_fecha:
        return df
    
    # 1. Convertir a datetime y ordenar cronológicamente
    df['FECHA_DT'] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['FECHA_DT']).sort_values('FECHA_DT').reset_index(drop=True)
    
    if df.empty:
        return df

    # 2. Calcular salto entre fechas: si hay >1 día de diferencia, es una nueva propagación
    diferencias = df['FECHA_DT'].diff().dt.days
    df['batch_id'] = (diferencias > 1).cumsum()
    
    # 3. Formatear etiqueta tipo [30jun-3jul]
    def obtener_etiqueta_rango(sub_df):
        f_min = sub_df['FECHA_DT'].min()
        f_max = sub_df['FECHA_DT'].max()
        meses_es = {1:'ene', 2:'feb', 3:'mar', 4:'abr', 5:'may', 6:'jun', 7:'jul', 8:'ago', 9:'sep', 10:'oct', 11:'nov', 12:'dic'}
        
        inicio = f"{f_min.day}{meses_es[f_min.month]}"
        fin = f"{f_max.day}{meses_es[f_max.month]}"
        
        if inicio == fin:
            return f"[{inicio}]"
        return f"[{inicio}-{fin}]"

    # Mapear etiquetas
    mapa_etiquetas = {}
    for b_id, sub_df in df.groupby('batch_id'):
        mapa_etiquetas[b_id] = obtener_etiqueta_rango(sub_df)
        
    df['Propagacion'] = df['batch_id'].map(mapa_etiquetas)
    return df

# --- ENCABEZADO Y BOTONES DE NAVEGACIÓN ---
col_b1, col_b2, _ = st.columns([1.5, 1.5, 7])
with col_b1:
    if st.button("◀ VOLVER A CALIDAD"):
        st.switch_page("pages/CONTROL_CALIDAD.py")
with col_b2:
    if st.button("◀ VOLVER AL INICIO"):
        st.switch_page("app.py")

st.markdown("<h1 style='color: #a3ff00; font-size: 2.2rem; font-weight: 800; letter-spacing: 2px; margin: 0;'>ANÁLISIS MICROBIOLÓGICOS <span style='color: #ffffff;'>(SPC)</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.95rem; margin-bottom: 2rem;'>Monitoreo estadístico de recuentos celulares y contaminación.</p>", unsafe_allow_html=True)

# --- DICCIONARIO DE PESTAÑAS ---
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

# --- SELECTORES DE FILTRO ---
col1, col2 = st.columns([1.2, 2.8])
with col1:
    etapa_seleccionada = st.selectbox("SELECCIONA LA ETAPA A MONITOREAR:", list(GIDS.keys()))

st.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# --- MOTOR DE LIMPIEZA DE DATOS ---
@st.cache_data(ttl=60)
def cargar_y_limpiar_microbiologia(gid):
    if gid == "PONER_GID_AQUI": return None
        
    url_csv = generar_url_csv(URL_BASE + gid, gid)
    try:
        df = pd.read_csv(url_csv)
        
        # 1. Limpiar textos comunes
        df = df.replace({"Ausencia": 0, "ausencia": 0, "AUSENCIA": 0})
        df = df.replace({"NA": np.nan, "N/A": np.nan, "n/a": np.nan, "-": np.nan, "": np.nan})
        
        # 2. Manejo del "DNPC"
        df = df.replace({"DNPC": 300, "dnpc": 300}) 
        
        # 3. Limpiar fechas falsas (1900)
        columnas_fecha = [col for col in df.columns if "fecha" in col.lower() or "semana" in col.lower()]
        for col in columnas_fecha:
            df.loc[df[col].astype(str).str.contains("1900", na=False), col] = np.nan
        if len(columnas_fecha) > 0:
            df = df.dropna(subset=[columnas_fecha[0]])
            
        # 4. Forzar conversión numérica a columnas métricas
        columnas_excluidas = ['fecha', 'semana', 'lote', 'analista', 'producto', 'procedencia', 'tipo', 'generación', 'etapa', 'tanque', 'observaciones', 'ft', 'tp', 'muestra', 'sector', 'estado', 'calibre', 'propagacion', 'batch_id', 'fecha_dt']
        
        for col in df.columns:
            if not any(excl in col.lower() for excl in columnas_excluidas):
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e:
        return f"Error: {e}"

# --- CARGA Y RENDERIZADO ---
gid_actual = GIDS[etapa_seleccionada]

if gid_actual == "PONER_GID_AQUI":
    st.info(f"Falta configurar el GID para **{etapa_seleccionada}**. Agrégalo en el código.")
else:
    with st.spinner("Conectando con Google Sheets y estructurando lotes..."):
        df_limpio = cargar_y_limpiar_microbiologia(gid_actual)
        
    if isinstance(df_limpio, str):
        st.error(f"Error de conexión: {df_limpio}")
    elif df_limpio is not None and not df_limpio.empty:
        
        # 🔥 SI ES CONTROL DE PROPAGACIÓN, AGRUPAMOS Y HABITAMOS EL SUB-FILTRO POR LOTE
        if etapa_seleccionada == "1. Control de Propagación":
            df_limpio = agrupar_por_propagaciones(df_limpio)
            
            if 'Propagacion' in df_limpio.columns:
                lista_lotes = ["Todas las Propagaciones"] + list(df_limpio['Propagacion'].unique())
                
                c_lote, _ = st.columns([1.5, 2.5])
                with c_lote:
                    lote_sel = st.selectbox("PROPAGACIÓN / LOTE SELECCIONADO:", lista_lotes)
                
                if lote_sel != "Todas las Propagaciones":
                    df_limpio = df_limpio[df_limpio['Propagacion'] == lote_sel]

        # 1. IDENTIFICAR COLUMNAS NUMÉRICAS PARA GRAFICAR
        cols_numericas = df_limpio.select_dtypes(include=[np.number]).columns.tolist()
        cols_graficables = [c for c in cols_numericas if "semana" not in c.lower() and "lote" not in c.lower() and "ft" not in c.lower() and "batch_id" not in c.lower()]
        
        # 2. INTERFAZ DIVIDIDA: GRÁFICO (Izquierda) / TABLA (Derecha)
        col_grafico, col_tabla = st.columns([2.5, 1.2])
        
        with col_grafico:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ GRÁFICO DE CONTROL (SPC)</h3>", unsafe_allow_html=True)
            
            if cols_graficables:
                parametro_a_graficar = st.selectbox("Selecciona el parámetro a analizar:", cols_graficables, label_visibility="collapsed")
                col_fecha = next((col for col in df_limpio.columns if "fecha" in col.lower()), df_limpio.index)
                
                # --- MATEMÁTICA SPC ---
                promedio = df_limpio[parametro_a_graficar].mean()
                desviacion = df_limpio[parametro_a_graficar].std()
                lcs = promedio + (3 * desviacion) if pd.notna(desviacion) and desviacion > 0 else promedio
                
                # Alerta Roja si supera el límite
                colores_puntos = np.where(df_limpio[parametro_a_graficar] >= lcs, '#f87171', '#a3ff00')
                
                fig = go.Figure()
                
                # Texto hover enriquecido con el rango del lote
                hover_text = [f"Fecha: {f}<br>Lote: {p}<br>Valor: {v}" for f, p, v in zip(
                    df_limpio[col_fecha], 
                    df_limpio.get('Propagacion', ['N/A']*len(df_limpio)), 
                    df_limpio[parametro_a_graficar]
                )]
                
                # Línea principal
                fig.add_trace(go.Scatter(
                    x=df_limpio[col_fecha], y=df_limpio[parametro_a_graficar],
                    mode='lines+markers', name='Medición',
                    hovertext=hover_text, hoverinfo="text",
                    line=dict(color='rgba(163, 255, 0, 0.4)', width=2),
                    marker=dict(size=8, color=colores_puntos, line=dict(width=1, color='#050505'))
                ))
                
                # Línea de Promedio
                if pd.notna(promedio):
                    fig.add_hline(y=promedio, line_dash="dash", line_color="#888888", 
                                  annotation_text=f"Prom: {promedio:.1f}", annotation_position="bottom right")
                
                # Línea de LCS
                if pd.notna(lcs) and lcs > promedio:
                    fig.add_hline(y=lcs, line_dash="dot", line_color="#f87171", 
                                  annotation_text=f"LCS: {lcs:.1f}", annotation_position="top right", annotation_font_color="#f87171")
                
                fig.update_layout(
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#1a1a1a", title=""),
                    yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="UFC / Medición"),
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se encontraron columnas numéricas analizables en esta etapa.")
                
        with col_tabla:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ ÚLTIMOS REGISTROS</h3>", unsafe_allow_html=True)
            
            # Ocultamos columnas técnicas creadas en el background
            cols_mostrar = [c for c in df_limpio.columns if c not in ['FECHA_DT', 'batch_id']]
            st.dataframe(df_limpio[cols_mostrar].tail(10), use_container_width=True, height=450)
            
    else:
        st.warning("La base de datos se cargó pero está vacía o sin datos válidos.")