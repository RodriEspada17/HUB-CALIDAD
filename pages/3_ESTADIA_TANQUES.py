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

# --- FUNCIONES DE LIMPIEZA Y TRADUCCIÓN ---
def limpiar_llave(serie):
    return serie.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.upper()

def parsear_fechas_espanol(serie):
    # Diccionario para traducir los meses de Sheets (español) a Pandas (inglés)
    meses_traduccion = {
        'ene': 'jan', 'feb': 'feb', 'mar': 'mar', 'abr': 'apr', 'may': 'may', 'jun': 'jun',
        'jul': 'jul', 'ago': 'aug', 'sep': 'sep', 'oct': 'oct', 'nov': 'nov', 'dic': 'dec'
    }
    serie_str = serie.astype(str).str.lower()
    for es, en in meses_traduccion.items():
        serie_str = serie_str.str.replace(es, en)
    return pd.to_datetime(serie_str, dayfirst=True, errors='coerce')

# --- LÓGICA DE PROCESAMIENTO ---
df_coc_raw, _ = cargar_datos(generar_url_csv(URL_BASE + GID_COCIMIENTO, GID_COCIMIENTO))
df_rep_raw, _ = cargar_datos(generar_url_csv(URL_BASE + GID_REPOSO, GID_REPOSO))

total_activos = 0
total_criticos = 0

df_cervezas_final = pd.DataFrame()
df_malta_final = pd.DataFrame()

if df_coc_raw is not None and not df_coc_raw.empty and df_rep_raw is not None and not df_rep_raw.empty:
    df_coc = df_coc_raw.copy()
    df_rep = df_rep_raw.copy()
    
    df_coc.columns = [str(c).strip().upper() for c in df_coc.columns]
    df_rep.columns = [str(c).strip().upper() for c in df_rep.columns]
    
    col_prod_coc = next((c for c in df_coc.columns if "PRODUCTO" in c), None)
    col_ft_coc = next((c for c in df_coc.columns if c == "FT"), None)
    col_lote_coc = next((c for c in df_coc.columns if "LOTE" in c and "FT" in c), None)
    if not col_lote_coc: col_lote_coc = next((c for c in df_coc.columns if "LOTE" in c), None)
    
    if col_prod_coc and col_ft_coc and col_lote_coc:
        # DESTRUCTOR DE FILAS FANTASMA
        df_coc = df_coc.dropna(subset=[col_ft_coc, col_lote_coc, col_prod_coc])
        df_coc = df_coc[~df_coc[col_ft_coc].astype(str).str.strip().str.upper().isin(['NAN', 'NONE', 'N/A', ''])]
        
        # ---------------------------------------------
        # REGLA MAESTRA: ACTIVO/INACTIVO (Según Cocimiento)
        # ---------------------------------------------
        col_envasado = next((c for c in df_coc.columns if "ENVASADO" in c), None)
        if col_envasado:
            mask_vacio = df_coc[col_envasado].isna()
            mask_texto = df_coc[col_envasado].astype(str).str.strip().str.upper().isin(['NAN', 'NONE', 'N/A', '', 'NO', 'FALSE', '0', '-'])
            df_activos = df_coc[mask_vacio | mask_texto].copy()
        else:
            df_activos = df_coc.copy()

        # ---------------------------------------------
        # 1. PROCESAR MALTA REAL
        # ---------------------------------------------
        col_llenado = next((c for c in df_activos.columns if "LLENADO" in c), None)
        df_malta = df_activos[df_activos[col_prod_coc].astype(str).str.upper().str.contains("MALTA", na=False)].copy()
        
        if col_llenado and not df_malta.empty:
            # AQUI USAMOS EL TRADUCTOR DE FECHAS
            df_malta['FECHA_PARSED'] = parsear_fechas_espanol(df_malta[col_llenado])
            df_malta['DIAS ESTADIA'] = (pd.Timestamp.now() - df_malta['FECHA_PARSED']).dt.total_seconds() / 86400
            df_malta['ESTADO'] = df_malta['DIAS ESTADIA'].apply(lambda x: '■ CRÍTICO (> 6.5d)' if x >= 6.5 else '■ NORMAL')
            df_malta = df_malta.dropna(subset=['DIAS ESTADIA'])
            
            cols_m = [col_lote_coc, col_ft_coc, col_prod_coc, col_llenado, 'DIAS ESTADIA', 'ESTADO']
            df_malta_final = df_malta[cols_m].sort_values(by='DIAS ESTADIA', ascending=False)
            total_activos += len(df_malta_final)
            total_criticos += len(df_malta_final[df_malta_final['ESTADO'].str.contains('CRÍTICO')])

        # ---------------------------------------------
        # 2. PROCESAR CERVEZAS
        # ---------------------------------------------
        df_cerv = df_activos[~df_activos[col_prod_coc].astype(str).str.upper().str.contains("MALTA", na=False)].copy()
        
        col_ft_rep = next((c for c in df_rep.columns if c == "FT"), None)
        col_lote_rep = next((c for c in df_rep.columns if "LOTE" in c and "FT" in c), None)
        if not col_lote_rep: col_lote_rep = next((c for c in df_rep.columns if "LOTE" in c), None)
        col_fecha_rep = next((c for c in df_rep.columns if "FECHA DE AN" in c or "FECHA" in c), None)
        
        if col_ft_rep and col_lote_rep and col_fecha_rep and not df_cerv.empty:
            df_cerv['_MATCH_FT'] = limpiar_llave(df_cerv[col_ft_coc])
            df_cerv['_MATCH_LOTE'] = limpiar_llave(df_cerv[col_lote_coc])
            
            df_rep = df_rep.dropna(subset=[col_ft_rep, col_lote_rep])
            df_rep['_MATCH_FT'] = limpiar_llave(df_rep[col_ft_rep])
            df_rep['_MATCH_LOTE'] = limpiar_llave(df_rep[col_lote_rep])
            
            df_rep_clean = df_rep.drop_duplicates(subset=['_MATCH_FT', '_MATCH_LOTE'], keep='last').copy()
            df_rep_clean.rename(columns={col_fecha_rep: 'FECHA_REPOSO_CRUCE'}, inplace=True)
            
            df_merged = pd.merge(df_cerv, df_rep_clean[['_MATCH_FT', '_MATCH_LOTE', 'FECHA_REPOSO_CRUCE']], on=['_MATCH_FT', '_MATCH_LOTE'], how='inner')
            
            if not df_merged.empty:
                # AQUI TAMBIEN USAMOS EL TRADUCTOR DE FECHAS
                df_merged['FECHA_PARSED'] = parsear_fechas_espanol(df_merged['FECHA_REPOSO_CRUCE'])
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
                
                cols_c = [col_lote_coc, col_ft_coc, col_prod_coc, 'FECHA_REPOSO_CRUCE', 'DIAS ESTADIA', 'ESTADO']
                df_cervezas_final = df_merged[cols_c].sort_values(by='DIAS ESTADIA', ascending=False)
                df_cervezas_final.rename(columns={'FECHA_REPOSO_CRUCE': 'FECHA FIN DE REPOSO'}, inplace=True)
                
                total_activos += len(df_cervezas_final)
                total_criticos += len(df_cervezas_final[df_cervezas_final['ESTADO'].str.contains('CRÍTICO')])

# --- TARJETAS DE MÉTRICAS (2 COLUMNAS) ---
col1, col2 = st.columns(2)
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

st.markdown("<br><hr style='border: 1px solid #1a1a1a;'><br>", unsafe_allow_html=True)

# --- PANEL PRINCIPAL DE CONTROL SIMULTÁNEO ---
st.markdown("<h4 style='color: #a3ff00; letter-spacing: 1px; font-size: 1.1rem; margin-bottom: 1.5rem;'>TABLEROS DE MONITOREO SIMULTÁNEO</h4>", unsafe_allow_html=True)

col_cerv, col_malt = st.columns(2)

def aplicar_estilo_tabla(df):
    def color_estado(val):
        if 'CRÍTICO' in str(val):
            return 'color: #f87171; font-weight: bold;'
        elif 'NORMAL' in str(val):
            return 'color: #4ade80;'
        return ''
    
    return (df.style
            .set_properties(**{'background-color': '#0f0f0f', 'color': '#e0e0e0', 'border': '1px solid #1a1a1a'})
            .map(color_estado, subset=['ESTADO'])
            .format({"DIAS ESTADIA": "{:.1f}"}))

with col_cerv:
    st.markdown("""
        <div style='background-color: #0a0a0a; padding: 12px; border-radius: 6px; border: 1px solid #1a1a1a; text-align: center; margin-bottom: 15px;'>
            <span style='color: #a3ff00; font-weight: bold; letter-spacing: 1px;'>🍺 CERVEZAS</span> <span style='color: #888888;'>(FIN DE REPOSO)</span>
        </div>
    """, unsafe_allow_html=True)
    
    if not df_cervezas_final.empty:
        st.dataframe(aplicar_estilo_tabla(df_cervezas_final), use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron tanques de cerveza activos.")

with col_malt:
    st.markdown("""
        <div style='background-color: #0a0a0a; padding: 12px; border-radius: 6px; border: 1px solid #1a1a1a; text-align: center; margin-bottom: 15px;'>
            <span style='color: #a3ff00; font-weight: bold; letter-spacing: 1px;'>🌾 MALTA REAL</span> <span style='color: #888888;'>(COCIMIENTO)</span>
        </div>
    """, unsafe_allow_html=True)
    
    if not df_malta_final.empty:
        st.dataframe(aplicar_estilo_tabla(df_malta_final), use_container_width=True, hide_index=True)
    else:
        st.info("No hay tanques de Malta Real activos.")