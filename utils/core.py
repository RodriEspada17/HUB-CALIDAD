import streamlit as st
import pandas as pd
import re
import unicodedata

# 1. DISEÑO CORPORATIVO TECH (Dark + Lime Green)
def aplicar_estilo_neon():
    import streamlit as st
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

        .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Space Grotesk', sans-serif; }
        
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-family: 'Space Grotesk', sans-serif !important;
            text-shadow: none !important;
            text-transform: none !important;
        }

        /* --- MENÚ LATERAL (NEON GREEN) --- */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
            border-right: 1px solid #1a1a1a;
        }
        
        /* Enlaces del menú en verde neón */
        [data-testid="stSidebarNav"] a {
            color: #a3ff00 !important;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        [data-testid="stSidebarNav"] a:hover {
            background-color: rgba(163, 255, 0, 0.15) !important;
            text-shadow: 0 0 8px #a3ff00;
        }

        /* Hack CSS para renombrar 'app' a '🏠 Home' */
        [data-testid="stSidebarNav"] ul li:first-child span {
            font-size: 0px; /* Oculta el texto original */
        }
        [data-testid="stSidebarNav"] ul li:first-child span::before {
            content: "🏠 Home";
            font-size: 1.1rem; /* Restaura el tamaño para el texto nuevo */
            color: #a3ff00;
        }
        /* --------------------------------- */

        div.stButton > button:first-child {
            background-color: #050505;
            color: #a3ff00;
            border: 1px solid #a3ff00;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
            padding: 10px 24px;
        }
        div.stButton > button:first-child:hover {
            background-color: #a3ff00;
            color: #050505;
            box-shadow: 0 0 15px rgba(163, 255, 0, 0.2);
            transform: translateY(-2px);
        }
        
        [data-testid="stDataFrame"] { background-color: #0f0f0f; border-radius: 8px; border: 1px solid #1a1a1a; }
        label, .st-emotion-cache-1y4p8pa { color: #888888 !important; font-weight: 600; font-family: 'Space Grotesk', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. ESPECIFICACIONES (TOL_MIN, TOL_MAX, STD_MIN, STD_MAX)
SPECS_COCIMIENTO_CCR = {"EXTRACTO ORIGINAL": (14.0, 15.0, 14.1, 14.9), "EO": (14.0, 15.0, 14.1, 14.9), "EXTRACTO": (14.0, 15.0, 14.1, 14.9)}
SPECS_COCIMIENTO_MALTA = {"EXTRACTO ORIGINAL": (14.4, 15.3, 14.5, 15.2), "EO": (14.4, 15.3, 14.5, 15.2), "EXTRACTO APARENTE": (14.4, 15.3, 14.5, 15.2), "EA": (14.4, 15.3, 14.5, 15.2)}
SPECS_REPOSO_CCR = {
    "EXTRACTO": (14.0, 15.0, 14.1, 14.9), "EO": (14.0, 15.0, 14.1, 14.9), 
    "EA": (2.70, 3.30, 2.80, 3.20), "ALCOHOL": (5.80, 6.40, 5.90, 6.30), "ALC": (5.80, 6.40, 5.90, 6.30),
    "COLOR": (5.90, 8.90, 6.40, 8.40), "AMARGO": (9.50, 13.50, 10.00, 13.00), 
    "PH": (3.95, 4.45, 4.05, 4.35), "TURBIDEZ": (0, 30.0, 0, 30.0), "DIACETILO": (0, 100.0, 0, 100.0)
}
SPECS_REPOSO_MALTA = {
    "EXTRACTO ORIGINAL": (14.4, 15.3, 14.5, 15.2), "EO": (14.4, 15.3, 14.5, 15.2),
    "EXTRACTO APARENTE": (14.4, 15.3, 14.5, 15.2), "EA": (14.4, 15.3, 14.5, 15.2),
    "ALCOHOL": (0, 0.50, 0, 0.20), "COLOR": (108.0, 148.0, 118.0, 138.0), 
    "AMARGO": (7.50, 10.50, 8.00, 10.00), "PH": (4.15, 4.65, 4.25, 4.55)
}
SPECS_PT_CCR = {
    "EXTRACTO ORIGINAL": (10.0, 10.60, 10.10, 10.50), "EO": (10.0, 10.60, 10.10, 10.50),
    "EXTRACTO APARENTE": (1.80, 2.40, 1.90, 2.30), "EA": (1.80, 2.40, 1.90, 2.30),
    "EXTRACTO REAL": (3.30, 3.90, 3.40, 3.80), "ER": (3.30, 3.90, 3.40, 3.80),
    "ALCOHOL EN VOLUMEN": (4.00, 4.60, 4.10, 4.50), "ALCOHOL EN PESO": (3.10, 3.70, 3.20, 3.60),
    "COLOR": (3.00, 6.00, 3.50, 5.50), "AMARGO": (6.00, 10.00, 6.50, 9.50), 
    "PH": (3.95, 4.45, 4.05, 4.35)
}
SPECS_PT_MALTA = {
    "EXTRACTO APARENTE": (12.80, 13.40, 12.90, 13.30), "EA": (12.80, 13.40, 12.90, 13.30),
    "EXTRACTO ORIGINAL": (12.80, 13.40, 12.90, 13.30), "EO": (12.80, 13.40, 12.90, 13.30),
    "AMARGO": (6.50, 9.50, 7.00, 9.00), "PH": (4.15, 4.65, 4.25, 4.55)
}
ESPECIFICACIONES = {
    "COCIMIENTO": {
        "AMSTEL": {"EXTRACTO ORIGINAL": (10.8, 11.8, 10.9, 11.7), "EO": (10.8, 11.8, 10.9, 11.7)},
        "SCHNEIDER": {"EXTRACTO ORIGINAL": (11.3, 12.1, 11.4, 12.0), "EO": (11.3, 12.1, 11.4, 12.0)},
        "MALTA REAL": SPECS_COCIMIENTO_MALTA, "MALTA": SPECS_COCIMIENTO_MALTA,
        "CAPITAL": SPECS_COCIMIENTO_CCR, "CORDILLERA": SPECS_COCIMIENTO_CCR, "REAL": SPECS_COCIMIENTO_CCR
    },
    "FIN_REPOSO": {
        "AMSTEL": {
            "EXTRACTO ORIGINAL": (10.8, 11.8, 10.9, 11.7), "EO": (10.8, 11.8, 10.9, 11.7),
            "EXTRACTO APARENTE": (1.80, 2.40, 1.90, 2.30), "EA": (1.80, 2.40, 1.90, 2.30),
            "ALCOHOL": (4.80, 5.40, 4.90, 5.30), "COLOR": (5.60, 8.60, 6.10, 8.10), 
            "AMARGO": (10.20, 14.20, 10.70, 13.70), "PH": (4.15, 4.65, 4.25, 4.55)
        },
        "SCHNEIDER": {
            "EXTRACTO ORIGINAL": (11.3, 12.1, 11.4, 12.0), "EO": (11.3, 12.1, 11.4, 12.0),
            "EXTRACTO APARENTE": (1.70, 2.30, 1.80, 2.20), "EA": (1.70, 2.30, 1.80, 2.20),
            "ALCOHOL": (4.90, 5.40, 4.95, 5.35), "COLOR": (7.20, 9.20, 7.70, 8.70), 
            "AMARGO": (12.00, 16.00, 13.00, 15.00), "PH": (4.00, 4.70, 4.00, 4.60)
        },
        "MALTA REAL": SPECS_REPOSO_MALTA, "MALTA": SPECS_REPOSO_MALTA,
        "CAPITAL": SPECS_REPOSO_CCR, "CORDILLERA": SPECS_REPOSO_CCR, "REAL": SPECS_REPOSO_CCR
    },
    "FILTRACION_PT": {
        "AMSTEL": {
            "EXTRACTO ORIGINAL": (9.90, 10.50, 10.0, 10.40), "EO": (9.90, 10.50, 10.0, 10.40),
            "EXTRACTO APARENTE": (1.60, 2.20, 1.70, 2.10), "EA": (1.60, 2.20, 1.70, 2.10),
            "EXTRACTO REAL": (3.20, 3.80, 3.30, 3.70), "ER": (3.20, 3.80, 3.30, 3.70),
            "COLOR": (4.00, 7.00, 4.50, 6.50), "AMARGO": (9.00, 13.00, 9.50, 12.50), 
            "PH": (4.15, 4.65, 4.25, 4.55)
        },
        "SCHNEIDER": {
            "EXTRACTO ORIGINAL": (10.70, 11.00, 10.70, 10.90), "EO": (10.70, 11.00, 10.70, 10.90),
            "EXTRACTO APARENTE": (1.52, 2.12, 1.62, 2.02), "EA": (1.52, 2.12, 1.62, 2.02),
            "EXTRACTO REAL": (3.20, 3.90, 3.30, 3.80), "ER": (3.20, 3.90, 3.30, 3.80),
            "COLOR": (6.00, 7.50, 6.00, 7.00), "AMARGO": (11.00, 15.00, 12.00, 14.00), 
            "PH": (4.00, 4.70, 4.00, 4.60)
        },
        "MALTA REAL": SPECS_PT_MALTA, "MALTA": SPECS_PT_MALTA,
        "CAPITAL": SPECS_PT_CCR, "CORDILLERA": SPECS_PT_CCR, "REAL": SPECS_PT_CCR
    }
}

def normalizar_texto(texto):
    texto = str(texto).upper().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def obtener_limites(etapa, producto, parametro):
    if etapa == "Cocimiento": dic_etapa = ESPECIFICACIONES["COCIMIENTO"]
    elif etapa == "Fin de Reposo": dic_etapa = ESPECIFICACIONES["FIN_REPOSO"]
    else: dic_etapa = ESPECIFICACIONES["FILTRACION_PT"]

    p_norm = normalizar_texto(producto)
    pa_norm = normalizar_texto(parametro)
    
    p_key = next((k for k in dic_etapa.keys() if k == p_norm or k in p_norm), None)
    if p_key:
        for k_p, lim in dic_etapa[p_key].items():
            if k_p == pa_norm or k_p in pa_norm:
                return lim[0], lim[1], (lim[2] if len(lim)>2 else None), (lim[3] if len(lim)>3 else None)
    return None, None, None, None

# 3. CARGA DE DATOS
def generar_url_csv(url, gid):
    if not url: return ""
    if "pub?" in url or "output=csv" in url: return url
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match: return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv&gid={gid}"
    return url

@st.cache_data(ttl=15)
def cargar_datos(url):
    try:
        df_raw = pd.read_csv(url)
        header_idx = next((i for i, row in df_raw.iterrows() if any("PRODUCTO" in str(val).upper() or "LOTE" in str(val).upper() for val in row.values)), None)
        if header_idx is not None:
            df = pd.read_csv(url, skiprows=header_idx + 1)
            df.columns = [str(col).strip() for col in df.columns]
            return df, None
        return df_raw, None
    except Exception as e:
        return None, str(e)
