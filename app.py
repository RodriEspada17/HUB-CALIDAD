import streamlit as st
import datetime
from utils.core import aplicar_estilo_neon

# Configuración inicial de la página
st.set_page_config(page_title="HUB BBO CALIDAD", layout="wide", initial_sidebar_state="expanded")

# Usuario fijo para desarrollo
st.session_state['usuario_actual'] = 'ADMIN_DEV'

bolivia_tz = datetime.timezone(datetime.timedelta(hours=-4))
fecha_actual = datetime.datetime.now(bolivia_tz).strftime("%d-%b-%Y %H:%M")

aplicar_estilo_neon()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; background-color: #050505 !important; color: #e0e0e0 !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #1a1a1a !important; }

    /* Ocultar botón de cerrar sesión en modo dev */
    div[data-testid="stSidebar"] div[data-testid="stButton"] { display: none !important; }

    .floating-tools { position: fixed; right: 0; top: 35%; display: flex; flex-direction: column; gap: 8px; z-index: 9999; }
    .tool-btn { background-color: #0a0a0a; border: 1px solid #1a1a1a; border-right: none; color: #888888; padding: 16px 8px; border-radius: 8px 0 0 8px; text-decoration: none !important; writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; font-size: 0.75rem; font-weight: 700; letter-spacing: 2px; transition: all 0.3s ease; display: flex; align-items: center; gap: 10px; box-shadow: -2px 2px 15px rgba(0,0,0,0.5); }
    .tool-btn:hover { color: #050505 !important; background-color: #a3ff00; border-color: #a3ff00; box-shadow: -5px 0 20px rgba(163, 255, 0, 0.3); }

    div[data-testid="stColumn"] div[data-testid="stButton"] > button {
        background-color: #0a0a0a !important; border: 1px solid #1a1a1a !important; padding: 24px !important; border-radius: 12px !important; min-height: 250px !important; width: 100% !important; display: flex !important; flex-direction: column !important; justify-content: flex-start !important; align-items: flex-start !important; text-align: left !important; transition: all 0.3s ease !important; box-shadow: 0 5px 15px rgba(0,0,0,0.5) !important; font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button { border-color: #a3ff00 !important; box-shadow: 0 0 20px rgba(163, 255, 0, 0.15) !important; transform: translateY(-4px) !important; }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p { color: #888888 !important; font-size: 0.9rem !important; line-height: 1.5 !important; white-space: pre-wrap !important; }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p strong:nth-of-type(1) { color: #a3ff00 !important; font-size: 1.15rem !important; letter-spacing: 2px !important; margin-bottom: 5px !important; display: inline-block !important; }
    div[data-testid="stColumn"] div[data-testid="stButton"] > button p strong:nth-of-type(2) { color: #ffffff !important; font-size: 1.35rem !important; display: block !important; margin-top: 15px !important; margin-bottom: 10px !important; letter-spacing: -0.5px !important; }

    /* Pastillas (Pills) con transición fluida */
    .pill-container { 
        margin-top: -65px; 
        margin-left: 24px; 
        margin-bottom: 30px; 
        pointer-events: none; 
        position: relative; 
        z-index: 10; 
        font-family: 'Inter', sans-serif !important; 
        transition: all 0.3s ease !important; /* <--- Agregamos esto para que sea suave */
    }
    
    /* EFECTO HOVER CONJUNTO (Tarjeta y pastilla se levantan juntas) */
    div[data-testid="stColumn"]:hover div[data-testid="stButton"] > button {
        border-color: #a3ff00 !important;
        box-shadow: 0 0 20px rgba(163, 255, 0, 0.15) !important;
        transform: translateY(-4px) !important;
    }
    div[data-testid="stColumn"]:hover .pill-container {
        transform: translateY(-4px) !important; /* <--- Levanta la pastilla al mismo tiempo */
    }
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style='text-align: center; margin-bottom: 5px;'>
        <div style='background-color: #0a0a0a; height: 60px; width: 60px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center; border: 2px solid #a3ff00; box-shadow: 0 0 10px rgba(163,255,0,0.2);'>
            <span style='font-size: 1.5rem;'>👤</span>
        </div>
        <p style='color: #ffffff; font-weight: 700; margin-top: 12px; margin-bottom: 0; letter-spacing: 1px;'>{st.session_state['usuario_actual'].upper()}</p>
        <span style='color: #a3ff00; font-size: 0.75rem; letter-spacing: 2px; font-weight: 600;'>MODO DESARROLLO</span>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid #1a1a1a; padding-bottom: 15px; margin-bottom: 30px; margin-top: 10px;'>
        <div>
            <h1 style='color: #a3ff00; font-size: 2rem; font-weight: 800; letter-spacing: 2px; margin: 0;'>HUB <span style='color: #ffffff;'>BBO</span></h1>
            <span style='color: #888888; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 500;'>Centro de Control y Monitoreo</span>
        </div>
        <div style='color: #555555; font-size: 0.75rem; display: flex; align-items: center; gap: 5px; font-weight: 600;'>
            <span>ÚLTIMA ACTUALIZACIÓN: {fecha_actual}</span>
        </div>
    </div>
    <div style='display: flex; gap: 30px; margin-bottom: 30px;'>
        <span style='color: #a3ff00; border-bottom: 2px solid #a3ff00; padding-bottom: 5px; font-size: 0.9rem; font-weight: 700; letter-spacing: 1px;'>■ MÓDULOS</span>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

txt_cc = "**///**\n\n**Control de Calidad**\n\nAnálisis SPC, tendencias y resumen de producción mensual.\n\n\n\n\n"
txt_mant = "**///**\n\n**Mantenimiento**\n\nGestión de órdenes de trabajo, paradas de planta, confiabilidad y repuestos.\n\n\n\n\n"
txt_elab = "**///**\n\n**Elaboración**\n\nControl de procesos de cocimiento, fermentación y filtración. Mermas y eficiencias.\n\n\n\n\n"
txt_env = "**///**\n\n**Envasado**\n\nSupervisión de líneas de llenado, mermas de empaque y eficiencias (OEE).\n\n\n\n\n"

with col1:
    if st.button(txt_cc, use_container_width=True, key="btn_cc"): st.switch_page("pages/CONTROL_CALIDAD.py")
    st.markdown("<div class='pill-container'><span class='pill-activo'>■ MÓDULO ACTIVO</span></div>", unsafe_allow_html=True)
with col2:
    if st.button(txt_mant, use_container_width=True, key="btn_mant"):
        try: st.switch_page("pages/MANTENIMIENTO.py")
        except: st.toast("🚧 Módulo de Mantenimiento en desarrollo.", icon="🚧")
    st.markdown("<div class='pill-container'><span class='pill-desarrollo'>■ EN DESARROLLO</span></div>", unsafe_allow_html=True)
with col3:
    if st.button(txt_elab, use_container_width=True, key="btn_elab"):
        try: st.switch_page("pages/ELABORACION.py")
        except: st.toast("🚧 Módulo de Elaboración en desarrollo.", icon="🚧")
    st.markdown("<div class='pill-container'><span class='pill-desarrollo'>■ EN DESARROLLO</span></div>", unsafe_allow_html=True)
with col4:
    if st.button(txt_env, use_container_width=True, key="btn_env"):
        try: st.switch_page("pages/ENVASADO.py")
        except: st.toast("🚧 Módulo de Envasado en desarrollo.", icon="🚧")
    st.markdown("<div class='pill-container'><span class='pill-desarrollo'>■ EN DESARROLLO</span></div>", unsafe_allow_html=True)

st.markdown("<br><hr style='border: 1px solid #1a1a1a;'><br>", unsafe_allow_html=True)