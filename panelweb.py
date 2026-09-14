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

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Fisioterapia Predictiva 3D | Portal Clínico",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILOS CSS REVISADOS: TEXTOS BLANCOS, HOVER Y ALTO CONTRASTE
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Orbitron:wght@600;800&display=swap');

    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #171e38 50%, #0b1120 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Encabezados y Subtítulos en Blanco Puro con Brillo */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }

    p, span, label, div {
        color: #ffffff !important;
    }

    /* Subtítulos específicos de Streamlit */
    .stMarkdown p, .stMarkdown label, .stMarkdown span {
        color: #e2e8f0 !important;
        font-size: 1.05rem;
    }

    /* Pestañas (Tabs): Texto blanco visible + Efecto HOVER interactivo */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(15, 23, 42, 0.8);
        padding: 10px;
        border-radius: 16px;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        color: #ffffff !important; /* Blanco puro por defecto */
        font-weight: 700 !important;
        padding: 10px 20px !important;
        border: 1px solid transparent !important;
        transition: all 0.3s ease !important;
    }

    /* Hover en pestañas */
    .stTabs [data-baseweb="tab"]:hover {
        color: #38bdf8 !important;
        background-color: rgba(56, 189, 248, 0.2) !important;
        border: 1px solid #38bdf8 !important;
        transform: translateY(-2px);
    }

    /* Pestaña Seleccionada */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #0284c7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important;
    }

    /* Textos en la Sidebar (Barra Lateral) */
    section[data-testid="stSidebar"] {
        background-color: #0d1527 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Radio Buttons en Sidebar con Hover */
    div[data-testid="stRadio"] label:hover {
        color: #38bdf8 !important;
        cursor: pointer;
    }

    /* Tarjetas Glassmorphism */
    div[data-testid="stForm"], .glass-card {
        background: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
    }

    /* Botones */
    .stButton>button, div[data-testid="stForm"] button {
        background: linear-gradient(90deg, #0284c7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: 1px solid #38bdf8 !important;
        padding: 0.6rem 1.8rem !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover, div[data-testid="stForm"] button:hover {
        transform: translateY(-2px) !important;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%) !important;
        color: #000000 !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.8) !important;
    }

    /* Inputs de texto y números */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }

    /* Slider styling */
    .stSlider label {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXIÓN A SUPABASE Y MODELO RANDOM FOREST ML
# ---------------------------------------------------------
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

if "tabla_pacientes_local" not in st.session_state:
    st.session_state.tabla_pacientes_local = pd.DataFrame()

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ---------------------------------------------------------
# BARRA LATERAL: RELOJ DIGITAL EN VIVO + CALENDARIO
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# TÍTULO PRINCIPAL EN BLANCO
# ---------------------------------------------------------
st.markdown("""
    <div style="text-align: center; padding: 15px 0;">
        <h1 style="font-size: 2.8rem; margin-bottom: 0px; color: #ffffff;">🩺 FISIOTERAPIA PREDICTIVA 3D</h1>
        <p style="color: #38bdf8; font-size: 1.2rem; font-weight: 600;">Sistema Inteligente de Evaluación, Diagnóstico, Modelado Anatómico y Predicción Clínica con ML</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# VISTA 1: PACIENTE / CONSULTA
# ---------------------------------------------------------
if perfil == "👤 Vista Paciente / Consulta":
    st.header("📋 Consulta de Expediente Médico")
    dni_buscar = st.text_input("Ingrese su número de DNI para consultar su estado:")
    
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
                st.warning("No se encontró ningún expediente asociado al DNI ingresado.")
        else:
            st.info("Por favor ingrese un número de DNI válido.")

# ---------------------------------------------------------
# VISTA 2: ADMINISTRADOR / FISIOTERAPEUTA
# ---------------------------------------------------------
else:
    if st.session_state.admin_logged_in:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📥 Capa Bronze: Registro & 3D", 
            "⚙️ Capa Silver: Transformación", 
            "🏆 Capa Gold: Inferencia ML", 
            "📊 Dashboard Interactivo HTML"
        ])
        
        # TAB 1: REGISTRO + MAQUETA ANATÓMICA MUSCULAR 3D INTERACTIVA
        with tab1:
            st.header("📋 Registro de Pacientes y Evaluación Anatómica (Capa Bronze)")
            
            # MAQUETA ANATÓMICA REALISTA DE MÚSCULOS EN 3D
            threejs_anatomical_maquette = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <style>
                    body { margin: 0; background: #050a14; color: white; font-family: 'Segoe UI', Tahoma, sans-serif; overflow: hidden; }
                    #canvas-container { width: 100%; height: 380px; border-radius: 16px; border: 2px solid #38bdf8; position: relative; box-shadow: 0 0 20px rgba(56, 189, 248, 0.3); }
                    #info-panel { 
                        position: absolute; top: 12px; left: 12px; 
                        background: rgba(15, 23, 42, 0.9); 
                        padding: 10px 16px; border-radius: 10px; font-size: 13px; 
                        border: 1px solid #38bdf8; max-width: 320px;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
                    }
                    #info-panel h4 { margin: 0 0 4px 0; color: #38bdf8; font-size: 14px; text-transform: uppercase; }
                    #info-panel p { margin: 0; color: #f8fafc; font-size: 12px; }
                    #controls-hint {
                        position: absolute; bottom: 12px; right: 12px;
                        background: rgba(15, 23, 42, 0.8);
                        padding: 6px 12px; border-radius: 8px; font-size: 11px; color: #ffb703;
                        border: 1px solid rgba(255, 183, 3, 0.4);
                    }
                </style>
            </head>
            <body>
                <div id="canvas-container">
                    <div id="info-panel">
                        <h4 id="muscle-title">🧍 Maqueta Anatómica Muscular 3D</h4>
                        <p id="muscle-desc">Pase el cursor sobre la figura para conocer los grupos musculares y zonas de fisioterapia.</p>
                    </div>
                    <div id="controls-hint">🔄 Rotación Automática Continua 360°</div>
                </div>

                <script>
                    const container = document.getElementById('canvas-container');
                    const scene = new THREE.Scene();
                    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    container.appendChild(renderer.domElement);

                    // Luces de alta definición para resaltar volumen de músculos
                    const light1 = new THREE.DirectionalLight(0xffffff, 1.2);
                    light1.position.set(5, 10, 7);
                    scene.add(light1);

                    const light2 = new THREE.DirectionalLight(0x38bdf8, 0.8);
                    light2.position.set(-5, -5, -5);
                    scene.add(light2);

                    const ambientLight = new THREE.AmbientLight(0x334155, 0.9);
                    scene.add(ambientLight);

                    const bodyGroup = new THREE.Group();

                    // Materiales Anatómicos Médicos
                    const matMusculo = new THREE.MeshPhongMaterial({ color: 0xd946ef, specular: 0xf472b6, shininess: 30 }); // Músculo muscular magenta
                    const matTorso = new THREE.MeshPhongMaterial({ color: 0xe11d48, specular: 0xfb7185, shininess: 40 }); // Pecho y Abdomen
                    const matArticulacion = new THREE.MeshPhongMaterial({ color: 0x38bdf8, emissive: 0x0284c7 }); // Puntos Articulares
                    const matPiernas = new THREE.MeshPhongMaterial({ color: 0xc084fc, specular: 0xe879f9, shininess: 25 }); // Cuádriceps

                    // 1. Cabeza y Cuello (Cervical)
                    const headGeo = new THREE.SphereGeometry(0.42, 24, 24);
                    const head = new THREE.Mesh(headGeo, matArticulacion);
                    head.position.y = 2.1;
                    head.userData = { title: "Zona Cervical / Cabeza", desc: "Músculos Trapecio y Esternocleidomastoideo. Evaluado en cervicalgias y estrés." };
                    bodyGroup.add(head);

                    const neckGeo = new THREE.CylinderGeometry(0.18, 0.22, 0.3, 16);
                    const neck = new THREE.Mesh(neckGeo, matMusculo);
                    neck.position.y = 1.7;
                    bodyGroup.add(neck);

                    // 2. Torso (Pectorales y Abdominales)
                    const chestGeo = new THREE.BoxGeometry(1.1, 0.8, 0.5);
                    const chest = new THREE.Mesh(chestGeo, matTorso);
                    chest.position.y = 1.25;
                    chest.userData = { title: "Tórax y Pectorales", desc: "Músculos Pectorales Mayor/Menor. Claves para postura de hombros." };
                    bodyGroup.add(chest);

                    const absGeo = new THREE.BoxGeometry(0.9, 0.7, 0.45);
                    const abs = new THREE.Mesh(absGeo, matMusculo);
                    abs.position.y = 0.55;
                    abs.userData = { title: "Core y Pared Abdominal", desc: "Recto abdominal y Oblicuos. Estabilizadores del tronco y columna." };
                    bodyGroup.add(abs);

                    // 3. Zona Lumbar y Pelvis
                    const pelvisGeo = new THREE.CylinderGeometry(0.5, 0.42, 0.5, 16);
                    const pelvis = new THREE.Mesh(pelvisGeo, matTorso);
                    pelvis.position.y = 0.0;
                    pelvis.userData = { title: "Región Lumbar y Glúteos", desc: "Zona crítica para Lumbalgia. Músculos Cuadrado Lumbar y Glúteo Mayor." };
                    bodyGroup.add(pelvis);

                    // 4. Hombros (Deltoides)
                    const shoulderGeo = new THREE.SphereGeometry(0.28, 16, 16);
                    const shoulderR = new THREE.Mesh(shoulderGeo, matArticulacion);
                    shoulderR.position.set(-0.75, 1.45, 0);
                    shoulderR.userData = { title: "Hombro Derecho (Deltoides)", desc: "Manguito Rotador y Deltoides. Frecuente en tendinopatías." };
                    bodyGroup.add(shoulderR);

                    const shoulderL = new THREE.Mesh(shoulderGeo, matArticulacion);
                    shoulderL.position.set(0.75, 1.45, 0);
                    shoulderL.userData = { title: "Hombro Izquierdo (Deltoides)", desc: "Manguito Rotador y Deltoides. Frecuente en tendinopatías." };
                    bodyGroup.add(shoulderL);

                    // 5. Brazos (Bíceps / Tríceps)
                    const armGeo = new THREE.CylinderGeometry(0.18, 0.15, 0.9, 16);
                    const armR = new THREE.Mesh(armGeo, matMusculo);
                    armR.position.set(-0.82, 0.85, 0);
                    bodyGroup.add(armR);

                    const armL = new THREE.Mesh(armGeo, matMusculo);
                    armL.position.set(0.82, 0.85, 0);
                    bodyGroup.add(armL);

                    // 6. Piernas y Rodillas (Cuádriceps)
                    const legGeo = new THREE.CylinderGeometry(0.25, 0.19, 1.1, 16);
                    const legR = new THREE.Mesh(legGeo, matPiernas);
                    legR.position.set(-0.32, -0.8, 0);
                    legR.userData = { title: "Muslo y Cuádriceps (Derecho)", desc: "Músculo Cuádriceps Femoral. Potencia en extensión de rodilla." };
                    bodyGroup.add(legR);

                    const legL = new THREE.Mesh(legGeo, matPiernas);
                    legL.position.set(0.32, -0.8, 0);
                    legL.userData = { title: "Muslo y Cuádriceps (Izquierdo)", desc: "Músculo Cuádriceps Femoral. Potencia en extensión de rodilla." };
                    bodyGroup.add(legL);

                    // Rodillas
                    const kneeGeo = new THREE.SphereGeometry(0.22, 16, 16);
                    const kneeR = new THREE.Mesh(kneeGeo, matArticulacion);
                    kneeR.position.set(-0.32, -1.45, 0.1);
                    kneeR.userData = { title: "Articulación de Rodilla", desc: "Evaluación de Ligamentos Cruzados y Meniscos en Esguinces." };
                    bodyGroup.add(kneeR);

                    const kneeL = new THREE.Mesh(kneeGeo, matArticulacion);
                    kneeL.position.set(0.32, -1.45, 0.1);
                    kneeL.userData = { title: "Articulación de Rodilla", desc: "Evaluación de Ligamentos Cruzados y Meniscos en Esguinces." };
                    bodyGroup.add(kneeL);

                    // Gemelos / Pantorrillas
                    const calfGeo = new THREE.CylinderGeometry(0.18, 0.12, 1.0, 16);
                    const calfR = new THREE.Mesh(calfGeo, matMusculo);
                    calfR.position.set(-0.32, -2.05, 0);
                    bodyGroup.add(calfR);

                    const calfL = new THREE.Mesh(calfGeo, matMusculo);
                    calfL.position.set(0.32, -2.05, 0);
                    bodyGroup.add(calfL);

                    bodyGroup.position.y = 0.2;
                    scene.add(bodyGroup);
                    camera.position.z = 6.2;

                    // Interacción Raycaster para Detectar Hover sobre Músculos
                    const raycaster = new THREE.Raycaster();
                    const mouse = new THREE.Vector2();

                    function onMouseMove(event) {
                        const rect = renderer.domElement.getBoundingClientRect();
                        mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
                        mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;

                        raycaster.setFromCamera(mouse, camera);
                        const intersects = raycaster.intersectObjects(bodyGroup.children);

                        if (intersects.length > 0) {
                            const hit = intersects[0].object;
                            if (hit.userData && hit.userData.title) {
                                document.getElementById('muscle-title').innerText = hit.userData.title;
                                document.getElementById('muscle-desc').innerText = hit.userData.desc;
                            }
                        }
                    }

                    container.addEventListener('mousemove', onMouseMove, false);

                    // Animación de Rotación Anatómica
                    function animate() {
                        requestAnimationFrame(animate);
                        bodyGroup.rotation.y += 0.008;
                        renderer.render(scene, camera);
                    }
                    animate();
                </script>
            </body>
            </html>
            """
            components.html(threejs_anatomical_maquette, height=400)

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
                    st.markdown("#### Kinesiofobia (TSK)")
                    tsk1 = st.slider("1. Miedo a lesionarse al moverse:", 1, 10, 5)
                    tsk2 = st.slider("2. Evita actividad física:", 1, 10, 5)
                    tsk3 = st.slider("3. Percepción de daño:", 1, 10, 5)
                    tsk_total = round((tsk1 + tsk2 + tsk3) * 1.66, 1)

                with col_pcs:
                    st.markdown("#### Catastrofismo (PCS)")
                    pcs1 = st.slider("1. Dolor perpetuo:", 1, 10, 5)
                    pcs2 = st.slider("2. Rumiación constante:", 1, 10, 5)
                    pcs3 = st.slider("3. Incapacidad de soporte:", 1, 10, 5)
                    pcs_total = round((pcs1 + pcs2 + pcs3) * 1.66, 1)

                guardar = st.form_submit_button("💾 Guardar Paciente")
                
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
                            st.success(f"✅ ¡Paciente {nombre} guardado exitosamente!")
                        except Exception as e:
                            st.warning(f"✅ Paciente guardado localmente. (Nota Supabase: {e})")
                    else:
                        st.success(f"✅ Paciente {nombre} guardado localmente.")

        # TAB 2: CAPA SILVER
        with tab2:
            st.header("⚙️ Capa Silver: Transformación")
            if not st.session_state.tabla_pacientes_local.empty:
                st.dataframe(st.session_state.tabla_pacientes_local, use_container_width=True)
            else:
                st.info("No hay registros cargados en la sesión.")

        # TAB 3: CAPA GOLD (INFERENCIA RANDOM FOREST)
        with tab3:
            st.header("🏆 Capa Gold: Inferencia ML (Random Forest)")
            if not st.session_state.tabla_pacientes_local.empty:
                ultimo = st.session_state.tabla_pacientes_local.iloc[-1]
                st.subheader(f"Expediente Evaluado: {ultimo['nombre']} (DNI: {ultimo['dni']})")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Total de Sesiones Estimadas", f"{ultimo['num_sesiones']} Sesiones")
                    st.metric("Fecha Estimada de Alta Médica", str(ultimo['fecha_alta']))
                with c2:
                    st.metric("Probabilidad de Éxito del Tratamiento", f"{ultimo['probabilidad_recuperacion']}%")
                    st.progress(float(ultimo['probabilidad_recuperacion']) / 100.0)
            else:
                st.info("Registra un paciente en la Capa Bronze para generar su estimación con Random Forest.")

        # TAB 4: DASHBOARD HTML EN ALTA DEFINICIÓN
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
                        --bg-main: #0f172a;
                        --card-bg: rgba(30, 41, 59, 0.85);
                        --primary: #38bdf8;
                        --primary-dark: #0284c7;
                        --success: #10b981;
                        --warning: #f59e0b;
                        --danger: #ef4444;
                        --text-dark: #ffffff;
                        --text-light: #cbd5e1;
                        --border: rgba(56, 189, 248, 0.3);
                    }
                    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
                    body { background-color: var(--bg-main); color: var(--text-dark); padding: 10px; }
                    header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: var(--card-bg); padding: 15px 25px; border-radius: 14px; border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
                    header h1 { font-size: 22px; color: #ffffff; }
                    header p { font-size: 13px; color: var(--primary); font-weight: 600; }
                    .filters-panel { background: var(--card-bg); padding: 15px; border-radius: 14px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; border: 1px solid var(--border); }
                    .filter-group { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 160px; }
                    .filter-group label { font-size: 11px; font-weight: 700; color: #ffffff; text-transform: uppercase; }
                    .filter-group select, .filter-group input { padding: 8px 12px; background: #090d16; color: #ffffff; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; outline: none; }
                    .btn-reset { padding: 8px 16px; background: var(--primary); color: #0f172a; border: none; border-radius: 8px; cursor: pointer; font-weight: 700; align-self: flex-end; transition: background 0.2s; }
                    .btn-reset:hover { background: #ffffff; color: #0f172a; }
                    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
                    .kpi-card { background: var(--card-bg); padding: 16px; border-radius: 14px; border: 1px solid var(--border); border-left: 5px solid var(--primary); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
                    .kpi-title { font-size: 12px; color: var(--text-light); margin-bottom: 6px; font-weight: 700; }
                    .kpi-value { font-size: 24px; font-weight: 800; color: #ffffff; }
                    .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 15px; margin-bottom: 20px; }
                    .chart-card { background: var(--card-bg); padding: 16px; border-radius: 14px; border: 1px solid var(--border); }
                    .chart-card h3 { font-size: 15px; margin-bottom: 12px; color: #ffffff; }
                    .table-container { background: var(--card-bg); padding: 16px; border-radius: 14px; border: 1px solid var(--border); overflow-x: auto; }
                    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
                    th { background-color: rgba(15, 23, 42, 0.9); color: #ffffff; padding: 10px; font-weight: 700; border-bottom: 2px solid var(--border); }
                    td { padding: 10px; border-bottom: 1px solid var(--border); color: #ffffff; }
                    tr:hover { background-color: rgba(56, 189, 248, 0.15); }
                    .badge { padding: 4px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; }
                    .badge-recuperado { background: rgba(16, 185, 129, 0.25); color: #34d399; border: 1px solid #10b981; }
                    .badge-tratamiento { background: rgba(56, 189, 248, 0.25); color: #38bdf8; border: 1px solid #38bdf8; }
                    .badge-alta { background: rgba(129, 140, 248, 0.25); color: #818cf8; border: 1px solid #818cf8; }
                    .badge-riesgo { background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid #ef4444; }
                    .progress-bar { width: 80px; height: 7px; background: #1e293b; border-radius: 4px; overflow: hidden; display: inline-block; vertical-align: middle; margin-right: 5px; }
                    .progress-fill { height: 100%; background: var(--primary); }
                </style>
            </head>
            <body>
                <header>
                    <div>
                        <h1>Plataforma Clínica de Fisioterapia</h1>
                        <p>Monitoreo de Sesiones, Tiempos de Recuperación y Registro 2023 - 2026</p>
                    </div>
                    <div style="text-align: right;">
                        <strong style="color: #ffffff;">Sistema Activo</strong><br>
                        <span style="font-size: 12px; color: var(--primary);">Capa Gold - Modelo Medallion</span>
                    </div>
                </header>

                <div class="filters-panel">
                    <div class="filter-group">
                        <label for="searchPatient">Buscar Paciente / ID</label>
                        <input type="text" id="searchPatient" placeholder="Ej. Carlos o PAC-101" oninput="applyFilters()">
                    </div>
                    <div class="filter-group">
                        <label for="filterDiag">Diagnóstico</label>
                        <select id="filterDiag" onchange="applyFilters()">
                            <option value="ALL">Todos los diagnósticos</option>
                            <option value="Lumbalgia">Lumbalgia</option>
                            <option value="Cervicalgia">Cervicalgia</option>
                            <option value="Tendinopatía">Tendinopatía</option>
                            <option value="Esguince Rodilla">Esguince Rodilla</option>
                            <option value="Post-Quirúrgico">Post-Quirúrgico</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="filterStatus">Estado del Paciente</label>
                        <select id="filterStatus" onchange="applyFilters()">
                            <option value="ALL">Todos los estados</option>
                            <option value="En Tratamiento">En Tratamiento</option>
                            <option value="Recuperado">Recuperado</option>
                            <option value="Alta Médica">Alta Médica</option>
                            <option value="En Riesgo">En Riesgo</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="filterTime">Tiempo Recuperación</label>
                        <select id="filterTime" onchange="applyFilters()">
                            <option value="ALL">Cualquier tiempo</option>
                            <option value="SHORT">Rápido (&lt; 5 sem)</option>
                            <option value="MEDIUM">Moderado (5 - 8 sem)</option>
                            <option value="LONG">Extendido (&gt; 8 sem)</option>
                        </select>
                    </div>
                    <button class="btn-reset" onclick="resetFilters()">Limpiar Filtros</button>
                </div>

                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-title">TOTAL PACIENTES CONSULTADOS</div>
                        <div class="kpi-value" id="kpiTotal">0</div>
                    </div>
                    <div class="kpi-card" style="border-left-color: var(--success);">
                        <div class="kpi-title">RECUPERACIÓN PROMEDIO</div>
                        <div class="kpi-value" id="kpiAvgTime">0 sem</div>
                    </div>
                    <div class="kpi-card" style="border-left-color: var(--warning);">
                        <div class="kpi-title">ADHERENCIA PROMEDIO</div>
                        <div class="kpi-value" id="kpiAdherence">0%</div>
                    </div>
                    <div class="kpi-card" style="border-left-color: var(--danger);">
                        <div class="kpi-title">REDUCCIÓN DOLOR (EVA)</div>
                        <div class="kpi-value" id="kpiPainDiff">0 pts</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-card">
                        <h3>Tiempo Estimado de Recuperación por Diagnóstico (Semanas)</h3>
                        <canvas id="chartRecovery"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Distribución de Pacientes por Estado de Tratamiento</h3>
                        <canvas id="chartStatus"></canvas>
                    </div>
                </div>

                <div class="table-container">
                    <h3 style="margin-bottom: 12px; color: #ffffff;">Registro Detallado de Pacientes y Tiempos Clínicos</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Paciente</th>
                                <th>Fecha / Hora Registro</th>
                                <th>Diagnóstico</th>
                                <th>Sesiones (Prog/Real)</th>
                                <th>Dolor (Ini → Fin)</th>
                                <th>Tiempo Est.</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody id="patientTableBody"></tbody>
                    </table>
                </div>

                <script>
                    const rawData = [
                        { id: "PAC-101", name: "Carlos Mendoza", date: "2023-04-12", time: "08:30:00", diag: "Lumbalgia", prog: 12, done: 12, painIni: 8, painFin: 2, weeks: 6, status: "Recuperado" },
                        { id: "PAC-102", name: "Ana Gutiérrez", date: "2023-06-19", time: "10:15:00", diag: "Cervicalgia", prog: 8, done: 8, painIni: 6, painFin: 1, weeks: 4, status: "Alta Médica" },
                        { id: "PAC-103", name: "Roberto Gómez", date: "2024-01-10", time: "15:45:00", diag: "Post-Quirúrgico", prog: 20, done: 14, painIni: 9, painFin: 4, weeks: 12, status: "En Tratamiento" },
                        { id: "PAC-104", name: "Lucía Fernández", date: "2024-03-05", time: "09:00:00", diag: "Tendinopatía", prog: 10, done: 4, painIni: 7, painFin: 6, weeks: 8, status: "En Riesgo" },
                        { id: "PAC-105", name: "Miguel Ángel Torres", date: "2024-08-22", time: "11:30:00", diag: "Esguince Rodilla", prog: 14, done: 14, painIni: 8, painFin: 2, weeks: 7, status: "Recuperado" },
                        { id: "PAC-106", name: "Elena Ramos", date: "2025-02-14", time: "08:00:00", diag: "Lumbalgia", prog: 10, done: 10, painIni: 7, painFin: 1, weeks: 5, status: "Alta Médica" },
                        { id: "PAC-107", name: "Javier López", date: "2025-05-30", time: "16:20:00", diag: "Post-Quirúrgico", prog: 24, done: 18, painIni: 9, painFin: 3, weeks: 14, status: "En Tratamiento" },
                        { id: "PAC-108", name: "Sofia Castro", date: "2025-09-11", time: "07:45:00", diag: "Cervicalgia", prog: 6, done: 6, painIni: 5, painFin: 0, weeks: 3, status: "Recuperado" },
                        { id: "PAC-109", name: "Diego Morales", date: "2026-01-18", time: "14:10:00", diag: "Tendinopatía", prog: 12, done: 8, painIni: 8, painFin: 5, weeks: 9, status: "En Tratamiento" },
                        { id: "PAC-110", name: "Valeria Benítez", date: "2026-02-27", time: "10:00:00", diag: "Esguince Rodilla", prog: 12, done: 3, painIni: 7, painFin: 7, weeks: 10, status: "En Riesgo" }
                    ];

                    let chartRecoveryInstance = null;
                    let chartStatusInstance = null;

                    function renderTable(data) {
                        const tbody = document.getElementById('patientTableBody');
                        tbody.innerHTML = '';

                        if (data.length === 0) {
                            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 20px;">No se encontraron registros con los filtros seleccionados.</td></tr>';
                            return;
                        }

                        data.forEach(item => {
                            const pct = Math.round((item.done / item.prog) * 100);
                            let badgeClass = 'badge-tratamiento';
                            if (item.status === 'Recuperado') badgeClass = 'badge-recuperado';
                            if (item.status === 'Alta Médica') badgeClass = 'badge-alta';
                            if (item.status === 'En Riesgo') badgeClass = 'badge-riesgo';

                            const row = `
                                <tr>
                                    <td><strong>${item.id}</strong></td>
                                    <td>${item.name}</td>
                                    <td>${item.date} <br><small style="color:var(--text-light);">${item.time}</small></td>
                                    <td>${item.diag}</td>
                                    <td>
                                        <div class="progress-bar"><div class="progress-fill" style="width: ${pct}%;"></div></div>
                                        ${item.done}/${item.prog} (${pct}%)
                                    </td>
                                    <td><span style="color:#f87171;">${item.painIni}</span> → <span style="color:#34d399;">${item.painFin}</span></td>
                                    <td><strong>${item.weeks} sem</strong></td>
                                    <td><span class="badge ${badgeClass}">${item.status}</span></td>
                                </tr>
                            `;
                            tbody.innerHTML += row;
                        });
                    }

                    function updateKPIs(data) {
                        document.getElementById('kpiTotal').innerText = data.length;

                        if (data.length === 0) {
                            document.getElementById('kpiAvgTime').innerText = "0 sem";
                            document.getElementById('kpiAdherence').innerText = "0%";
                            document.getElementById('kpiPainDiff').innerText = "0 pts";
                            return;
                        }

                        const avgWeeks = (data.reduce((acc, curr) => acc + curr.weeks, 0) / data.length).toFixed(1);
                        const avgAdherence = Math.round(data.reduce((acc, curr) => acc + (curr.done / curr.prog), 0) / data.length * 100);
                        const avgPainDiff = (data.reduce((acc, curr) => acc + (curr.painIni - curr.painFin), 0) / data.length).toFixed(1);

                        document.getElementById('kpiAvgTime').innerText = `${avgWeeks} sem`;
                        document.getElementById('kpiAdherence').innerText = `${avgAdherence}%`;
                        document.getElementById('kpiPainDiff').innerText = `${avgPainDiff} pts`;
                    }

                    function updateCharts(data) {
                        const diagMap = {};
                        const diagCounts = {};

                        data.forEach(item => {
                            diagMap[item.diag] = (diagMap[item.diag] || 0) + item.weeks;
                            diagCounts[item.diag] = (diagCounts[item.diag] || 0) + 1;
                        });

                        const diagLabels = Object.keys(diagMap);
                        const diagAverages = diagLabels.map(label => (diagMap[label] / diagCounts[label]).toFixed(1));

                        if (chartRecoveryInstance) chartRecoveryInstance.destroy();

                        const ctx1 = document.getElementById('chartRecovery').getContext('2d');
                        chartRecoveryInstance = new Chart(ctx1, {
                            type: 'bar',
                            data: {
                                labels: diagLabels,
                                datasets: [{
                                    label: 'Semanas Promedio',
                                    data: diagAverages,
                                    backgroundColor: ['#38bdf8', '#10b981', '#f59e0b', '#818cf8', '#ec4899']
                                }]
                            },
                            options: {
                                responsive: true,
                                plugins: { legend: { display: false } },
                                scales: { 
                                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.15)' }, ticks: { color: '#ffffff' } },
                                    x: { grid: { color: 'rgba(255,255,255,0.15)' }, ticks: { color: '#ffffff' } }
                                }
                            }
                        });

                        const statusMap = { 'Recuperado': 0, 'En Tratamiento': 0, 'Alta Médica': 0, 'En Riesgo': 0 };
                        data.forEach(item => {
                            if (statusMap[item.status] !== undefined) statusMap[item.status]++;
                        });

                        if (chartStatusInstance) chartStatusInstance.destroy();

                        const ctx2 = document.getElementById('chartStatus').getContext('2d');
                        chartStatusInstance = new Chart(ctx2, {
                            type: 'doughnut',
                            data: {
                                labels: Object.keys(statusMap),
                                datasets: [{
                                    data: Object.values(statusMap),
                                    backgroundColor: ['#10b981', '#38bdf8', '#818cf8', '#ef4444']
                                }]
                            },
                            options: {
                                responsive: true,
                                plugins: { legend: { position: 'bottom', labels: { color: '#ffffff', font: { weight: 'bold' } } } }
                            }
                        });
                    }

                    function applyFilters() {
                        const searchValue = document.getElementById('searchPatient').value.toLowerCase();
                        const diagValue = document.getElementById('filterDiag').value;
                        const statusValue = document.getElementById('filterStatus').value;
                        const timeValue = document.getElementById('filterTime').value;

                        const filtered = rawData.filter(item => {
                            const matchesSearch = item.name.toLowerCase().includes(searchValue) || item.id.toLowerCase().includes(searchValue);
                            const matchesDiag = (diagValue === 'ALL') || (item.diag === diagValue);
                            const matchesStatus = (statusValue === 'ALL') || (item.status === statusValue);
                            
                            let matchesTime = true;
                            if (timeValue === 'SHORT') matchesTime = item.weeks < 5;
                            if (timeValue === 'MEDIUM') matchesTime = item.weeks >= 5 && item.weeks <= 8;
                            if (timeValue === 'LONG') matchesTime = item.weeks > 8;

                            return matchesSearch && matchesDiag && matchesStatus && matchesTime;
                        });

                        renderTable(filtered);
                        updateKPIs(filtered);
                        updateCharts(filtered);
                    }

                    function resetFilters() {
                        document.getElementById('searchPatient').value = '';
                        document.getElementById('filterDiag').value = 'ALL';
                        document.getElementById('filterStatus').value = 'ALL';
                        document.getElementById('filterTime').value = 'ALL';
                        applyFilters();
                    }

                    window.onload = () => {
                        applyFilters();
                    };
                </script>
            </body>
            </html>
            """
            components.html(dashboard_html_code, height=950, scrolling=True)

    else:
        st.warning("🔒 Ingrese la contraseña de administrador en la barra lateral para acceder.")