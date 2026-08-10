import streamlit as st
import pandas as pd
import urllib.parse
from utils.core import aplicar_estilo_neon, generar_url_csv, cargar_datos

st.set_page_config(page_title="Exportar Datos", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_neon()

# --- CSS AVANZADO: ESTANDARIZACIÓN DE BOTONES Y ENLACES NEÓN ---
st.markdown("""
    <style>
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
    
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        background-color: #050505 !important;
        color: #a3ff00 !important;
        border: 1px solid #a3ff00 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        margin-bottom: 12px !important;
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
        margin: 0 !important;
    }

    /* Botón principal Neón */
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
        margin-top: 1.5rem !important;
    }
    .btn-wpp-neon:hover {
        background-color: #a3ff00 !important;
        color: #050505 !important;
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important;
        text-decoration: none !important;
    }

    /* Botón Secundario Gris Metálico (Para Grupos) */
    .btn-wpp-secondary {
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        background-color: #050505 !important;
        color: #888888 !important;
        border: 1px solid #333333 !important;
        padding: 9px 24px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        text-decoration: none !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        margin-top: 10px !important;
    }
    .btn-wpp-secondary:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #888888 !important;
        text-decoration: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR LA MEMORIA DEL HUB ---
if "reporte_listo" not in st.session_state:
    st.session_state.reporte_listo = False
if "mensaje_wpp" not in st.session_state:
    st.session_state.mensaje_wpp = ""
if "edit_phone" not in st.session_state:
    st.session_state.edit_phone = False
if "phone_number" not in st.session_state:
    st.session_state.phone_number = "59160996560"

def limpiar_estado():
    st.session_state.reporte_listo = False
    st.session_state.mensaje_wpp = ""

def toggle_edit_phone():
    st.session_state.edit_phone = not st.session_state.edit_phone

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
            st.markdown("<p style='color: #f87171;'>[ERROR] No se detectó columna de Producto.</p>", unsafe_allow_html=True)
            prod_sel = None

    with col3:
        ft_input = st.text_input("3. Ingrese FT", placeholder="Ej: 12", on_change=limpiar_estado)
        
    with col4:
        lote_input = st.text_input("4. Ingrese Lote FT", placeholder="Ej: 154", on_change=limpiar_estado)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BOTÓN DE BÚSQUEDA ---
    if st.button("BUSCAR Y GENERAR REPORTE"):
        st.session_state.reporte_listo = False
        
        if not col_ft or not col_lote:
            st.markdown("<p style='color: #f87171;'>[SISTEMA] No se encontraron las columnas FT y Lote FT.</p>", unsafe_allow_html=True)
        elif not ft_input or not lote_input:
            st.markdown("<p style='color: #facc15;'>[SISTEMA] Debes ingresar el FT y el Lote para buscar.</p>", unsafe_allow_html=True)
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
                st.markdown("<p style='color: #f87171;'>[ERROR] No se encontró ningún registro con esos datos.</p>", unsafe_allow_html=True)
            else:
                registro = df_filtro.iloc[0]
                
                mensaje = f"*REPORTE DE CALIDAD BBO*\n"
                mensaje += f"*Etapa:* {etapa_seleccionada}\n"
                mensaje += f"*Producto:* {prod_sel}\n"
                mensaje += f"*FT:* {ft_input} | *Lote FT:* {lote_input}\n"
                mensaje += f"-----------------------------------\n"
                
                for col in df_filtro.columns:
                    val = str(registro[col]).strip()
                    col_upper = str(col).upper()
                    
                    if "UNNAMED" in col_upper or val.upper() in ['NONE', 'NAN', 'N/A', '']:
                        continue
                    if col_upper in [str(col_prod).upper(), str(col_ft).upper(), str(col_lote).upper()]:
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
            
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                if st.session_state.edit_phone:
                    nuevo_num = st.text_input("Número de Destino:", value=st.session_state.phone_number)
                    st.session_state.phone_number = nuevo_num
                else:
                    st.text_input("Número de Destino (Solo Lectura):", value=st.session_state.phone_number, disabled=True)
            
            with col_t2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button("EDITAR", on_click=toggle_edit_phone, use_container_width=True)

            if st.session_state.phone_number:
                mensaje_codificado = urllib.parse.quote(st.session_state.mensaje_wpp)
                
                # Enlace directo al número
                url_whatsapp_directo = f"https://wa.me/{st.session_state.phone_number}?text={mensaje_codificado}"
                # Enlace general para elegir grupo o contacto
                url_whatsapp_grupos = f"https://api.whatsapp.com/send?text={mensaje_codificado}"
                
                st.markdown(f'<a href="{url_whatsapp_directo}" target="_blank" class="btn-wpp-neon">ENVIAR A DESTINO FIJO</a>', unsafe_allow_html=True)
                st.markdown(f'<a href="{url_whatsapp_grupos}" target="_blank" class="btn-wpp-secondary">SELECCIONAR GRUPO O CONTACTO</a>', unsafe_allow_html=True)

else:
    st.markdown("<p style='color: #f87171;'>[ERROR] Falla de conexión con la base de datos principal.</p>", unsafe_allow_html=True)