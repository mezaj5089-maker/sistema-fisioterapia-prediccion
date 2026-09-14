import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import joblib
import os
import datetime
from datetime import date, timedelta
import zoneinfo
import plotly.express as px
from supabase import create_client, Client

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA Y LAYOUT PRINCIPAL
# =========================================================
st.set_page_config(
    page_title="Fisioterapia Predictiva 3D | Portal Clínico Completo",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILOS CSS REFORZADOS: ALTO CONTRASTE Y LEGIBILIDAD ABSOLUTA
# =========================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@600;800&display=swap');

    /* Fondo principal y reset de tipografía global */
    html, body, .stApp {
        background: linear-gradient(135deg, #070c18 0%, #111827 50%, #070c18 100%) !important;
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Forzar texto blanco en todos los elementos de texto */
    h1, h2, h3, h4, h5, h6, label, p, span, div, li {
        color: #ffffff !important;
    }

    /* Subtítulos y descripciones de Streamlit */
    .stMarkdown p, .stMarkdown label, .stMarkdown span {
        color: #e2e8f0 !important;
        font-size: 1.02rem;
    }

    /* BARRA LATERAL (SIDEBAR) */
    section[data-testid="stSidebar"] {
        background-color: #0d1527 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.3) !important;
    }

    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* DISEÑO DE PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(15, 23, 42, 0.95);
        padding: 12px;
        border-radius: 16px;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border: 1px solid transparent !important;
        background-color: rgba(30, 41, 59, 0.6) !important;
        transition: all 0.3s ease-in-out !important;
    }

    /* Ecos visuales e interacción hover en pestañas */
    .stTabs [data-baseweb="tab"]:hover {
        color: #38bdf8 !important;
        background-color: rgba(56, 189, 248, 0.25) !important;
        border: 1px solid #38bdf8 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #0284c7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.5) !important;
    }

    /* CONTROLES DE ENTRADA (INPUTS, SELECTBOXES, NUMERIC) */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="select"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] * {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }

    /* CONTENEDORES TIPO TARJETA (GLASSMORPHISM) */
    div[data-testid="stForm"], .glass-card {
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 20px !important;
        padding: 28px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(10px);
    }

    /* BOTONES */
    .stButton>button, div[data-testid="stForm"] button {
        background: linear-gradient(90deg, #0284c7 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: 1px solid #38bdf8 !important;
        padding: 0.7rem 2rem !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton>button:hover, div[data-testid="stForm"] button:hover {
        transform: translateY(-3px) !important;
        background: linear-gradient(90deg, #38bdf8 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.7) !important;
    }

    /* SLIDERS */
    .stSlider label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# INICIALIZACIÓN DE SERVICIOS (SUPABASE Y MODELO ML)
# =========================================================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()

@st.cache_resource
def load_rf_model():
    if os.path.exists("modelo_fisioterapia.pkl"):
        return joblib.load("modelo_fisioterapia.pkl")
    return None

rf_model = load_rf_model()

# Persistencia de Estado de Sesión Local
if "tabla_pacientes_local" not in st.session_state:
    st.session_state.tabla_pacientes_local = pd.DataFrame()

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# =========================================================
# BARRA LATERAL: RELOJ EN VIVO 24H Y CALENDARIO
# =========================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #ffffff;'>🏥 Portal Clínico</h2>", unsafe_allow_html=True)

reloj_digital_js = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Roboto:wght@500;700&display=swap');
        body { margin: 0; padding: 0; background-color: transparent; font-family: 'Roboto', sans-serif; }
        .reloj-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
            border: 1px solid #38bdf8;
            border-radius: 14px;
            padding: 12px 10px;
            text-align: center;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
            color: #ffffff;
        }
        .reloj-header { font-size: 11px; font-weight: 700; color: #38bdf8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
        .reloj-display { display: flex; justify-content: center; align-items: baseline; font-family: 'Orbitron', monospace; background: #050811; padding: 8px 4px; border-radius: 8px; border: 1px solid #38bdf8; }
        .tiempo-principal { font-size: 26px; font-weight: 800; color: #38bdf8; text-shadow: 0 0 8px rgba(56, 189, 248, 0.8); letter-spacing: 1px; }
        .segundos { font-size: 16px; font-weight: 600; color: #c084fc; text-shadow: 0 0 6px rgba(192, 132, 252, 0.8); margin-left: 4px; }
        .fecha-sub { margin-top: 8px; font-size: 13px; font-weight: 700; color: #ffffff; letter-spacing: 0.5px; }
        .dia-semana { color: #ffb703; font-weight: 700; text-transform: capitalize; }
    </style>
</head>
<body>
    <div class="reloj-card">
        <div class="reloj-header">HORA Y FECHA OFICIAL (PERÚ)</div>
        <div class="reloj-display">
            <span id="hora-min" class="tiempo-principal">00:00</span>
            <span id="seg" class="segundos">:00</span>
        </div>
        <div class="fecha-sub">
            <span id="dia-nombre" class="dia-semana">Lunes</span>, 
            <span id="fecha-completa">01 Jan 2026</span>
        </div>
    </div>
    <script>
        function actualizarReloj() {
            const opcionesFecha = { timeZone: 'America/Lima', weekday: 'long', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
            const ahora = new Date();
            const formateador = new Intl.DateTimeFormat('es-PE', opcionesFecha);
            const partes = formateador.formatToParts(ahora);
            let hora = '', minuto = '', segundo = '', diaNombre = '', diaNum = '', mes = '', anio = '';
            partes.forEach(p => {
                if (p.type === 'hour') hora = p.value;
                if (p.type === 'minute') minuto = p.value;
                if (p.type === 'second') segundo = p.value;
                if (p.type === 'weekday') diaNombre = p.value;
                if (p.type === 'day') diaNum = p.value;
                if (p.type === 'month') mes = p.value;
                if (p.type === 'year') anio = p.value;
            });
            diaNombre = diaNombre.charAt(0).toUpperCase() + diaNombre.slice(1);
            mes = mes.charAt(0).toUpperCase() + mes.slice(1);
            document.getElementById('hora-min').textContent = `${hora}:${minuto}`;
            document.getElementById('seg').textContent = `:${segundo}`;
            document.getElementById('dia-nombre').textContent = diaNombre;
            document.getElementById('fecha-completa').textContent = `${diaNum} ${mes} ${anio}`;
        }
        setInterval(actualizarReloj, 1000);
        actualizarReloj();
    </script>
</body>
</html>
"""

with st.sidebar:
    components.html(reloj_digital_js, height=140)

tz_peru = zoneinfo.ZoneInfo("America/Lima")
ahora_peru = datetime.datetime.now(tz_peru)

st.sidebar.markdown("<p style='color:#ffffff; font-weight:bold; margin-bottom:2px;'>📅 Calendario de Consultas</p>", unsafe_allow_html=True)
fecha_seleccionada = st.sidebar.date_input(
    "", 
    value=ahora_peru.date(),
    format="DD/MM/YYYY"
)

st.sidebar.write("---")
st.sidebar.markdown("<p style='color:#ffffff; font-weight:bold;'>Seleccione el Perfil de Usuario:</p>", unsafe_allow_html=True)
perfil = st.sidebar.radio("", ["👤 Vista Paciente / Consulta", "🛡️ Vista Administrador / Fisioterapeuta"])

if perfil == "🛡️ Vista Administrador / Fisioterapeuta":
    if st.session_state.admin_logged_in:
        if st.sidebar.button("🔒 Cerrar Sesión"):
            st.session_state.admin_logged_in = False
            st.rerun()
    else:
        password = st.sidebar.text_input("Contraseña de Acceso Admin:", type="password")
        if password == "admin123":
            st.session_state.admin_logged_in = True
            st.sidebar.success("Acceso Autorizado")
            st.rerun()

# =========================================================
# ENCABEZADO PRINCIPAL DE LA APLICACIÓN
# =========================================================
st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2.8rem; margin-bottom: 0px; color: #ffffff;">🩺 FISIOTERAPIA PREDICTIVA 3D</h1>
        <p style="color: #38bdf8; font-size: 1.25rem; font-weight: 600;">Sistema Inteligente de Evaluación, Diagnóstico, Modelado Anatómico y Predicción Clínica con ML</p>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# VISTA 1: CONSULTA PACIENTE
# =========================================================
if perfil == "👤 Vista Paciente / Consulta":
    st.header("📋 Consulta de Expediente Médico del Paciente")
    st.write("Ingrese su documento de identidad registrado para consultar los resultados de su evaluación y tiempos de recuperación estimados.")
    
    dni_buscar = st.text_input("Ingrese su número de DNI:")
    
    if st.button("🔍 Buscar Expediente"):
        if dni_buscar:
            encontrado = False
            if supabase:
                try:
                    res = supabase.table("pacientes").select("*").eq("dni", dni_buscar).execute()
                    if res.data:
                        paciente = res.data[0]
                        st.success(f"¡Bienvenido(a), **{paciente['nombre']}**!")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Sesiones Estimadas", f"{paciente['num_sesiones']} Sesiones")
                        c2.metric("Fecha Estimada de Alta", str(paciente['fecha_alta']))
                        c3.metric("Probabilidad de Éxito", f"{paciente['probabilidad_recuperacion']}%")
                        encontrado = True
                except Exception:
                    pass
            
            if not encontrado and not st.session_state.tabla_pacientes_local.empty:
                df_loc = st.session_state.tabla_pacientes_local
                res_loc = df_loc[df_loc['dni'] == dni_buscar]
                if not res_loc.empty:
                    paciente = res_loc.iloc[0]
                    st.success(f"¡Bienvenido(a), **{paciente['nombre']}**!")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Sesiones Estimadas", f"{paciente['num_sesiones']} Sesiones")
                    c2.metric("Fecha Estimada de Alta", str(paciente['fecha_alta']))
                    c3.metric("Probabilidad de Éxito", f"{paciente['probabilidad_recuperacion']}%")
                    encontrado = True
                    
            if not encontrado:
                st.warning("No se encontró ningún expediente asociado al DNI ingresado en la base de datos.")
        else:
            st.info("Por favor ingrese un número de DNI válido para realizar la búsqueda.")

# =========================================================
# VISTA 2: ADMINISTRADOR / FISIOTERAPEUTA (SISTEMA COMPLETO)
# =========================================================
else:
    if st.session_state.admin_logged_in:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📥 Capa Bronze: Registro & 3D", 
            "⚙️ Capa Silver: Transformación", 
            "🏆 Capa Gold: Inferencia ML", 
            "📊 Dashboard Interactivo HTML"
        ])
        
        # ---------------------------------------------------------
        # TAB 1: REGISTRO + MAQUETA ANATÓMICA MUSCULAR Y GEOMETRÍA 3D
        # ---------------------------------------------------------
        with tab1:
            st.header("📋 Registro de Pacientes y Evaluación Anatómica (Capa Bronze)")
            st.write("Examine la maqueta humana 3D para la identificación de zonas musculares y complete el formulario clínico a continuación.")

            # CÓDIGO THREE.JS: MAQUETA MUSCULAR COMPLETA Y ELEMENTOS GEOMÉTRICOS
            threejs_anatomical_maquette = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <style>
                    body { margin: 0; background: #050a14; color: white; font-family: 'Segoe UI', Tahoma, sans-serif; overflow: hidden; }
                    #canvas-container { width: 100%; height: 450px; border-radius: 16px; border: 2px solid #38bdf8; position: relative; box-shadow: 0 0 25px rgba(56, 189, 248, 0.35); }
                    #info-panel { 
                        position: absolute; top: 15px; left: 15px; 
                        background: rgba(15, 23, 42, 0.95); 
                        padding: 12px 18px; border-radius: 12px; font-size: 13px; 
                        border: 1px solid #38bdf8; max-width: 340px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
                    }
                    #info-panel h4 { margin: 0 0 6px 0; color: #38bdf8; font-size: 15px; text-transform: uppercase; }
                    #info-panel p { margin: 0; color: #ffffff; font-size: 12px; line-height: 1.4; }
                    #controls-hint {
                        position: absolute; bottom: 12px; right: 12px;
                        background: rgba(15, 23, 42, 0.9);
                        padding: 8px 14px; border-radius: 8px; font-size: 11px; color: #ffb703;
                        border: 1px solid rgba(255, 183, 3, 0.5); font-weight: bold;
                    }
                </style>
            </head>
            <body>
                <div id="canvas-container">
                    <div id="info-panel">
                        <h4 id="muscle-title">🧍 Maqueta Anatómica Muscular & Geometría 3D</h4>
                        <p id="muscle-desc">Pase el cursor sobre los grupos musculares o figuras geométricas biomecánicas para obtener detalles.</p>
                    </div>
                    <div id="controls-hint">🔄 Entorno Biomecánico 3D Interactivo (Rotación Continua)</div>
                </div>

                <script>
                    const container = document.getElementById('canvas-container');
                    const scene = new THREE.Scene();
                    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    container.appendChild(renderer.domElement);

                    // Iluminación
                    const light1 = new THREE.DirectionalLight(0xffffff, 1.2);
                    light1.position.set(5, 10, 7);
                    scene.add(light1);

                    const light2 = new THREE.DirectionalLight(0x38bdf8, 0.9);
                    light2.position.set(-5, -5, -5);
                    scene.add(light2);

                    const ambientLight = new THREE.AmbientLight(0x334155, 1.0);
                    scene.add(ambientLight);

                    const mainGroup = new THREE.Group();
                    const bodyGroup = new THREE.Group();
                    const geoGroup = new THREE.Group();

                    // Materiales
                    const matMusculo = new THREE.MeshPhongMaterial({ color: 0xd946ef, specular: 0xf472b6, shininess: 30 }); 
                    const matTorso = new THREE.MeshPhongMaterial({ color: 0xe11d48, specular: 0xfb7185, shininess: 40 }); 
                    const matArticulacion = new THREE.MeshPhongMaterial({ color: 0x38bdf8, emissive: 0x0284c7 }); 
                    const matPiernas = new THREE.MeshPhongMaterial({ color: 0xc084fc, specular: 0xe879f9, shininess: 25 }); 

                    // --- ANATOMÍA MUSCULAR HUMANA ---
                    // Cabeza y Cuello
                    const headGeo = new THREE.SphereGeometry(0.42, 24, 24);
                    const head = new THREE.Mesh(headGeo, matArticulacion);
                    head.position.y = 2.1;
                    head.userData = { title: "Zona Cervical / Cabeza", desc: "Músculos Trapecio y Esternocleidomastoideo. Evaluado en cervicalgias." };
                    bodyGroup.add(head);

                    const neckGeo = new THREE.CylinderGeometry(0.18, 0.22, 0.3, 16);
                    const neck = new THREE.Mesh(neckGeo, matMusculo);
                    neck.position.y = 1.7;
                    bodyGroup.add(neck);

                    // Tórax y Abdomen
                    const chestGeo = new THREE.BoxGeometry(1.1, 0.8, 0.5);
                    const chest = new THREE.Mesh(chestGeo, matTorso);
                    chest.position.y = 1.25;
                    chest.userData = { title: "Tórax y Pectorales", desc: "Músculos Pectorales Mayor/Menor. Claves en posturales de hombro." };
                    bodyGroup.add(chest);

                    const absGeo = new THREE.BoxGeometry(0.9, 0.7, 0.45);
                    const abs = new THREE.Mesh(absGeo, matMusculo);
                    abs.position.y = 0.55;
                    abs.userData = { title: "Core y Pared Abdominal", desc: "Recto abdominal y Oblicuos. Estabilización de columna vertebral." };
                    bodyGroup.add(abs);

                    // Pelvis
                    const pelvisGeo = new THREE.CylinderGeometry(0.5, 0.42, 0.5, 16);
                    const pelvis = new THREE.Mesh(pelvisGeo, matTorso);
                    pelvis.position.y = 0.0;
                    pelvis.userData = { title: "Región Lumbar y Pelvis", desc: "Zona crítica en Lumbalgia. Músculos Cuadrado Lumbar y Glúteos." };
                    bodyGroup.add(pelvis);

                    // Hombros
                    const shoulderGeo = new THREE.SphereGeometry(0.28, 16, 16);
                    const shoulderR = new THREE.Mesh(shoulderGeo, matArticulacion);
                    shoulderR.position.set(-0.75, 1.45, 0);
                    shoulderR.userData = { title: "Hombro Derecho", desc: "Manguito Rotador y Deltoides." };
                    bodyGroup.add(shoulderR);

                    const shoulderL = new THREE.Mesh(shoulderGeo, matArticulacion);
                    shoulderL.position.set(0.75, 1.45, 0);
                    shoulderL.userData = { title: "Hombro Izquierdo", desc: "Manguito Rotador y Deltoides." };
                    bodyGroup.add(shoulderL);

                    // Extremidades Inferiores
                    const legGeo = new THREE.CylinderGeometry(0.25, 0.19, 1.1, 16);
                    const legR = new THREE.Mesh(legGeo, matPiernas);
                    legR.position.set(-0.32, -0.8, 0);
                    legR.userData = { title: "Cuádriceps Derecho", desc: "Músculo Cuádriceps Femoral y Tendón Rotuliano." };
                    bodyGroup.add(legR);

                    const legL = new THREE.Mesh(legGeo, matPiernas);
                    legL.position.set(0.32, -0.8, 0);
                    legL.userData = { title: "Cuádriceps Izquierdo", desc: "Músculo Cuádriceps Femoral y Tendón Rotuliano." };
                    bodyGroup.add(legL);

                    // Rodillas
                    const kneeGeo = new THREE.SphereGeometry(0.22, 16, 16);
                    const kneeR = new THREE.Mesh(kneeGeo, matArticulacion);
                    kneeR.position.set(-0.32, -1.45, 0.1);
                    kneeR.userData = { title: "Articulación Rodilla Derecha", desc: "Evaluación de Ligamentos y Meniscos." };
                    bodyGroup.add(kneeR);

                    const kneeL = new THREE.Mesh(kneeGeo, matArticulacion);
                    kneeL.position.set(0.32, -1.45, 0.1);
                    kneeL.userData = { title: "Articulación Rodilla Izquierda", desc: "Evaluación de Ligamentos y Meniscos." };
                    bodyGroup.add(kneeL);

                    mainGroup.add(bodyGroup);

                    // --- FIGURAS GEOMÉTRICAS BIOMECÁNICAS ALREDEDOR ---
                    const matGeoWire = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true });
                    const matGeoGold = new THREE.MeshStandardMaterial({ color: 0xfbbf24, metalness: 0.8, roughness: 0.2 });

                    // Toroides (Anillos de Rango Articular)
                    const torus1 = new THREE.Mesh(new THREE.TorusGeometry(1.6, 0.03, 16, 100), matGeoWire);
                    torus1.rotation.x = Math.PI / 2;
                    torus1.position.y = 1.45;
                    geoGroup.add(torus1);

                    // Icosaedro Flotante (Vector de Fuerza)
                    const ico = new THREE.Mesh(new THREE.IcosahedronGeometry(0.35, 0), matGeoGold);
                    ico.position.set(1.8, 1.8, 0);
                    ico.userData = { title: "Eje Geométrico Vectorial", desc: "Representación de vectores de fuerza y ejes dinámicos kinésicos." };
                    geoGroup.add(ico);

                    // Octaedro Biomecánico
                    const oct = new THREE.Mesh(new THREE.OctahedronGeometry(0.35, 0), matGeoWire);
                    oct.position.set(-1.8, 0.5, 0);
                    oct.userData = { title: "Poliedro de Equilibrio Biomecánico", desc: "Centro de gravedad y simetría postular." };
                    geoGroup.add(oct);

                    mainGroup.add(geoGroup);
                    scene.add(mainGroup);

                    camera.position.z = 6.5;

                    // Interacción Raycaster Hover
                    const raycaster = new THREE.Raycaster();
                    const mouse = new THREE.Vector2();

                    function onMouseMove(event) {
                        const rect = renderer.domElement.getBoundingClientRect();
                        mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
                        mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;

                        raycaster.setFromCamera(mouse, camera);
                        const intersects = raycaster.intersectObjects([...bodyGroup.children, ...geoGroup.children]);

                        if (intersects.length > 0) {
                            const hit = intersects[0].object;
                            if (hit.userData && hit.userData.title) {
                                document.getElementById('muscle-title').innerText = hit.userData.title;
                                document.getElementById('muscle-desc').innerText = hit.userData.desc;
                            }
                        }
                    }

                    container.addEventListener('mousemove', onMouseMove, false);

                    // Animación
                    function animate() {
                        requestAnimationFrame(animate);
                        mainGroup.rotation.y += 0.007;
                        ico.rotation.x += 0.02;
                        ico.rotation.y += 0.02;
                        oct.rotation.y += 0.02;
                        renderer.render(scene, camera);
                    }
                    animate();
                </script>
            </body>
            </html>
            """
            components.html(threejs_anatomical_maquette, height=470)

            # FORMULARIO COMPLETO DE REGISTRO CLÍNICO
            with st.form("form_bronze"):
                st.subheader("1. Datos Personales y Clínicos Básicos")
                col1, col2 = st.columns(2)
                with col1:
                    dni = st.text_input("DNI del Paciente:")
                    nombre = st.text_input("Nombre Completo:")
                    edad = st.number_input("Edad:", 1, 100, 30)
                    genero = st.selectbox("Género:", ["Masculino", "Femenino", "Otro"])
                with col2:
                    eva = st.slider("Escala EVA (Dolor Inicial 1-10):", 1, 10, 5)
                    zona = st.selectbox("Zona Afectada:", ["Lumbar", "Cervical", "Hombro", "Rodilla", "Tobillo", "Otro"])
                
                st.write("---")
                st.subheader("2. Evaluación Psicofísica Detallada")
                col_tsk, col_pcs = st.columns(2)
                
                with col_tsk:
                    st.markdown("#### Kinesiofobia (Escala TSK)")
                    tsk1 = st.slider("1. Miedo a lesionarse al moverse:", 1, 10, 5)
                    tsk2 = st.slider("2. Evita actividad física por temor:", 1, 10, 5)
                    tsk3 = st.slider("3. Percepción de vulnerabilidad física:", 1, 10, 5)
                    tsk_total = round((tsk1 + tsk2 + tsk3) * 1.66, 1)

                with col_pcs:
                    st.markdown("#### Catastrofismo (Escala PCS)")
                    pcs1 = st.slider("1. Pensamientos de dolor perpetuo:", 1, 10, 5)
                    pcs2 = st.slider("2. Rumiación constante sobre la lesión:", 1, 10, 5)
                    pcs3 = st.slider("3. Percepción de incapacidad para soportar:", 1, 10, 5)
                    pcs_total = round((pcs1 + pcs2 + pcs3) * 1.66, 1)

                guardar = st.form_submit_button("💾 Registar Expediente Clínico")
                
                if guardar and dni and nombre:
                    if rf_model is not None:
                        try:
                            features = np.array([[eva, tsk_total, pcs_total]])
                            pred_sesiones = int(rf_model.predict(features)[0])
                        except Exception:
                            pred_sesiones = int(eva * 1.5 + 4)
                    else:
                        pred_sesiones = int(eva * 1.5 + 4)

                    prob_exito = round(max(30.0, 100.0 - (eva * 3.5 + tsk_total * 0.4 + pcs_total * 0.4)), 1)
                    fecha_alta_calculada = ahora_peru.date() + timedelta(days=pred_sesiones * 2)

                    nuevo_reg = {
                        "dni": dni, "nombre": nombre, "edad": edad, "genero": genero,
                        "eva_inicial": eva, "zona_afectada": zona, 
                        "tsk_score": tsk_total, "pcs_score": pcs_total,
                        "num_sesiones": pred_sesiones, "fecha_alta": fecha_alta_calculada.isoformat(),
                        "probabilidad_recuperacion": prob_exito
                    }

                    st.session_state.tabla_pacientes_local = pd.concat(
                        [st.session_state.tabla_pacientes_local, pd.DataFrame([nuevo_reg])], 
                        ignore_index=True
                    )

                    if supabase:
                        try:
                            supabase.table("pacientes").insert(nuevo_reg).execute()
                            st.success(f"✅ ¡Expediente de {nombre} guardado en Supabase!")
                        except Exception as e:
                            st.warning(f"✅ Registrado en sesión local. (Detalle Supabase: {e})")
                    else:
                        st.success(f"✅ ¡Expediente de {nombre} registrado localmente con éxito!")

        # ---------------------------------------------------------
        # TAB 2: CAPA SILVER
        # ---------------------------------------------------------
        with tab2:
            st.header("⚙️ Capa Silver: Transformación y Limpieza de Datos")
            st.write("Vista estructurada de los datos capturados en bruto procesados para modelamiento y análisis clínico.")
            
            if not st.session_state.tabla_pacientes_local.empty:
                st.dataframe(st.session_state.tabla_pacientes_local, use_container_width=True)
            else:
                st.info("No hay registros cargados en la sesión actual. Ingrese un paciente en la Capa Bronze.")

        # ---------------------------------------------------------
        # TAB 3: CAPA GOLD (MODELO ML)
        # ---------------------------------------------------------
        with tab3:
            st.header("🏆 Capa Gold: Inferencia del Modelo Random Forest")
            st.write("Predicciones optimizadas del algoritmo de Inteligencia Artificial para el plan de tratamiento.")

            if not st.session_state.tabla_pacientes_local.empty:
                ultimo = st.session_state.tabla_pacientes_local.iloc[-1]
                st.subheader(f"Expediente Evaluado: {ultimo['nombre']} (DNI: {ultimo['dni']})")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Total de Sesiones Estimadas", f"{ultimo['num_sesiones']} Sesiones")
                    st.metric("Fecha Estimada de Alta Médica", str(ultimo['fecha_alta']))
                with c2:
                    st.metric("Probabilidad del Éxito Terapéutico", f"{ultimo['probabilidad_recuperacion']}%")
                    st.progress(float(ultimo['probabilidad_recuperacion']) / 100.0)
            else:
                st.info("Registre un paciente en la Capa Bronze para habilitar la inferencia con Machine Learning.")

        # ---------------------------------------------------------
        # TAB 4: DASHBOARD HTML CON FILTROS SOLICITADOS
        # ---------------------------------------------------------
        with tab4:
            st.header("📊 Dashboard de Control y Tiempo de Recuperación")
            
            dashboard_html_code = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    :root {
                        --bg-main: #0b1120;
                        --card-bg: rgba(30, 41, 59, 0.95);
                        --primary: #38bdf8;
                        --text-dark: #ffffff;
                        --border: rgba(56, 189, 248, 0.4);
                    }
                    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
                    body { background-color: var(--bg-main); color: var(--text-dark); padding: 10px; }
                    
                    /* CONTROLES / BOTONES SOLICITADOS */
                    .filter-bar {
                        display: flex; flex-wrap: wrap; gap: 20px; align-items: center;
                        background: var(--card-bg); padding: 18px; border-radius: 14px;
                        border: 1px solid var(--border); margin-bottom: 20px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
                    }
                    .filter-group { display: flex; flex-direction: column; gap: 6px; }
                    .filter-group label { font-size: 13px; font-weight: 700; color: #38bdf8; text-transform: uppercase; }
                    .filter-group select {
                        background: #0f172a; color: #ffffff; border: 1px solid #38bdf8;
                        padding: 9px 14px; border-radius: 8px; font-weight: 600; font-size: 14px; outline: none;
                        cursor: pointer;
                    }

                    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
                    .metric-card {
                        background: var(--card-bg); padding: 20px; border-radius: 14px;
                        border: 1px solid var(--border); text-align: left;
                    }
                    .metric-title { font-size: 13px; color: #cbd5e1; font-weight: 600; margin-bottom: 6px; }
                    .metric-value { font-size: 28px; font-weight: 800; color: #ffffff; }

                    .chart-container {
                        background: var(--card-bg); padding: 20px; border-radius: 14px;
                        border: 1px solid var(--border); height: 320px;
                    }
                </style>
            </head>
            <body>
                <p style="color: #cbd5e1; font-size: 13px; margin-bottom: 12px;">Panel demostrativo con registros históricos 2023–2026. Las estimaciones no sustituyen el criterio médico directo.</p>
                
                <!-- BARRA CON NUEVOS FILTROS DE INTERACCIÓN -->
                <div class="filter-bar">
                    <div class="filter-group">
                        <label for="tipo-lesion">Tipo de Lesión:</label>
                        <select id="tipo-lesion" onchange="updateDashboard()">
                            <option value="Todos">Todas las Lesiones</option>
                            <option value="Postquirurgica" selected>Postquirúrgica</option>
                            <option value="Muscular">Muscular</option>
                            <option value="Articular">Articular</option>
                            <option value="Tendinosa">Tendinosa</option>
                            <option value="Neurologica">Neurológica</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label for="cronicidad">Cronicidad:</label>
                        <select id="cronicidad" onchange="updateDashboard()">
                            <option value="Todos">Todas</option>
                            <option value="Agudo">Agudo</option>
                            <option value="Subagudo">Subagudo</option>
                            <option value="Cronico" selected>Crónico</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label for="genero-filter">Género:</label>
                        <select id="genero-filter" onchange="updateDashboard()">
                            <option value="Todos">Todos</option>
                            <option value="Masculino" selected>Masculino</option>
                            <option value="Femenino">Femenino</option>
                            <option value="Otro">Otro</option>
                        </select>
                    </div>
                </div>

                <!-- METRICAS RESUMEN -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-title">Pacientes Registrados</div>
                        <div class="metric-value" id="val-pacientes">27</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Tasa de Recuperación</div>
                        <div class="metric-value" id="val-recuperacion">40.7%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Sesiones Medianas Positivas</div>
                        <div class="metric-value" id="val-sesiones">19</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Tiempo Estimado</div>
                        <div class="metric-value" id="val-tiempo">9.5 semanas</div>
                    </div>
                </div>

                <!-- GRÁFICO DINÁMICO CHART.JS -->
                <div class="chart-container">
                    <canvas id="mainChart"></canvas>
                </div>

                <script>
                    const ctx = document.getElementById('mainChart').getContext('2d');
                    let chart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Postquirúrgica', 'Muscular', 'Articular', 'Tendinosa', 'Neurológica'],
                            datasets: [{
                                label: 'Pacientes por Categoría de Lesión',
                                data: [27, 18, 12, 15, 8],
                                backgroundColor: '#2563eb',
                                borderRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { labels: { color: '#ffffff' } }
                            },
                            scales: {
                                x: { ticks: { color: '#ffffff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                                y: { ticks: { color: '#ffffff' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                            }
                        }
                    });

                    function updateDashboard() {
                        const lesion = document.getElementById('tipo-lesion').value;
                        const cronicidad = document.getElementById('cronicidad').value;
                        const genero = document.getElementById('genero-filter').value;

                        let baseVal = 27;
                        if(cronicidad === 'Agudo') baseVal = 14;
                        if(genero === 'Femenino') baseVal = 21;
                        if(lesion === 'Muscular') baseVal = 18;

                        document.getElementById('val-pacientes').innerText = baseVal;
                        document.getElementById('val-recuperacion').innerText = (35 + (baseVal % 10)*1.5).toFixed(1) + "%";
                        chart.data.datasets[0].data = [baseVal, baseVal - 4, baseVal - 8, baseVal - 3, baseVal - 10];
                        chart.update();
                    }
                </script>
            </body>
            </html>
            """
            components.html(dashboard_html_code, height=540)