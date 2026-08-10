import streamlit as st
import pandas as pd
import urllib.parse
from utils.core import aplicar_estilo_neon, generar_url_csv, cargar_datos

# Configuración inicial
st.set_page_config(page_title="Exportar Datos", layout="wide", page_icon="▪️", initial_sidebar_state="expanded")
aplicar_estilo_neon()

# --- INICIALIZAR LA MEMORIA DEL HUB (SESSION STATE) ---
if "reporte_listo" not in st.session_state:
    st.session_state.reporte_listo = False
if "mensaje_wpp" not in st.session_state:
    st.session_state.mensaje_wpp = ""

# Función para borrar la memoria si el usuario cambia algo arriba
def limpiar_estado():
    st.session_state.reporte_listo = False
    st.session_state.mensaje_wpp = ""

# --- SIDEBAR ---
st.sidebar.page_link("app.py", label="◀ VOLVER AL INICIO")
st.sidebar.page_link("pages/CONTROL_CALIDAD.py", label="◀ VOLVER A CALIDAD")
st.sidebar.markdown("<br><hr style='border: 1px solid #1a1a1a;'>", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h2 style='text-transform: uppercase; font-size: 1.8rem;'>MÓDULO / <span style='color: #a3ff00;'>EXPORTAR DATOS (WPP)</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 1rem; margin-bottom: 2rem;'>Busca un lote específico y genera un reporte instantáneo para enviar por WhatsApp.</p>", unsafe_allow_html=True)

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
    # Purgar datos vacíos
    col_prod_temp = [c for c in df.columns if "PRODUCTO" in str(c).upper()]
    if col_prod_temp:
        df = df[~df[col_prod_temp[0]].astype(str).str.strip().str.upper().isin(['NAN', 'NONE', 'N/A', ''])]

    col_prod = col_prod_temp[0] if col_prod_temp else None
    col_ft = next((c for c in df.columns if str(c).strip().upper() == "FT"), None)
    col_lote = next((c for c in df.columns if "LOTE" in str(c).upper() and "FT" in str(c).upper()), None)
    
    if not col_lote:
        col_lote = next((c for c in df.columns if "LOTE" in str(c).upper()), None)

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
            st.error("No se detectó columna de Producto.")
            prod_sel = None

    with col3:
        ft_input = st.text_input("3. Ingrese FT", placeholder="Ej: 12", on_change=limpiar_estado)
        
    with col4:
        lote_input = st.text_input("4. Ingrese Lote FT", placeholder="Ej: 154", on_change=limpiar_estado)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BOTÓN DE BÚSQUEDA ---
    if st.button("🔍 BUSCAR Y GENERAR REPORTE"):
        st.session_state.reporte_listo = False # Reiniciamos por si había un error previo
        
        if not col_ft or not col_lote:
            st.error("⚠️ No se encontraron las columnas 'FT' y 'Lote FT' en esta base de datos.")
        elif not ft_input or not lote_input:
            st.warning("⚠️ Debes ingresar el FT y el Lote para buscar.")
        else:
            df_filtro = df.copy()
            
            if prod_sel.upper() == "CAPITAL":
                df_filtro = df_filtro[df_filtro[col_prod].astype(str).str.strip().str.upper().isin(["CAPITAL", "CORDILLERA", "REAL"])]
            elif prod_sel.upper() in ["MALTA REAL", "MALTA"]:
                df_filtro = df_filtro[df_filtro[col_prod].astype(str).str.strip().str.upper().isin(["MALTA REAL", "MALTA"])]
            else:
                df_filtro = df_filtro[df_filtro[col_prod].astype(str).str.strip().str.upper() == prod_sel.upper()]

            df_filtro = df_filtro[df_filtro[col_ft].astype(str).str.strip() == str(ft_input).strip()]
            df_filtro = df_filtro[df_filtro[col_lote].astype(str).str.strip() == str(lote_input).strip()]

            if df_filtro.empty:
                st.error("❌ No se encontró ningún registro con esos datos. Verifica que el FT y Lote sean correctos.")
            else:
                registro = df_filtro.iloc[0]
                
                # Armamos el mensaje
                mensaje = f"📊 *REPORTE DE CALIDAD BBO*\n"
                mensaje += f"⚙️ *Etapa:* {etapa_seleccionada}\n"
                mensaje += f"🍺 *Producto:* {prod_sel}\n"
                mensaje += f"🔖 *Lote FT:* {lote_input}  |  *FT:* {ft_input}\n"
                mensaje += f"-----------------------------------\n"
                
                for col in df_filtro.columns:
                    val = str(registro[col]).strip()
                    col_upper = str(col).upper()
                    
                    if "UNNAMED" in col_upper or val.upper() in ['NONE', 'NAN', 'N/A', '']:
                        continue
                    if col_upper in [str(col_prod).upper(), str(col_ft).upper(), str(col_lote).upper()]:
                        continue
                    
                    mensaje += f"▪️ *{col}:* {val}\n"
                
                mensaje += f"-----------------------------------\n"
                mensaje += f"💡 _Generado automáticamente desde BBO HUB_"

                # GUARDAMOS EN LA MEMORIA
                st.session_state.mensaje_wpp = mensaje
                st.session_state.reporte_listo = True


    # --- MOSTRAR RESULTADOS (FUERA DEL BOTÓN, USANDO LA MEMORIA) ---
    if st.session_state.reporte_listo:
        st.success("✅ ¡Datos encontrados con éxito!")
        
        col_prev, col_env = st.columns([1, 1])
        
        with col_prev:
            st.markdown("<h4 style='color: #a3ff00;'>VISTA PREVIA DEL MENSAJE</h4>", unsafe_allow_html=True)
            st.info(st.session_state.mensaje_wpp)
        
        with col_env:
            st.markdown("<h4 style='color: #a3ff00;'>ENVÍO POR WHATSAPP</h4>", unsafe_allow_html=True)
            num_wpp = st.text_input("Número de teléfono (con código de país, sin el '+')", placeholder="Ej: 59170000000")
            
            if num_wpp:
                mensaje_codificado = urllib.parse.quote(st.session_state.mensaje_wpp)
                url_whatsapp = f"https://wa.me/{num_wpp}?text={mensaje_codificado}"
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("🟢 ABRIR WHATSAPP Y ENVIAR", url_whatsapp, use_container_width=True)
            else:
                st.warning("Escribe el número de teléfono para generar el botón de envío.")

else:
    st.error("Error de conexión con la base de datos.")