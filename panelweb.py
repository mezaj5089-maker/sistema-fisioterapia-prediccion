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
# ESTILOS CSS++ AVANZADOS (GLASSMORPHISM & CYBER-CLINICAL)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Orbitron:wght@600;800&display=swap');

    /* Fondo general con gradiente dinámico futurista */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
        color: #f8fafc;
    }

    /* Ocultar barra superior por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Encabezados con degradado */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }

    /* Tarjetas y Formularios con Estilo Glassmorphism */
    div[data-testid="stForm"], .glass-card {
        background: rgba(30, 41, 59, 0.65) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.125) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }

    /* Botones Neón e Interactivos */
    .stButton>button, div[data-testid="stForm"] button {
        background: linear-gradient(90deg, #0284c7 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 1.8rem !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stButton>button:hover, div[data-testid="stForm"] button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
        background: linear-gradient(90deg, #0369a1 0%, #4f46e5 100%) !important;
    }

    /* Entradas de Texto, Números y Desplegables */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.5) !important;
    }

    /* Sliders Personalizados */
    .stSlider > div > div > div > div {
        background-color: #38bdf8 !important;
    }

    /* Valores de Métricas */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    /* Pestañas Personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(15, 23, 42, 0.5);
        padding: 8px;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.2), rgba(129, 140, 248, 0.2)) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
    }

    /* Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
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
# BARRA LATERAL: RELOJ DIGITAL EN VIVO (JS/HTML) + CALENDARIO
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center;'>🏥 Portal Clínico</h2>", unsafe_allow_html=True)

reloj_digital_js = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Roboto:wght@500;700&display=swap');

        body {
            margin: 0;
            padding: 0;
            background-color: transparent;
            font-family: 'Roboto', sans-serif;
        }

        .reloj-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9));
            border: 1px solid #38bdf8;
            border-radius: 14px;
            padding: 12px 10px;
            text-align: center;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
            color: #ffffff;
        }

        .reloj-header {
            font-size: 10px;
            font-weight: 700;
            color: #38bdf8;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .reloj-display {
            display: flex;
            justify-content: center;
            align-items: baseline;
            font-family: 'Orbitron', monospace;
            background: #050811;
            padding: 8px 4px;
            border-radius: 8px;
            border: 1px solid #1f293d;
        }

        .tiempo-principal {
            font-size: 26px;
            font-weight: 800;
            color: #38bdf8;
            text-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
            letter-spacing: 1px;
        }

        .segundos {
            font-size: 16px;
            font-weight: 600;
            color: #c084fc;
            text-shadow: 0 0 6px rgba(192, 132, 252, 0.6);
            margin-left: 4px;
        }

        .fecha-sub {
            margin-top: 8px;
            font-size: 12px;
            font-weight: 600;
            color: #e2e8f0;
            letter-spacing: 0.5px;
        }

        .dia-semana {
            color: #ffb703;
            font-weight: 700;
            text-transform: capitalize;
        }
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
            const opcionesFecha = { 
                timeZone: 'America/Lima',
                weekday: 'long',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            };

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

st.sidebar.subheader("📅 Calendario de Consultas")
fecha_seleccionada = st.sidebar.date_input(
    "Seleccione fecha:", 
    value=ahora_peru.date(),
    format="DD/MM/YYYY"
)

st.sidebar.write("---")
st.sidebar.write("Seleccione el Perfil de Usuario:")
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
# TÍTULO PRINCIPAL
# ---------------------------------------------------------
st.markdown("""
    <div style="text-align: center; padding: 15px 0;">
        <h1 style="font-size: 2.8rem; margin-bottom: 0px;">🩺 FISIOTERAPIA PREDICTIVA 3D</h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">Sistema Inteligente de Evaluación, Diagnóstico, Modelado Anatómico y Predicción Clínica con ML</p>
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
        
        # TAB 1: REGISTRO + MODELADO ANATÓMICO THREE.JS
        with tab1:
            st.header("📋 Registro de Pacientes y Evaluación Anatómica (Capa Bronze)")
            
            # VISOR ANATÓMICO INTERACTIVO EN 3D (THREE.JS)
            threejs_viewer_code = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <style>
                    body { margin: 0; background: #090d16; color: white; font-family: sans-serif; overflow: hidden; }
                    #canvas-container { width: 100%; height: 280px; border-radius: 14px; border: 1px solid rgba(56, 189, 248, 0.4); position: relative; }
                    #info-box { position: absolute; top: 10px; left: 10px; background: rgba(15,23,42,0.85); padding: 6px 12px; border-radius: 8px; font-size: 11px; border: 1px solid #38bdf8; }
                </style>
            </head>
            <body>
                <div id="canvas-container">
                    <div id="info-box">🧍 Modelo Anatómico 3D Interactivo - Evaluación Física</div>
                </div>
                <script>
                    const container = document.getElementById('canvas-container');
                    const scene = new THREE.Scene();
                    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    container.appendChild(renderer.domElement);

                    const light1 = new THREE.DirectionalLight(0x38bdf8, 1);
                    light1.position.set(5, 5, 5).normalize();
                    scene.add(light1);
                    const light2 = new THREE.AmbientLight(0x818cf8, 0.6);
                    scene.add(light2);

                    const bodyGroup = new THREE.Group();
                    const matBody = new THREE.MeshPhongMaterial({ color: 0x1e293b, wireframe: true });
                    const matJoint = new THREE.MeshPhongMaterial({ color: 0x38bdf8, emissive: 0x0284c7 });

                    // Torso
                    const torsoGeo = new THREE.CylinderGeometry(0.8, 0.6, 2.2, 16);
                    const torso = new THREE.Mesh(torsoGeo, matBody);
                    bodyGroup.add(torso);

                    // Cabeza
                    const headGeo = new THREE.SphereGeometry(0.5, 16, 16);
                    const head = new THREE.Mesh(headGeo, matJoint);
                    head.position.y = 1.6;
                    bodyGroup.add(head);

                    // Marcador Lumbar Neón
                    const lumbarGeo = new THREE.SphereGeometry(0.35, 16, 16);
                    const lumbarMat = new THREE.MeshPhongMaterial({ color: 0xf43f5e, emissive: 0xe11d48 });
                    const lumbar = new THREE.Mesh(lumbarGeo, lumbarMat);
                    lumbar.position.set(0, -0.4, 0.5);
                    bodyGroup.add(lumbar);

                    // Marcador Rodillas Neón
                    const kneeGeo = new THREE.SphereGeometry(0.25, 16, 16);
                    const kneeMat = new THREE.MeshPhongMaterial({ color: 0x10b981, emissive: 0x059669 });
                    const kneeR = new THREE.Mesh(kneeGeo, kneeMat);
                    kneeR.position.set(-0.4, -1.8, 0.2);
                    bodyGroup.add(kneeR);
                    const kneeL = new THREE.Mesh(kneeGeo, kneeMat);
                    kneeL.position.set(0.4, -1.8, 0.2);
                    bodyGroup.add(kneeL);

                    scene.add(bodyGroup);
                    camera.position.z = 6;

                    function animate() {
                        requestAnimationFrame(animate);
                        bodyGroup.rotation.y += 0.01;
                        renderer.render(scene, camera);
                    }
                    animate();
                </script>
            </body>
            </html>
            """
            components.html(threejs_viewer_code, height=290)

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

        # TAB 4: INTEGRACIÓN COMPLETA DEL DASHBOARD HTML / CHART.JS
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
                        --card-bg: rgba(30, 41, 59, 0.75);
                        --primary: #38bdf8;
                        --primary-dark: #0284c7;
                        --success: #10b981;
                        --warning: #f59e0b;
                        --danger: #ef4444;
                        --text-dark: #f8fafc;
                        --text-light: #94a3b8;
                        --border: rgba(255, 255, 255, 0.1);
                    }
                    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
                    body { background-color: var(--bg-main); color: var(--text-dark); padding: 10px; }
                    header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: var(--card-bg); padding: 15px 25px; border-radius: 14px; border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
                    header h1 { font-size: 22px; color: var(--primary); }
                    header p { font-size: 13px; color: var(--text-light); }
                    .filters-panel { background: var(--card-bg); padding: 15px; border-radius: 14px; margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; border: 1px solid var(--border); }
                    .filter-group { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 160px; }
                    .filter-group label { font-size: 11px; font-weight: 600; color: var(--text-light); text-transform: uppercase; }
                    .filter-group select, .filter-group input { padding: 8px 12px; background: #090d16; color: #ffffff; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; outline: none; }
                    .btn-reset { padding: 8px 16px; background: var(--primary); color: #0f172a; border: none; border-radius: 8px; cursor: pointer; font-weight: 700; align-self: flex-end; transition: background 0.2s; }
                    .btn-reset:hover { background: var(--primary-dark); color: white; }
                    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
                    .kpi-card { background: var(--card-bg); padding: 16px; border-radius: 14px; border: 1px solid var(--border); border-left: 5px solid var(--primary); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
                    .kpi-title { font-size: 12px; color: var(--text-light); margin-bottom: 6px; font-weight: 600; }
                    .kpi-value { font-size: 24px; font-weight: 700; color: var(--text-dark); }
                    .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 15px; margin-bottom: 20px; }
                    .chart-card { background: var(--card-bg); padding: 16px; border-radius: 14px; border: 1px solid var(--border); }
                    .chart-card h3 { font-size: 15px; margin-bottom: 12px; color: var(--text-dark); }
                    .table-container { background: var(--card-bg); padding: 16px; border-radius: 14px; border: 1px solid var(--border); overflow-x: auto; }
                    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
                    th { background-color: rgba(15, 23, 42, 0.8); color: var(--text-light); padding: 10px; font-weight: 600; border-bottom: 2px solid var(--border); }
                    td { padding: 10px; border-bottom: 1px solid var(--border); }
                    tr:hover { background-color: rgba(56, 189, 248, 0.05); }
                    .badge { padding: 4px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block; }
                    .badge-recuperado { background: rgba(16, 185, 129, 0.2); color: #34d399; }
                    .badge-tratamiento { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
                    .badge-alta { background: rgba(129, 140, 248, 0.2); color: #818cf8; }
                    .badge-riesgo { background: rgba(239, 68, 68, 0.2); color: #f87171; }
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
                        <strong>Sistema Activo</strong><br>
                        <span style="font-size: 12px; color: var(--text-light);">Capa Gold - Modelo Medallion</span>
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
                    <h3 style="margin-bottom: 12px;">Registro Detallado de Pacientes y Tiempos Clínicos</h3>
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
                                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#94a3b8' } },
                                    x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#94a3b8' } }
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
                                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
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
            
            # Renderizado directo dentro de Streamlit
            components.html(dashboard_html_code, height=950, scrolling=True)

    else:
        st.warning("🔒 Ingrese la contraseña de administrador en la barra lateral para acceder.")