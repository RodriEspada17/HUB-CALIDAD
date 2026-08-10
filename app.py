import streamlit as st
from utils.core import aplicar_estilo_neon

# Configuración inicial de la página
st.set_page_config(page_title="BBO HUB CALIDAD", layout="wide", initial_sidebar_state="expanded")

# --- INICIALIZAR ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Aplica la tipografía y el fondo base de nuestra librería
aplicar_estilo_neon()

# --- CSS GLOBAL DE ALTA GAMA ---
st.markdown("""
    <style>
    /* 1. Destructor total del menú feo por defecto de Streamlit */
    [data-testid="stSidebarNav"] {display: none !important;}
    
    /* 2. Botones Neón Globales */
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button { 
        background-color: #050505 !important; 
        border: 1px solid #a3ff00 !important; 
        border-radius: 6px !important; 
        transition: all 0.3s ease !important; 
        width: 100% !important; 
        padding: 0.8rem 1rem !important; 
    }
    div[data-testid="stButton"] > button p,
    div[data-testid="stFormSubmitButton"] > button p { 
        color: #a3ff00 !important; 
        font-weight: 600 !important; 
        font-family: 'Space Grotesk', sans-serif !important; 
        font-size: 1rem !important; 
        margin: 0 !important;
        letter-spacing: 1px;
    }
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #a3ff00 !important; 
        box-shadow: 0 0 15px rgba(163, 255, 0, 0.4) !important; 
        transform: translateY(-2px) !important; 
    }
    div[data-testid="stButton"] > button:hover p,
    div[data-testid="stFormSubmitButton"] > button:hover p { 
        color: #050505 !important; 
    }

    /* 3. Tarjetas Premium del Dashboard Principal */
    .dash-card {
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        padding: 30px;
        border-radius: 12px;
        transition: all 0.3s ease;
        text-align: left;
        margin-bottom: 15px;
        min-height: 180px;
    }
    .dash-card:hover {
        border-color: #333333;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .dash-title {
        color: #a3ff00;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 15px;
        text-transform: uppercase;
        border-bottom: 1px solid #1a1a1a;
        padding-bottom: 10px;
    }
    .dash-desc {
        color: #888888;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛑 PANTALLA DE LOGIN (Modo Bloqueo)
# ==========================================
if not st.session_state['autenticado']:
    st.markdown("""
        <style>
        /* Desaparecer menú lateral en Login */
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        /* Caja de Login Premium */
        [data-testid="stForm"] { 
            border: 1px solid #1a1a1a !important; 
            border-radius: 12px !important; 
            background-color: #0a0a0a !important; 
            padding: 3rem 2.5rem !important; 
            box-shadow: 0 15px 40px rgba(0,0,0,0.9), 0 0 20px rgba(163,255,0,0.03) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("<h1 style='text-align: center; color: #a3ff00; font-size: 3.5rem; letter-spacing: 3px; margin-bottom: 0;'>BBO HUB</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #888888; font-size: 0.9rem; letter-spacing: 2px; margin-bottom: 2.5rem;'>CONTROL CENTRAL DE CALIDAD</p>", unsafe_allow_html=True)
            
            usuario = st.text_input("Usuario", placeholder="Ingresa tu ID corporativo...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("ACCEDER AL SISTEMA")
            
            if submit:
                try:
                    if usuario in st.secrets["passwords"] and st.secrets["passwords"][usuario] == password:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_actual'] = usuario
                        st.rerun() 
                    else:
                        st.error("Credenciales incorrectas. Acceso denegado.")
                except Exception as e:
                    st.error("Error crítico: La Bóveda de Secretos no está configurada en Streamlit Cloud.")

# ==========================================
# 🟢 DASHBOARD PRINCIPAL (Modo Acceso)
# ==========================================
else:
    # --- SIDEBAR (Menú Estilizado y Profesional - SIN NAVEGACIÓN) ---
    st.sidebar.markdown(f"""
        <div style='background-color: #050505; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 25px;'>
            <span style='color: #888888; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase;'>Sesión Activa</span><br>
            <span style='color: #a3ff00; font-weight: bold; font-size: 1.2rem; letter-spacing: 1px;'>■ {st.session_state['usuario_actual'].upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<br><br><br><br><br><br><hr style='border: 1px solid #1a1a1a;'><br>", unsafe_allow_html=True)
    
    if st.sidebar.button("■ CERRAR SESIÓN"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- CONTENIDO PRINCIPAL ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 4.5rem; letter-spacing: 3px; color: #ffffff; margin-bottom: 0; line-height: 1;'>BBO <span style='color: #a3ff00;'>HUB</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 1.1rem; letter-spacing: 3px; margin-bottom: 4rem; text-transform: uppercase;'>Centro de Control y Monitoreo</p>", unsafe_allow_html=True)

    # --- CUADRÍCULA DE MÓDULOS (En el centro) ---
    col1, col2 = st.columns(2)
    
    # MÓDULO 1: CALIDAD
    with col1:
        st.markdown("""
            <div class='dash-card'>
                <div class='dash-title'>■ CONTROL DE CALIDAD</div>
                <div class='dash-desc'>Plataforma de monitoreo estadístico avanzado. Analiza tendencias fisicoquímicas en tiempo real, calcula métricas de capacidad (Cp/Cpk) y exporta reportes.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER A CALIDAD ➔", key="btn_calidad"):
            st.switch_page("pages/CONTROL_CALIDAD.py")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # MÓDULO 3: ELABORACIÓN
        st.markdown("""
            <div class='dash-card'>
                <div class='dash-title'>■ ELABORACIÓN</div>
                <div class='dash-desc'>Panel de control para procesos de cocimiento, fermentación y filtración. Monitoreo de mermas, extractos y eficiencias de sala.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER A ELABORACIÓN ➔", key="btn_elab"):
            try:
                st.switch_page("pages/ELABORACION.py")
            except:
                st.warning("🚧 Módulo en construcción. Archivo 'ELABORACION.py' aún no creado.")

    # MÓDULO 2: ESTADÍA
    with col2:
        st.markdown("""
            <div class='dash-card'>
                <div class='dash-title'>■ ESTADÍA DE TANQUES</div>
                <div class='dash-desc'>Tablero de seguimiento logístico para tiempos de maduración. Cuenta con sistema dual de alertas tempranas, panel de estado crítico y notificaciones.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER A ESTADÍA ➔", key="btn_estadia"):
            st.switch_page("pages/3_ESTADIA_TANQUES.py")
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # MÓDULO 4: ENVASADO
        st.markdown("""
            <div class='dash-card'>
                <div class='dash-title'>■ ENVASADO</div>
                <div class='dash-desc'>Supervisión de líneas de llenado, mermas de empaque, control de oxígeno disuelto y eficiencias operativas de turno (OEE).</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("ACCEDER A ENVASADO ➔", key="btn_envasado"):
            try:
                st.switch_page("pages/ENVASADO.py")
            except:
                st.warning("🚧 Módulo en construcción. Archivo 'ENVASADO.py' aún no creado.")
        
    st.markdown("<br><br><hr style='border: 1px solid #1a1a1a; margin-top: 3rem;'><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #333333; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;'>BBO Cervecería © 2026 - Departamento de Calidad</p>", unsafe_allow_html=True)