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

# --- FUNCIÓN LIMPIADORA DE LLAVES ---
def limpiar_llave(serie):
    return serie.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.upper()

# --- LÓGICA DE PROCESAMIENTO ---
df_coc, _ = cargar_datos(generar_url_csv(URL_BASE + GID_COCIMIENTO, GID_COCIMIENTO))
df_rep, _ = cargar_datos(generar_url_csv(URL_BASE + GID_REPOSO, GID_REPOSO))

total_activos = 0
total_criticos = 0
promedio_global = 0.0

df_cervezas_final = pd.DataFrame()
df_malta_final = pd.DataFrame()
debug_info = []

if df_coc is not None and not df_coc.empty and df_rep is not None and not df_rep.empty:
    df_coc.columns = [str(c).strip().upper() for c in df_coc.columns]
    df_rep.columns = [str(c).strip().upper() for c in df_rep.columns]
    
    # ---------------------------------------------
    # FILTRO "ATRAPA-TODO" PARA TANQUES ACTIVOS
    # ---------------------------------------------
    col_envasado = next((c for c in df_coc.columns if "ENVASADO" in c), None)
    if col_envasado:
        mask_vacio = df_coc[col_envasado].isna()
        mask_texto = df_coc[col_envasado].astype(str).str.strip().str.upper().isin(['NAN', 'NONE', 'N/A', '', 'NO', 'FALSE', '0'])
        df_activos = df_coc[mask_vacio | mask_texto]
        debug_info.append(f"Columna de Envasado encontrada: '{col_envasado}'. Tanques marcados como activos: {len(df_activos)}")
    else:
        df_activos = df_coc
        debug_info.append("⚠️ NO se encontró columna con la palabra 'ENVASADO' en Cocimiento. Tomando toda la base.")

    col_prod_coc = next((c for c in df_activos.columns if "PRODUCTO" in c), None)
    col_ft_coc = next((c for c in df_activos.columns if c == "FT"), None)
    col_lote_coc = next((c for c in df_activos.columns if "LOTE" in c and "FT" in c), None)
    if not col_lote_coc: col_lote_coc = next((c for c in df_activos.columns if "LOTE" in c), None)
    
    # ---------------------------------------------
    # 1. PROCESAR MALTA REAL
    # ---------------------------------------------
    if col_prod_coc:
        col_llenado = next((c for c in df_activos.columns if "LLENADO" in c), None)
        df_malta = df_activos[df_activos[col_prod_coc].astype(str).str.upper().str.contains("MALTA", na=False)].copy()
        
        if col_llenado and not df_malta.empty:
            df_malta['FECHA_PARSED'] = pd.to_datetime(df_malta[col_llenado], dayfirst=True, errors='coerce')
            df_malta['DIAS ESTADIA'] = (pd.Timestamp.now() - df_malta['FECHA_PARSED']).dt.total_seconds() / 86400
            df_malta['ESTADO'] = df_malta['DIAS ESTADIA'].apply(lambda x: '■ CRÍTICO (> 6.5d)' if x >= 6.5 else '■ NORMAL')
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
    if col_prod_coc:
        df_cerv = df_activos[~df_activos[col_prod_coc].astype(str).str.upper().str.contains("MALTA", na=False)].copy()
        debug_info.append(f"Tanques activos de Cerveza en Cocimiento (Sin envasar): {len(df_cerv)}")
    else:
        df_cerv = pd.DataFrame()

    col_ft_rep = next((c for c in df_rep.columns if c == "FT"), None)
    col_lote_rep = next((c for c in df_rep.columns if "LOTE" in c and "FT" in c), None)
    if not col_lote_rep: col_lote_rep = next((c for c in df_rep.columns if "LOTE" in c), None)
    col_fecha_rep = next((c for c in df_rep.columns if "FECHA DE AN" in c or "FECHA" in c), None)
    
    if not col_ft_coc: debug_info.append("❌ Falta columna 'FT' en Cocimiento.")
    if not col_lote_coc: debug_info.append("❌ Falta columna 'LOTE FT' en Cocimiento.")
    if not col_ft_rep: debug_info.append("❌ Falta columna 'FT' en Fin de Reposo.")
    if not col_lote_rep: debug_info.append("❌ Falta columna 'LOTE' en Fin de Reposo.")
    if not col_fecha_rep: debug_info.append("❌ Falta columna de 'FECHA' en Fin de Reposo.")

    if col_ft_coc and col_lote_coc and col_ft_rep and col_lote_rep and col_fecha_rep and not df_cerv.empty:
        
        df_cerv['_MATCH_FT'] = limpiar_llave(df_cerv[col_ft_coc])
        df_cerv['_MATCH_LOTE'] = limpiar_llave(df_cerv[col_lote_coc])
        
        df_rep_clean = df_rep.copy()
        df_rep_clean['_MATCH_FT'] = limpiar_llave(df_rep_clean[col_ft_rep])
        df_rep_clean['_MATCH_LOTE'] = limpiar_llave(df_rep_clean[col_lote_rep])
        df_rep_clean = df_rep_clean.drop_duplicates(subset=['_MATCH_FT', '_MATCH_LOTE'], keep='last')
        
        # --- SOLUCIÓN DE LA COLISIÓN ---
        # Renombramos la fecha temporalmente para que no choque con la de Cocimiento
        df_rep_clean.rename(columns={col_fecha_rep: 'FECHA_REPOSO_CRUCE'}, inplace=True)
        
        df_merged = pd.merge(df_cerv, df_rep_clean[['_MATCH_FT', '_MATCH_LOTE', 'FECHA_REPOSO_CRUCE']], on=['_MATCH_FT', '_MATCH_LOTE'], how='inner')
        debug_info.append(f"Cruce exitoso (Match de FT y Lote): {len(df_merged)} tanques cruzados.")
        
        if not df_merged.empty:
            # Ahora calculamos en base a la columna segura
            df_merged['FECHA_PARSED'] = pd.to_datetime(df_merged['FECHA_REPOSO_CRUCE'], dayfirst=True, errors='coerce')
            df_merged['DIAS ESTADIA'] = (pd.Timestamp.now() - df_merged['FECHA_PARSED']).dt.total_seconds() / 86400
            
            def get_status_cerv(row):
                prod = str(row[col_prod_coc]).upper()
                dias = row['DIAS ESTADIA']
                if pd.isna(dias): return '■ N/A'
                if "SCHNEIDER" in prod and dias >= 10: return '■ CRÍTICO (> 10d)'
                if "AMSTEL" in prod and dias >= 21: return '■ CRÍTICO (> 21d)'
                return '■ NORMAL'
                
            df_merged['ESTADO'] = df_merged.apply(get_status_cerv, axis=1)
            
            df_merged = df_merged.dropna(subset=['DIAS ESTADIA'])
            df_merged['DIAS ESTADIA'] = df_merged['DIAS ESTADIA'].round(1)
            
            cols_c = []
            if col_lote_coc: cols_c.append(col_lote_coc)
            if col_ft_coc: cols_c.append(col_ft_coc)
            cols_c.extend([col_prod_coc, 'FECHA_REPOSO_CRUCE', 'DIAS ESTADIA', 'ESTADO'])
            
            df_cervezas_final = df_merged[cols_c].sort_values(by='DIAS ESTADIA', ascending=False)
            
            # La devolvemos a un nombre limpio y bonito para la tabla final
            df_cervezas_final.rename(columns={'FECHA_REPOSO_CRUCE': 'FECHA FIN DE REPOSO'}, inplace=True)
            
            total_activos += len(df_cervezas_final)
            total_criticos += len(df_cervezas_final[df_cervezas_final['ESTADO'].str.contains('CRÍTICO')])
            
    # Calcular promedio
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

# Función para pintar el estado sin emojis
def color_estado(val):
    if 'CRÍTICO' in str(val):
        return 'color: #f87171; font-weight: bold;'
    elif 'NORMAL' in str(val):
        return 'color: #4ade80;'
    return ''

with tab_cervezas:
    if not df_cervezas_final.empty:
        st.dataframe(df_cervezas_final.style.applymap(color_estado, subset=['ESTADO']), use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron tanques de cerveza activos con cruce de Fin de Reposo.")

with tab_malta:
    if not df_malta_final.empty:
        st.dataframe(df_malta_final.style.applymap(color_estado, subset=['ESTADO']), use_container_width=True, hide_index=True)
    else:
        st.info("No hay tanques de Malta Real activos en este momento.")

# --- MODO RAYOS X (DIAGNÓSTICO) ---
with st.expander("Modo Rayos X (Diagnóstico de Datos)"):
    for msg in debug_info:
        st.write(f"- {msg}")
    
    st.write("**Muestra de Cervezas (Cocimiento) antes del cruce:**")
    if 'df_cerv' in locals() and not df_cerv.empty:
        st.dataframe(df_cerv[[col_ft_coc, col_lote_coc, col_prod_coc]].head())