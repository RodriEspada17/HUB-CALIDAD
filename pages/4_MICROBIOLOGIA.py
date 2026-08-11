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
    
    /* Botón Volver */
    .btn-volver {
        display: inline-block; padding: 8px 16px; margin-bottom: 20px; border: 1px solid #1a1a1a; 
        border-radius: 6px; color: #888888; text-decoration: none; font-size: 0.8rem; font-weight: 700; 
        letter-spacing: 1px; transition: 0.3s;
    }
    .btn-volver:hover { border-color: #a3ff00; color: #a3ff00; background-color: rgba(163, 255, 0, 0.05); }
    
    /* Cajas y Selectores */
    .stSelectbox label { color: #888888 !important; font-weight: 600 !important; letter-spacing: 1px; font-size: 0.85rem !important; }
    </style>
""", unsafe_allow_html=True)

# Verificación de Seguridad
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.error("⚠️ Acceso denegado. Vuelve al inicio y loguéate.")
    st.stop()

# --- ENCABEZADO ---
st.markdown('<a href="CONTROL_CALIDAD" target="_self" class="btn-volver">◀ VOLVER A CALIDAD</a>', unsafe_allow_html=True)
st.markdown("<h1 style='color: #a3ff00; font-size: 2.2rem; font-weight: 800; letter-spacing: 2px; margin: 0;'>ANÁLISIS MICROBIOLÓGICOS <span style='color: #ffffff;'>(SPC)</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 0.95rem; margin-bottom: 2rem;'>Monitoreo estadístico de recuentos celulares y contaminación.</p>", unsafe_allow_html=True)

# --- DICCIONARIO DE PESTAÑAS (TUS GIDS REALES) ---
URL_BASE = "https://docs.google.com/spreadsheets/d/1CHG6Ndce1Hon9nUFikJqY5YIezYHHC1z_GKnWBmBOFQ/edit?pli=1&gid="

GIDS = {
    "1. Control de Propagación": "2050551093",
    "2. Análisis de Levadura": "160101583", 
    "3. Cocimiento": "1413638154",
    "4. Fermentación": "1692699392",
    "5. Filtración": "1258366654",
    "6. Envasado": "1542069577",
    "7. Agua y Materia Prima": "PONER_GID_AQUI" # <- Pestaña de la última captura
}

# --- SELECTOR DE ETAPA ---
col1, col2 = st.columns([1, 3])
with col1:
    etapa_seleccionada = st.selectbox("SELECCIONA LA ETAPA A MONITOREAR:", list(GIDS.keys()))

st.markdown("<hr style='border: 1px solid #1a1a1a; margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# --- MOTOR DE LIMPIEZA DE DATOS (DATA CLEANING AVANZADO) ---
@st.cache_data(ttl=60)
def cargar_y_limpiar_microbiologia(gid):
    if gid == "PONER_GID_AQUI": return None
        
    url_csv = generar_url_csv(URL_BASE + gid, gid)
    try:
        df = pd.read_csv(url_csv)
        
        # 1. Limpiar textos comunes
        df = df.replace({"Ausencia": 0, "ausencia": 0, "AUSENCIA": 0})
        df = df.replace({"NA": np.nan, "N/A": np.nan, "n/a": np.nan, "-": np.nan, "": np.nan})
        
        # 2. Manejo del "DNPC" (Tope visual)
        df = df.replace({"DNPC": 300, "dnpc": 300}) 
        
        # 3. Limpiar fechas falsas (1900)
        columnas_fecha = [col for col in df.columns if "fecha" in col.lower() or "semana" in col.lower()]
        for col in columnas_fecha:
            df.loc[df[col].astype(str).str.contains("1900", na=False), col] = np.nan
        if len(columnas_fecha) > 0:
            df = df.dropna(subset=[columnas_fecha[0]])
            
        # 4. Forzar conversión numérica a columnas métricas (Ignorar errores y volverlos NaN)
        columnas_excluidas = ['fecha', 'semana', 'lote', 'analista', 'producto', 'procedencia', 'tipo', 'generación', 'etapa', 'tanque', 'observaciones', 'ft', 'tp', 'muestra', 'sector', 'estado', 'calibre']
        
        for col in df.columns:
            if not any(excl in col.lower() for excl in columnas_excluidas):
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e:
        return f"Error: {e}"

# --- CARGA, DISPLAY Y GRÁFICOS ---
gid_actual = GIDS[etapa_seleccionada]

if gid_actual == "PONER_GID_AQUI":
    st.info(f"Falta configurar el GID para **{etapa_seleccionada}**. Agrégalo en el código.")
else:
    with st.spinner("Conectando con Google Sheets y filtrando data..."):
        df_limpio = cargar_y_limpiar_microbiologia(gid_actual)
        
    if isinstance(df_limpio, str):
        st.error(f"Error de conexión: {df_limpio}")
    elif df_limpio is not None and not df_limpio.empty:
        
        # 1. IDENTIFICAR COLUMNAS NUMÉRICAS PARA GRAFICAR
        cols_numericas = df_limpio.select_dtypes(include=[np.number]).columns.tolist()
        # Filtramos 'semana' u otros números que no sean métricas biológicas
        cols_graficables = [c for c in cols_numericas if "semana" not in c.lower() and "lote" not in c.lower() and "ft" not in c.lower()]
        
        # 2. INTERFAZ DIVIDIDA: GRÁFICO (Izquierda) / TABLA (Derecha)
        col_grafico, col_tabla = st.columns([2.5, 1.2])
        
        with col_grafico:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ GRÁFICO DE CONTROL (SPC)</h3>", unsafe_allow_html=True)
            
            if cols_graficables:
                parametro_a_graficar = st.selectbox("Selecciona el parámetro a analizar:", cols_graficables, label_visibility="collapsed")
                
                # Eje X: Buscamos una columna de fecha, si no hay, usamos el índice
                col_fecha = next((col for col in df_limpio.columns if "fecha" in col.lower()), df_limpio.index)
                
                # Crear gráfico Neón con Plotly
                fig = px.line(df_limpio, x=col_fecha, y=parametro_a_graficar, markers=True)
                fig.update_traces(line_color='#a3ff00', marker=dict(size=8, color='#a3ff00', line=dict(width=2, color='#050505')))
                
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#1a1a1a", title=""),
                    yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="UFC / Medición"),
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se encontraron columnas numéricas analizables en esta etapa.")
                
        with col_tabla:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ ÚLTIMOS REGISTROS</h3>", unsafe_allow_html=True)
            st.dataframe(df_limpio.tail(10), use_container_width=True, height=450)
            
    else:
        st.warning("La base de datos se cargó pero está vacía o sin datos válidos.")