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
        box-shadow: none !important; outline: none !important; border-color: #1a1a1a !important;
    }
    div[data-testid="stButton"] > button:focus p { color: #888888 !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) { border-color: #1a1a1a !important; background-color: transparent !important; }
    div[data-testid="stButton"] > button:focus:not(:hover) p { color: #888888 !important; }
    
    /* Cajas y Selectores */
    .stSelectbox label { color: #888888 !important; font-weight: 600 !important; letter-spacing: 1px; font-size: 0.85rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- ESTÁNDARES DE TEMPERATURA POR ETAPA ---
SPECS_TEMP = {
    "Laboratorio": {"target": 25.0, "tol": 0.5, "min": 24.5, "max": 25.5, "color": "#60a5fa", "bg": "rgba(96, 165, 250, 0.08)", "symbol": "circle"},
    "Industrial 1": {"target": 18.0, "tol": 0.5, "min": 17.5, "max": 18.5, "color": "#a3ff00", "bg": "rgba(163, 255, 0, 0.06)", "symbol": "diamond"},
    "Industrial 2": {"target": 16.0, "tol": 0.5, "min": 15.5, "max": 16.5, "color": "#facc15", "bg": "rgba(250, 204, 21, 0.06)", "symbol": "square"},
    "Industrial 3": {"target": 14.0, "tol": 0.5, "min": 13.5, "max": 14.5, "color": "#f97316", "bg": "rgba(249, 115, 22, 0.06)", "symbol": "triangle-up"}
}

# --- FUNCIÓN: AGRUPAR PROPAGACIONES POR DÍAS CONSECUTIVOS Y FECHA/HORA ---
def agrupar_por_propagaciones(df):
    col_fecha = next((c for c in df.columns if "fecha" in c.lower()), None)
    col_hora = next((c for c in df.columns if "hora" in c.lower()), None)
    
    if not col_fecha:
        return df
    
    # Fusionar Fecha y Hora para ordenamiento cronológico exacto
    if col_hora:
        df['FECHA_DT'] = pd.to_datetime(df[col_fecha].astype(str) + ' ' + df[col_hora].astype(str), errors='coerce', dayfirst=True)
    else:
        df['FECHA_DT'] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
        
    df = df.dropna(subset=['FECHA_DT']).sort_values('FECHA_DT').reset_index(drop=True)
    
    if df.empty: return df

    # Salto de >1 día determina una nueva propagación
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

# --- FUNCIÓN INTELIGENTE: CLASIFICAR ESCALA (LABORATORIO VS INDUSTRIAL 1, 2, 3) ---
def clasificar_escala(df):
    col_escala = next((c for c in df.columns if "escala" in c.lower() or "etapa" in c.lower() or "fase" in c.lower()), None)
    col_temp = next((c for c in df.columns if "temp" in c.lower()), None)
    
    fases = []
    for idx, row in df.iterrows():
        val_escala = str(row[col_escala]).strip().lower() if col_escala else ""
        
        if "lab" in val_escala:
            fases.append("Laboratorio")
        elif "ind" in val_escala or "plant" in val_escala or "tanque" in val_escala:
            # Si especifica la etapa directamente en el texto
            if "1" in val_escala:
                fases.append("Industrial 1")
            elif "2" in val_escala:
                fases.append("Industrial 2")
            elif "3" in val_escala:
                fases.append("Industrial 3")
            else:
                # Si sólo dice "Industrial", se deduce automáticamente por el rango de Temperatura
                if col_temp and pd.notna(row[col_temp]):
                    try:
                        t = float(str(row[col_temp]).replace(',', '.'))
                        if t >= 21.0:
                            fases.append("Laboratorio")
                        elif t >= 17.0:
                            fases.append("Industrial 1")
                        elif t >= 15.0:
                            fases.append("Industrial 2")
                        else:
                            fases.append("Industrial 3")
                    except:
                        fases.append("Industrial 1")
                else:
                    fases.append("Industrial 1")
        else:
            fases.append("Laboratorio" if idx < 4 else "Industrial 1")
            
    df['Escala_Fase'] = fases
    return df

# --- ENCABEZADO Y NAVEGACIÓN ---
col_b1, col_b2, _ = st.columns([1.5, 1.5, 7])
with col_b1:
    if st.button("◀ VOLVER A CALIDAD"): st.switch_page("pages/CONTROL_CALIDAD.py")
with col_b2:
    if st.button("◀ VOLVER AL INICIO"): st.switch_page("app.py")

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
            
        columnas_excluidas = ['fecha', 'hora', 'semana', 'lote', 'escala', 'analista', 'producto', 'procedencia', 'tipo', 'generación', 'etapa', 'tanque', 'observaciones', 'ft', 'tp', 'muestra', 'sector', 'estado', 'calibre', 'propagacion', 'batch_id', 'fecha_dt', 'escala_fase']
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
        
        # SI ES CONTROL DE PROPAGACIÓN: PROCESAR LOTES Y DETECTAR ESCALAS 1, 2 Y 3
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

        cols_numericas = df_limpio.select_dtypes(include=[np.number]).columns.tolist()
        cols_graficables = [c for c in cols_numericas if "semana" not in c.lower() and "lote" not in c.lower() and "ft" not in c.lower() and "batch_id" not in c.lower()]
        
        col_grafico, col_tabla = st.columns([2.5, 1.2])
        
        with col_grafico:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ GRÁFICO DE CONTROL (SPC) MULTI-ESCALA</h3>", unsafe_allow_html=True)
            
            if cols_graficables:
                parametro_a_graficar = st.selectbox("Selecciona el parámetro a analizar:", cols_graficables, label_visibility="collapsed")
                col_fecha = next((col for col in df_limpio.columns if "fecha" in col.lower()), df_limpio.index)
                col_hora_str = next((col for col in df_limpio.columns if "hora" in col.lower()), None)
                
                fig = go.Figure()

                # 🔥 DIBUJAR SOMBRAS DE FONDO TRANSPARENTES SEGÚN ETAPA
                if 'Escala_Fase' in df_limpio.columns:
                    for i in range(len(df_limpio) - 1):
                        x0 = df_limpio[col_fecha].iloc[i]
                        x1 = df_limpio[col_fecha].iloc[i+1]
                        fase_i = df_limpio['Escala_Fase'].iloc[i]
                        bg_color = SPECS_TEMP.get(fase_i, {}).get('bg', 'rgba(255,255,255,0.02)')
                        fig.add_vrect(x0=x0, x1=x1, fillcolor=bg_color, layer="below", line_width=0)

                # 🔥 DIBUJAR TRAZOS Y PUNTOS CON EVALUACIÓN DE ESTÁNDAR
                escala_orden = ["Laboratorio", "Industrial 1", "Industrial 2", "Industrial 3"]
                fases_presentes = [f for f in escala_orden if f in df_limpio['Escala_Fase'].values] if 'Escala_Fase' in df_limpio.columns else ["General"]

                es_temperatura = "temp" in parametro_a_graficar.lower()

                for fase_tipo in fases_presentes:
                    group = df_limpio[df_limpio['Escala_Fase'] == fase_tipo] if 'Escala_Fase' in df_limpio.columns else df_limpio
                    spec = SPECS_TEMP.get(fase_tipo, {"color": "#a3ff00", "symbol": "circle", "target": None, "min": None, "max": None})
                    
                    # Evaluación de semáforo (Rojo si sale de norma)
                    if es_temperatura and spec["min"] is not None:
                        colores_puntos = np.where((group[parametro_a_graficar] < spec["min"]) | (group[parametro_a_graficar] > spec["max"]), '#f87171', spec["color"])
                    else:
                        prom_g = group[parametro_a_graficar].mean()
                        std_g = group[parametro_a_graficar].std()
                        lcs_g = prom_g + (3 * std_g) if pd.notna(std_g) and std_g > 0 else prom_g
                        colores_puntos = np.where(group[parametro_a_graficar] >= lcs_g, '#f87171', spec["color"])

                    # Texto Hover enriquecido con Hora y Estándar
                    hover_text = []
                    for idx, row in group.iterrows():
                        hora_txt = f" {row[col_hora_str]}" if col_hora_str and pd.notna(row[col_hora_str]) else ""
                        target_txt = f"<br>STD: {spec['target']} ± {spec['tol']}°C" if es_temperatura and spec['target'] else ""
                        hover_text.append(f"Fecha: {row[col_fecha]}{hora_txt}<br>Lote: {row.get('Propagacion', 'N/A')}<br>Etapa: <b>{fase_tipo}</b><br>Valor: <b>{row[parametro_a_graficar]}</b>{target_txt}")

                    fig.add_trace(go.Scatter(
                        x=group[col_fecha], y=group[parametro_a_graficar],
                        mode='lines+markers', name=fase_tipo,
                        hovertext=hover_text, hoverinfo="text",
                        line=dict(color=spec["color"], width=2),
                        marker=dict(size=9, symbol=spec["symbol"], color=colores_puntos, line=dict(width=1, color='#050505'))
                    ))

                fig.update_layout(
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="#1a1a1a", title=""),
                    yaxis=dict(showgrid=True, gridcolor="#1a1a1a", title="°C" if es_temperatura else "UFC / Medición"),
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se encontraron columnas numéricas analizables en esta etapa.")
                
        with col_tabla:
            st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; margin-bottom: 15px;'>■ ÚLTIMOS REGISTROS</h3>", unsafe_allow_html=True)
            cols_mostrar = [c for c in df_limpio.columns if c not in ['FECHA_DT', 'batch_id']]
            st.dataframe(df_limpio[cols_mostrar].tail(10), use_container_width=True, height=450)
            
    else:
        st.warning("La base de datos se cargó pero está vacía o sin datos válidos.")