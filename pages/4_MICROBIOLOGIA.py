import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
    
    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px;
    }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; font-weight: 700 !important; }
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

# --- DICCIONARIO DE PESTAÑAS (GIDs) ---
# AQUÍ ES DONDE CONECTAMOS TU EXCEL. 
URL_BASE = "https://docs.google.com/spreadsheets/d/1CHG6Ndce1Hon9nUFikJqY5YIezYHHC1z_GKnWBmBOFQ/edit?pli=1&gid="

# TODO: Necesitamos que pongas el número GID correcto para cada pestaña de tu Google Sheets.
GIDS = {
    "1. Control de Propagación": "2050551093",  # GID de prueba (el que me pasaste antes)
    "2. Análisis de Levadura": "160101583", 
    "3. Cocimiento": "1413638154",
    "4. Fermentación": "1692699392",
    "5. Filtración": "1258366654",
    "6. Envasado": "1542069577"
}

# --- SELECTOR DE ETAPA ---
col1, col2 = st.columns([1, 3])
with col1:
    etapa_seleccionada = st.selectbox("SELECCIONA LA ETAPA:", list(GIDS.keys()))

st.markdown("<hr style='border: 1px solid #1a1a1a;'>", unsafe_allow_html=True)

# --- MOTOR DE LIMPIEZA DE DATOS (DATA CLEANING) ---
@st.cache_data(ttl=60) # Refresca los datos cada 60 segundos
def cargar_y_limpiar_microbiologia(gid):
    if gid == "PONER_GID_AQUI":
        return None # Evita error si aún no pones el GID
        
    url_csv = generar_url_csv(URL_BASE + gid, gid)
    try:
        df = pd.read_csv(url_csv)
        
        # 1. Limpiar "Ausencia" a 0
        df = df.replace({"Ausencia": 0, "ausencia": 0, "AUSENCIA": 0})
        
        # 2. Convertir NA a nulos (NaN) matemáticos
        df = df.replace({"NA": np.nan, "N/A": np.nan, "n/a": np.nan, "-": np.nan})
        
        # 3. Limpiar fechas falsas (1900) - asumiendo que tienes una columna que contiene "Fecha"
        columnas_fecha = [col for col in df.columns if "fecha" in col.lower() or "semana" in col.lower()]
        for col in columnas_fecha:
            # Si contiene "1900", borramos la fila (lo marcamos como nulo temporalmente)
            df.loc[df[col].astype(str).str.contains("1900", na=False), col] = np.nan
            
        # Borrar filas donde las fechas crìticas se volvieron nulas
        if len(columnas_fecha) > 0:
            df = df.dropna(subset=[columnas_fecha[0]])
            
        # 4. Manejo del temido "DNPC" (Demasiado Numeroso Para Contar)
        df = df.replace({"DNPC": 300, "dnpc": 300}) # Le damos un valor altísimo para que rompa el gráfico
        
        return df
    except Exception as e:
        return f"Error: {e}"

# --- CARGA Y DISPLAY ---
gid_actual = GIDS[etapa_seleccionada]

if gid_actual == "PONER_GID_AQUI":
    st.info(f"Falta configurar el GID para **{etapa_seleccionada}**. Busca el número al final del link de tu hoja de Google y ponlo en el código.")
else:
    with st.spinner(f"Cargando datos de {etapa_seleccionada}..."):
        df_limpio = cargar_y_limpiar_microbiologia(gid_actual)
        
    if isinstance(df_limpio, str):
        st.error(f"No se pudo conectar a la base de datos: {df_limpio}")
    elif df_limpio is not None and not df_limpio.empty:
        st.success(f"✅ Base de datos limpia y lista ({len(df_limpio)} registros).")
        st.dataframe(df_limpio.tail(15), use_container_width=True) # Muestra las últimas filas
    else:
        st.warning("La base de datos está vacía o hubo un error al procesar las filas.")
