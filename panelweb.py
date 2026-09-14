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
    page_title="Fisioterapia Predictiva",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------------------------------------
# ESTILOS CSS (DISEÑO MANTENIDO INTACTO)
# ---------------------------------------------------------
URL_FONDO = "https://raw.githubusercontent.com/mezaj5089-maker/sistema-fisioterapia-prediccion/main/fisio.png"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(240, 244, 248, 0.85), rgba(240, 244, 248, 0.90)), 
                    url("{URL_FONDO}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}

    h1, h2, h3 {{
        color: #0F4C81 !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 700;
    }}

    .stButton>button {{
        background-color: #0F4C81;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #1B6AAA;
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

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
# BARRA LATERAL: RELOJ EN VIVO (JS/HTML) + CALENDARIO
# ---------------------------------------------------------
st.sidebar.title("🏥 Portal Clínico")

# Componente HTML / JavaScript para Reloj Digital en Tiempo Real
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
            background: #0d1117;
            border: 2px solid #00f2fe;
            border-radius: 14px;
            padding: 12px 10px;
            text-align: center;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.25);
            color: #ffffff;
        }

        .reloj-header {
            font-size: 10px;
            font-weight: 700;
            color: #00f2fe;
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
            color: #00ff87;
            text-shadow: 0 0 8px rgba(0, 255, 135, 0.6);
            letter-spacing: 1px;
        }

        .segundos {
            font-size: 16px;
            font-weight: 600;
            color: #ff007f;
            text-shadow: 0 0 6px rgba(255, 0, 127, 0.6);
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
            // Configurar zona horaria de Perú (America/Lima)
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

            // Capitalizar la primera letra del día y mes
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

# Renderizar Reloj Digital Interactivo en la Barra Lateral
with st.sidebar:
    components.html(reloj_digital_js, height=140)

# Cálculo de la fecha base para el calendario
tz_peru = zoneinfo.ZoneInfo("America/Lima")
ahora_peru = datetime.datetime.now(tz_peru)

# Calendario automático interactivo
st.sidebar.subheader("📅 Calendario de Consultas")
fecha_seleccionada = st.sidebar.date_input(
    "Seleccione fecha:", 
    value=ahora_peru.date(),
    format="DD/MM/YYYY"
)

st.sidebar.write("---")
st.sidebar.write("Seleccione el Perfil de Usuario:")
perfil = st.sidebar.radio("", ["👤 Vista Paciente / Consulta", "🛡️ Vista Administrador / Fisioterapeuta"])

# Cierre e inicio de sesión
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
st.title("🩺 FISIOTERAPIA PREDICTIVA")
st.caption("Sistema Inteligente de Evaluación, Diagnóstico y Predicción Clínica con ML")

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
            "📥 Capa Bronze: Registro", 
            "⚙️ Capa Silver: Transformación", 
            "🏆 Capa Gold: Inferencia ML", 
            "📁 Base de Datos / Dashboard"
        ])
        
        # TAB 1: REGISTRO CON EVALUACIÓN PSICOFÍSICA
        with tab1:
            st.header("📋 Registro de Pacientes (Capa Bronze)")
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
                    # Inferencia con Modelo Random Forest
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
                            st.success(f"✅ ¡Paciente {nombre} guardado exitosamente en Supabase y localmente!")
                        except Exception as e:
                            st.warning(f"✅ Paciente guardado localmente. Nota Supabase: {e}")
                    else:
                        st.success(f"✅ Paciente {nombre} guardado localmente.")

        # TAB 2: CAPA SILVER
        with tab2:
            st.header("⚙️ Capa Silver: Transformación")
            st.write("Estructuración y limpieza de variables clínicas.")
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

        # TAB 4: BASE DE DATOS Y DASHBOARD
        with tab4:
            st.header("📁 Base de Datos / Dashboard")
            df_final = pd.DataFrame()
            if supabase:
                try:
                    res = supabase.table("pacientes").select("*").execute()
                    df_final = pd.DataFrame(res.data)
                except Exception:
                    df_final = st.session_state.tabla_pacientes_local
            else:
                df_final = st.session_state.tabla_pacientes_local

            if not df_final.empty:
                st.dataframe(df_final, use_container_width=True)
                st.write("---")
                st.subheader("📊 Métricas y Analítica")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig1 = px.histogram(df_final, x="zona_afectada", title="Pacientes por Zona Afectada", color="zona_afectada")
                    st.plotly_chart(fig1, use_container_width=True)
                with col_g2:
                    fig2 = px.scatter(df_final, x="eva_inicial", y="num_sesiones", color="genero", title="Escala EVA vs Sesiones Estimadas")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No hay registros en la base de datos.")

    else:
        st.warning("🔒 Ingrese la contraseña de administrador en la barra lateral para acceder.")