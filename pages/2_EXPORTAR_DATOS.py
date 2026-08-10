import streamlit as st
import pandas as pd
import urllib.parse
from utils.core import aplicar_estilo_neon, generar_url_csv, cargar_datos

# Configuración inicial
st.set_page_config(page_title="Exportar Datos", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_neon()

# --- CSS AVANZADO: ESTANDARIZACIÓN DE BOTONES Y ENLACES NEÓN ---
st.markdown("""
    <style>
    /* 1. Botones principales del módulo */
    .stButton > button {
        background-color: #050505 !important;
        color: #a3ff00 !important;
        border: 1px solid #a3ff00 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: #a3ff00 !important;
        color: #050505 !important;
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* 2. Transformar los enlaces del Sidebar en Botones Neón */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        background-color: #050505 !important;
        color: #a3ff00 !important;
        border: 1px solid #a3ff00 !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        justify-content: center !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
        background-color: #a3ff00 !important;
        color: #050505 !important;
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] > div {
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
        color: inherit !important; 
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }

    /* 3. Botón de WhatsApp Neón Principal */
    .btn-wpp-neon {
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        background-color: #050505 !important;
        color: #a3ff00 !important;
        border: 1px solid #a3ff00 !important;
        padding: 9px 24px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        text-decoration: none !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        margin-top: 10px !important;
    }
    .btn-wpp-neon:hover {
        background-color: #a3ff00 !important;
        color: #050505 !important;
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important;
        text-decoration: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR LA MEMORIA DEL HUB (SESSION STATE) ---
if "reporte_listo" not in st.session_state:
    st.session_state.reporte_listo = False
if "mensaje_wpp" not in st.session_state:
    st.session_state.mensaje_wpp = ""

def limpiar_estado():
    st.session_state.reporte_listo = False
    st.session_state.mensaje_wpp = ""

# --- DICCIONARIO DE UNIDADES ---
UNIDADES = {
    "EXTRACTO ORIGINAL": "[°Plato]",
    "EXTRACTO APARENTE": "[%w/w]",
    "EXTRACTO REAL": "[%w/w]",
    "ALCOHOL EN PESO": "[%w/w]",
    "ALCOHOL EN VOLUMEN": "[%v/v]",
    "COLOR": "[EBC]",
    "AMARGO": "[IBU]"
}

# --- SIDEBAR ---
st.sidebar.page_link("app.py", label="< VOLVER AL INICIO")
st.sidebar.page_link("pages/CONTROL_CALIDAD.py", label="< VOLVER A CALIDAD")
st.sidebar.markdown("<br><hr style='border: 1px solid #1a1a1a;'>", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h2 style='text-transform: uppercase; font-size: 1.8rem;'>MÓDULO / <span style='color: #a3ff00;'>EXPORTAR DATOS</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 1rem; margin-bottom: 2rem;'>Busca un lote específico y genera un reporte instantáneo para enviar por plataforma de mensajería.</p>", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS ---
URL_BASE = "https://docs.google.com/spreadsheets/d/1YiYwKJZsR7vBrLjCQBbGxzVxlTQEBRJVZEezJyQK3Yw/edit?pli=1&gid="
PESTANAS = {"Cocimiento": "1587615990", "Fin de Reposo": "79058483", "Filtración": "343087732", "Producto Terminado": "181144280"}

# --- FORMULARIO DE BÚSQUEDA ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    etapa_seleccionada = st.selectbox("1. Etapa del Proceso", list(PESTANAS.keys()), on_change=limpiar_estado)

gid_actual = PESTANAS[etapa_seleccionada]
url_completa = URL_BASE + gid_actual
df, _ = cargar_datos(generar_url_csv(url_completa, gid_actual))

if df is not None and not df.empty:
    col_prod_temp = [c for c in df.columns if "PRODUCTO" in str(c).upper()]
    if col_prod_temp:
        df = df[~df[col_prod_temp[0]].astype(str).str.strip().str.upper().isin(['NAN', 'NONE', 'N/A', ''])]

    col_prod = col_prod_temp[0] if col_prod_temp else None
    
    # Detección inteligente de columnas según la etapa
    col_id1 = None
    col_id2 = None
    
    if etapa_seleccionada == "Filtración":
        col_id1 = next((c for c in df.columns if str(c).strip().upper() == "TP"), None)
        col_id2 = next((c for c in df.columns if "LOTE" in str(c).upper() and "TP" in str(c).upper()), None)
        if not col_id2: col_id2 = next((c for c in df.columns if "LOTE" in str(c).upper()), None)
            
    elif etapa_seleccionada == "Producto Terminado":
        col_id1 = next((c for c in df.columns if "CODIGO" in str(c).upper() or "LOTE" in str(c).upper()), None)
        
    else: # Cocimiento y Fin de Reposo
        col_id1 = next((c for c in df.columns if str(c).strip().upper() == "FT"), None)
        col_id2 = next((c for c in df.columns if "LOTE" in str(c).upper() and "FT" in str(c).upper()), None)
        if not col_id2: col_id2 = next((c for c in df.columns if "LOTE" in str(c).upper()), None)

    # Selección de Producto
    with col2:
        if col_prod:
            productos_limpios = df[col_prod].astype(str).str.strip().str.upper()
            if etapa_seleccionada in ["Cocimiento", "Fin de Reposo"]:
                lista_productos = ["Amstel", "Schneider", "Capital", "Malta Real"]
            else:
                raw_unique = productos_limpios.unique()
                lista_productos = sorted(list(set([str(p).title() for p in raw_unique if str(p).upper() not in ['NAN', 'NONE', 'N/A', '']])))
            prod_sel = st.selectbox("2. Producto", lista_productos, on_change=limpiar_estado)
        else:
            st.markdown("<p style='color: #f87171;'>[ERROR] No se detectó columna de Producto.</p>", unsafe_allow_html=True)
            prod_sel = None

    # Campos de Entrada Dinámicos
    input_1 = ""
    input_2 = ""
    
    with col3:
        if etapa_seleccionada == "Filtración":
            input_1 = st.text_input("3. Ingrese TP", placeholder="Ej: 5", on_change=limpiar_estado)
        elif etapa_seleccionada == "Producto Terminado":
            input_1 = st.text_input("3. Ingrese Lote", placeholder="Ej: P-12345", on_change=limpiar_estado)
        else:
            input_1 = st.text_input("3. Ingrese FT", placeholder="Ej: 12", on_change=limpiar_estado)
            
    with col4:
        if etapa_seleccionada == "Filtración":
            input_2 = st.text_input("4. Ingrese Lote TP", placeholder="Ej: 154", on_change=limpiar_estado)
        elif etapa_seleccionada in ["Cocimiento", "Fin de Reposo"]:
            input_2 = st.text_input("4. Ingrese Lote FT", placeholder="Ej: 154", on_change=limpiar_estado)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BOTÓN DE BÚSQUEDA ---
    if st.button("BUSCAR Y GENERAR REPORTE"):
        st.session_state.reporte_listo = False
        
        # 1. Filtro General de Producto
        df_filtro = df.copy()
        if prod_sel.upper() == "CAPITAL":
            df_filtro = df_filtro[df_filtro[col_prod].astype(str).str.strip().str.upper().isin(["CAPITAL", "CORDILLERA", "REAL"])]
        elif prod_sel.upper() in ["MALTA REAL", "MALTA"]:
            df_filtro = df_filtro[df_filtro[col_prod].astype(str).str.strip().str.upper().isin(["MALTA REAL", "MALTA"])]
        else:
            df_filtro = df_filtro[df_filtro[col_prod].astype(str).str.strip().str.upper() == prod_sel.upper()]

        # 2. Filtro Específico por Etapa
        error_detectado = False
        
        if etapa_seleccionada == "Producto Terminado":
            if not col_id1:
                st.markdown("<p style='color: #f87171;'>[SISTEMA] No se encontró la columna de Lote/Código en la base de datos.</p>", unsafe_allow_html=True)
                error_detectado = True
            elif not input_1:
                st.markdown("<p style='color: #facc15;'>[SISTEMA] Debes ingresar el Lote (Ej: P-...) para buscar.</p>", unsafe_allow_html=True)
                error_detectado = True
            else:
                # Búsqueda flexible para encontrar el P-
                search_val = str(input_1).strip().upper()
                df_filtro = df_filtro[df_filtro[col_id1].astype(str).str.strip().str.upper().str.contains(search_val)]
                
        elif etapa_seleccionada == "Filtración":
            if not col_id1 or not col_id2:
                st.markdown("<p style='color: #f87171;'>[SISTEMA] No se encontraron las columnas TP y Lote TP.</p>", unsafe_allow_html=True)
                error_detectado = True
            elif not input_1 or not input_2:
                st.markdown("<p style='color: #facc15;'>[SISTEMA] Debes ingresar el TP y el Lote TP para buscar.</p>", unsafe_allow_html=True)
                error_detectado = True
            else:
                df_filtro = df_filtro[df_filtro[col_id1].astype(str).str.strip() == str(input_1).strip()]
                df_filtro = df_filtro[df_filtro[col_id2].astype(str).str.strip() == str(input_2).strip()]
                
        else: # Cocimiento y Fin de Reposo
            if not col_id1 or not col_id2:
                st.markdown("<p style='color: #f87171;'>[SISTEMA] No se encontraron las columnas FT y Lote FT.</p>", unsafe_allow_html=True)
                error_detectado = True
            elif not input_1 or not input_2:
                st.markdown("<p style='color: #facc15;'>[SISTEMA] Debes ingresar el FT y el Lote para buscar.</p>", unsafe_allow_html=True)
                error_detectado = True
            else:
                df_filtro = df_filtro[df_filtro[col_id1].astype(str).str.strip() == str(input_1).strip()]
                df_filtro = df_filtro[df_filtro[col_id2].astype(str).str.strip() == str(input_2).strip()]

        # 3. Generación del Reporte si no hubo errores
        if not error_detectado:
            if df_filtro.empty:
                st.markdown("<p style='color: #f87171;'>[ERROR] No se encontró ningún registro con esos datos.</p>", unsafe_allow_html=True)
            else:
                registro = df_filtro.iloc[0]
                
                # Encabezado dinámico
                mensaje = f"*REPORTE DE CALIDAD BBO*\n"
                mensaje += f"*Etapa:* {etapa_seleccionada}\n"
                mensaje += f"*Producto:* {prod_sel}\n"
                
                if etapa_seleccionada == "Producto Terminado":
                    lote_encontrado = str(registro[col_id1]).strip()
                    mensaje += f"*Lote:* {lote_encontrado}\n"
                elif etapa_seleccionada == "Filtración":
                    mensaje += f"*TP:* {input_1} | *Lote TP:* {input_2}\n"
                else:
                    mensaje += f"*FT:* {input_1} | *Lote FT:* {input_2}\n"
                    
                mensaje += f"-----------------------------------\n"
                
                # Omitir las columnas identificadoras para no repetirlas
                columnas_omitir = [str(col_prod).upper()]
                if col_id1: columnas_omitir.append(str(col_id1).upper())
                if col_id2: columnas_omitir.append(str(col_id2).upper())
                
                for col in df_filtro.columns:
                    val = str(registro[col]).strip()
                    col_upper = str(col).upper()
                    
                    if "UNNAMED" in col_upper or val.upper() in ['NONE', 'NAN', 'N/A', '']:
                        continue
                    if col_upper in columnas_omitir:
                        continue
                    
                    nombre_columna_formateado = col
                    for clave, unidad in UNIDADES.items():
                        if clave in col_upper:
                            nombre_columna_formateado = f"{col} {unidad}"
                            break
                    
                    mensaje += f"*{nombre_columna_formateado}:* {val}\n"
                
                mensaje += f"-----------------------------------\n"
                mensaje += f"_Generado automáticamente desde BBO HUB_"

                st.session_state.mensaje_wpp = mensaje
                st.session_state.reporte_listo = True

    # --- MOSTRAR RESULTADOS ---
    if st.session_state.reporte_listo:
        
        st.markdown("""
            <div style="border-left: 4px solid #a3ff00; padding: 12px 16px; margin-top: 10px; margin-bottom: 25px; background-color: #0a0a0a;">
                <span style="color: #a3ff00; font-weight: 700; font-family: 'Space Grotesk', sans-serif;">[SISTEMA]</span> 
                <span style="color: #e0e0e0; font-family: 'Space Grotesk', sans-serif; margin-left: 8px;">Datos localizados y procesados correctamente. Listo para exportar.</span>
            </div>
        """, unsafe_allow_html=True)
        
        col_prev, col_env = st.columns([1.2, 1])
        
        with col_prev:
            st.markdown("<h4 style='color: #888888; font-size: 0.9rem; letter-spacing: 1px;'>VISTA PREVIA DEL DOCUMENTO</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color: #0f0f0f; border: 1px solid #1a1a1a; padding: 15px; border-radius: 6px; color: #a3ff00; font-family: monospace; font-size: 0.9rem; white-space: pre-wrap;">{st.session_state.mensaje_wpp}</div>
            """, unsafe_allow_html=True)
        
        with col_env:
            st.markdown("<h4 style='color: #888888; font-size: 0.9rem; letter-spacing: 1px;'>PARÁMETROS DE ENVÍO</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color: #888888; font-size: 0.9rem; margin-bottom: 1.5rem;'>Haz clic en el botón inferior para abrir la aplicación de mensajería y seleccionar el grupo o contacto de destino.</p>", unsafe_allow_html=True)
            
            mensaje_codificado = urllib.parse.quote(st.session_state.mensaje_wpp)
            url_whatsapp_grupos = f"https://api.whatsapp.com/send?text={mensaje_codificado}"
            
            st.markdown(f'<a href="{url_whatsapp_grupos}" target="_blank" class="btn-wpp-neon">SELECCIONAR GRUPO O CONTACTO</a>', unsafe_allow_html=True)

else:
    st.markdown("<p style='color: #f87171;'>[ERROR] Falla de conexión con la base de datos principal.</p>", unsafe_allow_html=True)