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
    div[data-testid="stButton"] > button:hover p { color: #a3ff00 !important; }
        
    /* ELIMINAR EL FOCO PERMANENTE DESPUÉS DEL CLIC */
    div[data-testid="stButton"] > button:focus,
    div[data-testid="stButton"] > button:active {
        box-shadow: none !important; outline: none !important; border-color: #1a1a1a !important;
    }
    div[data-testid="stButton"] > button:focus p { color: #888888 !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) { border-color: #1a1a1a !important; background-color: transparent !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) p { color: #888888 !important; }
    
    .stSelectbox label { color: #888888 !important; font-weight: 600 !important; letter-spacing: 1px; font-size: 0.85rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- ESTÁNDARES DE TEMPERATURA POR ETAPA ---
SPECS_TEMP = {
    "Laboratorio": {"target": 25.0, "tol": 0.5, "min": 24.5, "max": 25.5, "color": "#60a5fa", "bg": "rgba(96, 165, 250, 0.06)", "symbol": "circle"},
    "Industrial 1": {"target": 18.0, "tol": 0.5, "min": 17.5, "max": 18.5, "color": "#a3ff00", "bg": "rgba(163, 255, 0, 0.06)", "symbol": "diamond"},
    "Industrial 2": {"target": 16.0, "tol": 0.5, "min": 15.5, "max": 16.5, "color": "#facc15", "bg": "rgba(250, 204, 21, 0.06)", "symbol": "square"},
    "Industrial 3": {"target": 14.0, "tol": 0.5, "min": 13.5, "max": 14.5, "color": "#f97316", "bg": "rgba(249, 115, 22, 0.06)", "symbol": "triangle-up"}
}

def agrupar_por_propagaciones(df):
    col_fecha = next((c for c in df.columns if "fecha" in c.lower()), None)
    col_hora = next((c for c in df.columns if "hora" in c.lower()), None)
    
    if not col_fecha: return df
    
    # Fusión Fecha + Hora para ordenamiento exacto por minuto
    if col_hora:
        df['FECHA_DT'] = pd.to_datetime(df[col_fecha].astype(str) + ' ' + df[col_hora].astype(str), errors='coerce', dayfirst=True)
    else:
        df['FECHA_DT'] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
        
    df = df.dropna(subset=['FECHA_DT']).sort_values('FECHA_DT').reset_index(drop=True)
    if df.empty: return df

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

# 🔥 CLASIFICACIÓN PRECISA LEYENDO LAS COLUMNAS 'ESCALA' Y 'ETAPA'
def clasificar_escala(df):
    col_escala = next((c for c in df.columns if "escala" in c.lower()), None)
    col_etapa = next((c for c in df.columns if "etapa" in c.lower()), None)
    
    fases = []
    for idx, row in df.iterrows():
        val_escala = str(row[col_escala]).strip().lower() if col_escala and pd.notna(row[col_escala]) else ""
        val_etapa = str(row[col_etapa]).strip() if col_etapa and pd.notna(row[col_etapa]) else ""
        
        etapa_num = "".join(filter(str.isdigit, val_etapa))
        
        if "lab" in val_escala:
            fases.append("Laboratorio")
        elif "ind" in val_escala or "plant" in val_escala or "tanque" in val_escala:
            if etapa_num in ["1", "2", "3"]:
                fases.append(f"Industrial {etapa_num}")
            else:
                fases.append("Industrial 1")
        else:
            if etapa_num in ["1", "2", "3"]:
                fases.append(f"Industrial {etapa_num}")
            else:
                fases.append("Laboratorio" if idx < 4 else "Industrial 1")
                
    df['Escala_Fase'] = fases
    return df

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
            
        columnas_excluidas = ['fecha', 'hora', 'semana', 'lote', 'escala', 'etapa', 'analista', 'producto', 'procedencia', 'tipo', 'generación', 'tanque', 'observaciones', 'ft', 'tp', 'muestra', 'sector', 'estado', 'calibre', 'propagacion', 'batch_id', 'fecha_dt', 'escala_fase']
        for col in df.columns:
            if not any(excl in col.lower() for excl in columnas_excluidas):
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e:
        return f"Error: {e}"

gid_actual = GIDS[etapa_seleccionada]

if gid_actual == "PONER_GID_AQUI":
    st.info(f"Falta configurar el GID para **{etapa_seleccionada}**. Agrégalo en el código.")
else:
    with st.spinner("Conectando con Google Sheets y estructurando datos..."):
        df_limpio = cargar_y_limpiar_microbiologia(gid_actual)
        
    if isinstance(df_limpio, str):
        st.error(f"Error de conexión: {df_limpio}")
    elif df_limpio is not None and not df_limpio.empty:
        
        if etapa_seleccionada == "1. Control de Propagación":
            df_limpio = agrupar_por_propagaciones(df_limpio)
            df_limpio = clasificar_escala(df_limpio)
            
            if 'Propagacion' in df_limpio.columns:
                lista_lotes = ["Todas las Propagaciones"] + list(df_limpio['Propagacion'].unique())
                c_lote, _ = st.columns([1.5, 2.5])
                with c_lote:
                    lote_sel = st.selectbox("PROPAGACIÓN / LOTE SELECCIONADO:", lista_lotes)
                
                if lote_sel != "Todas las Propagaciones":
                    df_limpio = df_limpio[df_limpio['Propagacion'] == lote_sel]

        # 1. IDENTIFICAR COLUMNAS NUMÉRICAS REALES
        cols_numericas = df_limpio.select_dtypes(include=[np.number]).columns.tolist()
        cols_prohibidas_graf = ['semana', 'lote', 'ft', 'batch_id', 'etapa', 'escala', 'escala_fase', 'hora']
        cols_graficables = [c for c in cols_numericas if not any(ex in c.lower() for ex in cols_prohibidas_graf)]
        
        col_grafico, col_tabla = st.columns([2.5, 1.2])
        
        with col_grafico:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ GRÁFICO DE CONTROL (SPC) MULTI-ESCALA</h3>", unsafe_allow_html=True)
            
            if cols_graficables:
                idx_default = next((i for i, c in enumerate(cols_graficables) if "temp" in c.lower()), 0)
                parametro_a_graficar = st.selectbox("Selecciona el parámetro a analizar:", cols_graficables, index=idx_default, label_visibility="collapsed")
                
                col_fecha_orig = next((col for col in df_limpio.columns if "fecha" in col.lower()), "FECHA_DT")
                col_hora_str = next((col for col in df_limpio.columns if "hora" in col.lower()), None)
                es_temperatura = "temp" in parametro_a_graficar.lower()
                
                fig = go.Figure()

                # 🔥 2. SOMBRAS Y FRANJAS DE TOLERANCIA POR BLOQUES TEMPORALES CONTINUOS
                if 'Escala_Fase' in df_limpio.columns:
                    df_limpio['fase_block'] = (df_limpio['Escala_Fase'] != df_limpio['Escala_Fase'].shift()).cumsum()
                    for _, sub_block in df_limpio.groupby('fase_block'):
                        fase_name = sub_block['Escala_Fase'].iloc[0]
                        spec_info = SPECS_TEMP.get(fase_name, {})
                        x_min = sub_block['FECHA_DT'].min()
                        x_max = sub_block['FECHA_DT'].max()
                        
                        # Fondo de la etapa
                        fig.add_vrect(x0=x_min, x1=x_max, fillcolor=spec_info.get('bg', 'rgba(255,255,255,0.02)'), layer="below", line_width=0)
                        
                        # Franja de tolerancia ±0.5°C
                        if es_temperatura and spec_info.get('min') is not None:
                            fig.add_shape(
                                type="rect", x0=x_min, x1=x_max, y0=spec_info['min'], y1=spec_info['max'],
                                fillcolor="rgba(74, 222, 128, 0.12)", line=dict(color="rgba(74, 222, 128, 0.3)", width=1),
                                layer="below"
                            )

                # 🔥 3. DIBUJAR PUNTOS Y EVALUAR ESTÁNDAR
                escala_orden = ["Laboratorio", "Industrial 1", "Industrial 2", "Industrial 3"]
                fases_presentes = [f for f in escala_orden if f in df_limpio['Escala_Fase'].values] if 'Escala_Fase' in df_limpio.columns else ["General"]

                for fase_tipo in fases_presentes:
                    group = df_limpio[df_limpio['Escala_Fase'] == fase_tipo] if 'Escala_Fase' in df_limpio.columns else df_limpio
                    spec = SPECS_TEMP.get(fase_tipo, {"color": "#a3ff00", "symbol": "circle", "target": None, "min": None, "max": None})
                    
                    colores_puntos = []
                    hover_text = []
                    
                    for idx, row in group.iterrows():
                        val = row[parametro_a_graficar]
                        hora_txt = f" {row[col_hora_str]}" if col_hora_str and pd.notna(row[col_hora_str]) else ""
                        
                        if es_temperatura and spec["min"] is not None:
                            if pd.notna(val) and (spec["min"] <= float(val) <= spec["max"]):
                                colores_puntos.append(spec["color"])
                                estado_txt = "<span style='color: #4ade80;'><b>✅ DENTRO DE STD</b></span>"
                            else:
                                colores_puntos.append('#f87171') # Rojo fuera de norma
                                estado_txt = "<span style='color: #f87171;'><b>🚨 FUERA DE STD</b></span>"
                                
                            target_txt = f"<br>STD Objetivos: <b>{spec['target']} ± {spec['tol']}°C</b><br>Estado: {estado_txt}"
                        else:
                            colores_puntos.append(spec["color"])
                            target_txt = ""

                        hover_text.append(
                            f"Fecha: {row[col_fecha_orig]}{hora_txt}<br>"
                            f"Lote: {row.get('Propagacion', 'N/A')}<br>"
                            f"Etapa: <b>{fase_tipo}</b><br>"
                            f"Valor: <b>{val} {'°C' if es_temperatura else ''}</b>"
                            f"{target_txt}"
                        )

                    fig.add_trace(go.Scatter(
                        x=group['FECHA_DT'], y=group[parametro_a_graficar],
                        mode='lines+markers', name=f"{fase_tipo} ({spec['target']}°C)" if es_temperatura and spec['target'] else fase_tipo,
                        hovertext=hover_text, hoverinfo="text",
                        line=dict(color=spec["color"], width=2),
                        marker=dict(size=9, symbol=spec["symbol"], color=colores_puntos, line=dict(width=1, color='#050505'))
                    ))

                # 🔥 4. FORMATO EJE X (CRONOLÓGICO Y LIMPIO)
                fig.update_layout(
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="", tickformat="%d-%b"),
                    yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="Temperatura (°C)" if es_temperatura else "UFC / Medición"),
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se encontraron columnas numéricas analizables en esta etapa.")
                
        with col_tabla:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ ÚLTIMOS REGISTROS</h3>", unsafe_allow_html=True)
            cols_mostrar = [c for c in df_limpio.columns if c not in ['FECHA_DT', 'batch_id', 'fase_block']]
            st.dataframe(df_limpio[cols_mostrar].tail(10), use_container_width=True, height=450)
            
    else:
        st.warning("La base de datos se cargó pero está vacía o sin datos válidos.")