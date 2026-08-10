import streamlit as st
import pandas as pd
from utils.core import aplicar_estilo_neon, generar_url_csv, cargar_datos

# Configuración inicial
st.set_page_config(page_title="Estadía de Tanques", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_neon()

# --- CSS AVANZADO: DISEÑO DE DASHBOARD ---
st.markdown("""
    <style>
    .stButton > button { background-color: #050505 !important; color: #a3ff00 !important; border: 1px solid #a3ff00 !important; border-radius: 6px !important; font-weight: 600 !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { background-color: #a3ff00 !important; color: #050505 !important; box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important; transform: translateY(-2px) !important; }
    
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { background-color: #050505 !important; color: #a3ff00 !important; border: 1px solid #a3ff00 !important; border-radius: 6px !important; padding: 6px 12px !important; margin-bottom: 8px !important; transition: all 0.3s ease !important; display: flex !important; justify-content: center !important; }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover { background-color: #a3ff00 !important; color: #050505 !important; box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important; transform: translateY(-2px) !important; }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] > div { background-color: transparent !important; }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p { color: inherit !important; font-weight: 600 !important; font-size: 0.9rem !important; margin: 0 !important; }
    
    .metric-card { background-color: #0a0a0a; border: 1px solid #1a1a1a; padding: 24px; border-radius: 8px; text-align: center; transition: all 0.3s ease; }
    .metric-card:hover { border-color: #333333; }
    .metric-title { color: #888888; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: 600; }
    .metric-value-green { color: #a3ff00; font-size: 3rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; line-height: 1; }
    .metric-value-red { color: #f87171; font-size: 3rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; line-height: 1; }
    .metric-value-neutral { color: #ffffff; font-size: 3rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; line-height: 1; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.page_link("app.py", label="< VOLVER AL INICIO")
st.sidebar.page_link("pages/CONTROL_CALIDAD.py", label="< VOLVER A CALIDAD")
st.sidebar.markdown("<br><hr style='border: 1px solid #1a1a1a;'>", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h2 style='text-transform: uppercase; font-size: 1.8rem;'>MÓDULO / <span style='color: #a3ff00;'>ESTADÍA DE TANQUES</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 1rem; margin-bottom: 2rem;'>Monitoreo en tiempo real del tiempo de residencia en tanques clasificado por marca y etapa.</p>", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS ---
URL_BASE = "https://docs.google.com/spreadsheets/d/1YiYwKJZsR7vBrLjCQBbGxzVxlTQEBRJVZEezJyQK3Yw/edit?pli=1&gid="
GID_COCIMIENTO = "1587615990"
GID_REPOSO = "79058483"

# --- LÓGICA DE PROCESAMIENTO ---
df_coc, _ = cargar_datos(generar_url_csv(URL_BASE + GID_COCIMIENTO, GID_COCIMIENTO))
df_rep, _ = cargar_datos(generar_url_csv(URL_BASE + GID_REPOSO, GID_REPOSO))

total_activos = 0
total_criticos = 0
promedio_global = 0.0

df_cervezas_final = pd.DataFrame()
df_malta_final = pd.DataFrame()

if df_coc is not None and not df_coc.empty and df_rep is not None and not df_rep.empty:
    # Limpiar nombres de columnas
    df_coc.columns = [str(c).strip().upper() for c in df_coc.columns]
    df_rep.columns = [str(c).strip().upper() for c in df_rep.columns]
    
    # Identificar columna ¿Envasado? y filtrar TANQUES ACTIVOS
    col_envasado = next((c for c in df_coc.columns if "ENVASADO" in c), None)
    if col_envasado:
        # Si está vacío o tiene algo como 'NO' o 'NAN', sigue activo. Si tiene "SI" o "X", lo descartamos.
        df_activos = df_coc[df_coc[col_envasado].astype(str).str.strip().str.upper().isin(['NAN', 'NONE', 'N/A', '', 'NO', 'FALSE'])]
    else:
        df_activos = df_coc

    col_prod_coc = next((c for c in df_activos.columns if "PRODUCTO" in c), None)
    col_ft_coc = next((c for c in df_activos.columns if c == "FT"), None)
    col_lote_coc = next((c for c in df_activos.columns if "LOTE" in c and "FT" in c), None)
    if not col_lote_coc: col_lote_coc = next((c for c in df_activos.columns if "LOTE" in c), None)
    
    # ---------------------------------------------
    # 1. PROCESAR MALTA REAL (Desde Fin de Llenado)
    # ---------------------------------------------
    col_llenado = next((c for c in df_activos.columns if "LLENADO" in c), None)
    
    df_malta = df_activos[df_activos[col_prod_coc].astype(str).str.upper().str.contains("MALTA", na=False)].copy()
    
    if col_llenado and not df_malta.empty:
        df_malta['FECHA_PARSED'] = pd.to_datetime(df_malta[col_llenado], dayfirst=True, errors='coerce')
        # Calcular días (Fecha actual - Fecha de llenado)
        df_malta['DIAS ESTADIA'] = (pd.Timestamp.now() - df_malta['FECHA_PARSED']).dt.total_seconds() / 86400
        
        # Limite 6.5
        df_malta['ESTADO'] = df_malta['DIAS ESTADIA'].apply(lambda x: '🔴 CRÍTICO (> 6.5d)' if x >= 6.5 else '🟢 NORMAL')
        
        # Formatear para visualización
        df_malta = df_malta.dropna(subset=['DIAS ESTADIA'])
        df_malta['DIAS ESTADIA'] = df_malta['DIAS ESTADIA'].round(1)
        
        cols_m = []
        if col_lote_coc: cols_m.append(col_lote_coc)
        if col_ft_coc: cols_m.append(col_ft_coc)
        cols_m.extend([col_prod_coc, col_llenado, 'DIAS ESTADIA', 'ESTADO'])
        
        df_malta_final = df_malta[cols_m].sort_values(by='DIAS ESTADIA', ascending=False)
        total_activos += len(df_malta_final)
        total_criticos += len(df_malta_final[df_malta_final['ESTADO'].str.contains('CRÍTICO')])

    # ---------------------------------------------
    # 2. PROCESAR CERVEZAS (Desde Fin de Reposo)
    # ---------------------------------------------
    df_cerv = df_activos[~df_activos[col_prod_coc].astype(str).str.upper().str.contains("MALTA", na=False)].copy()
    
    col_ft_rep = next((c for c in df_rep.columns if c == "FT"), None)
    col_lote_rep = next((c for c in df_rep.columns if "LOTE" in c and "FT" in c), None)
    if not col_lote_rep: col_lote_rep = next((c for c in df_rep.columns if "LOTE" in c), None)
    col_fecha_rep = next((c for c in df_rep.columns if "FECHA DE AN" in c or "FECHA" in c), None)
    
    if col_ft_coc and col_lote_coc and col_ft_rep and col_lote_rep and col_fecha_rep and not df_cerv.empty:
        # Cruce de bases usando FT y LOTE FT
        df_cerv['_MATCH_FT'] = df_cerv[col_ft_coc].astype(str).str.strip().str.upper()
        df_cerv['_MATCH_LOTE'] = df_cerv[col_lote_coc].astype(str).str.strip().str.upper()
        
        df_rep['_MATCH_FT'] = df_rep[col_ft_rep].astype(str).str.strip().str.upper()
        df_rep['_MATCH_LOTE'] = df_rep[col_lote_rep].astype(str).str.strip().str.upper()
        
        # Inner join: Solo los tanques activos que YA estén en la pestaña de Reposo
        df_merged = pd.merge(df_cerv, df_rep[['_MATCH_FT', '_MATCH_LOTE', col_fecha_rep]], on=['_MATCH_FT', '_MATCH_LOTE'], how='inner')
        
        if not df_merged.empty:
            df_merged['FECHA_PARSED'] = pd.to_datetime(df_merged[col_fecha_rep], dayfirst=True, errors='coerce')
            df_merged['DIAS ESTADIA'] = (pd.Timestamp.now() - df_merged['FECHA_PARSED']).dt.total_seconds() / 86400
            
            # Lógica de límites
            def get_status_cerv(row):
                prod = str(row[col_prod_coc]).upper()
                dias = row['DIAS ESTADIA']
                if pd.isna(dias): return '⚪ N/A'
                if "SCHNEIDER" in prod and dias >= 10: return '🔴 CRÍTICO (> 10d)'
                if "AMSTEL" in prod and dias >= 21: return '🔴 CRÍTICO (> 21d)'
                return '🟢 NORMAL'
                
            df_merged['ESTADO'] = df_merged.apply(get_status_cerv, axis=1)
            
            df_merged = df_merged.dropna(subset=['DIAS ESTADIA'])
            df_merged['DIAS ESTADIA'] = df_merged['DIAS ESTADIA'].round(1)
            
            cols_c = []
            if col_lote_coc: cols_c.append(col_lote_coc)
            if col_ft_coc: cols_c.append(col_ft_coc)
            cols_c.extend([col_prod_coc, col_fecha_rep, 'DIAS ESTADIA', 'ESTADO'])
            
            df_cervezas_final = df_merged[cols_c].sort_values(by='DIAS ESTADIA', ascending=False)
            
            # Renombrar columna de fecha para que sea clara
            df_cervezas_final.rename(columns={col_fecha_rep: 'FECHA FIN DE REPOSO'}, inplace=True)
            
            total_activos += len(df_cervezas_final)
            total_criticos += len(df_cervezas_final[df_cervezas_final['ESTADO'].str.contains('CRÍTICO')])
            
    # Calcular promedio global
    suma_dias = 0
    if not df_malta_final.empty: suma_dias += df_malta_final['DIAS ESTADIA'].sum()
    if not df_cervezas_final.empty: suma_dias += df_cervezas_final['DIAS ESTADIA'].sum()
    if total_activos > 0: promedio_global = suma_dias / total_activos

# --- TARJETAS DE MÉTRICAS (DINÁMICAS) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Tanques Activos</div>
            <div class='metric-value-green'>{total_activos}</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    color_crit = "metric-value-red" if total_criticos > 0 else "metric-value-green"
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Alertas Críticas (Vencidos)</div>
            <div class='{color_crit}'>{total_criticos}</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Promedio Global (Días)</div>
            <div class='metric-value-neutral'>{promedio_global:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr style='border: 1px solid #1a1a1a;'><br>", unsafe_allow_html=True)

# --- PANEL PRINCIPAL DE CONTROL ---
st.markdown("<h4 style='color: #a3ff00; letter-spacing: 1px; font-size: 1.1rem;'>TABLEROS DE MONITOREO</h4>", unsafe_allow_html=True)

tab_cervezas, tab_malta = st.tabs(["CERVEZAS (Fin de Reposo)", "MALTA REAL (Cocimiento)"])

with tab_cervezas:
    if not df_cervezas_final.empty:
        st.dataframe(df_cervezas_final, use_container_width=True, hide_index=True)
    else:
        st.info("No hay tanques de Cerveza activos en etapa de Reposo en este momento, o no se encontró la columna de Envasado.")

with tab_malta:
    if not df_malta_final.empty:
        st.dataframe(df_malta_final, use_container_width=True, hide_index=True)
    else:
        st.info("No hay tanques de Malta Real activos en este momento.")