import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import base64
import datetime
from datetime import date, timedelta
import plotly.express as px
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y COLORES
# ---------------------------------------------------------
st.set_page_config(
    page_title="Fisioterapia Predictiva",
    page_icon="🏥",
    layout="wide"
)

# Carga de la imagen de fondo local en base64 si existe 'fisio.png'
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_base64 = get_base64_image("fisio.png")

bg_style = ""
if img_base64:
    bg_style = f"""
    .stApp {{
        background: linear-gradient(rgba(244, 247, 246, 0.85), rgba(244, 247, 246, 0.90)), 
                    url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    """

custom_css = f"""
{bg_style}
<style>
/* Títulos y fuentes principales */
h1, h2, h3 {{
    color: #1A365D !important;
    font-family: 'Segoe UI', Roboto, sans-serif;
    font-weight: 700;
}}

/* Estilo de la hora en vivo verde esmeralda */
.reloj-box {{
    background-color: #007A60;
    color: white;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0, 122, 96, 0.25);
    margin-bottom: 15px;
}}

.reloj-box h2 {{
    color: white !important;
    margin: 4px 0 0 0;
    font-size: 26px;
    letter-spacing: 1px;
}}

.reloj-box small {{
    color: #D1FAE5;
    font-weight: 600;
}}

/* Tarjetas traslúcidas con bordes suaves */
div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {{
    background: rgba(255, 255, 255, 0.88);
    border-radius: 12px;
    padding: 18px;
    border: 1px solid #E2E8F0;
}}

/* Botones llamativos */
.stButton>button {{
    background-color: #2B6CB0;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1.2rem;
    transition: all 0.3s ease;
}}
.stButton>button:hover {{
    background-color: #2C5282;
    box-shadow: 0 4px 12px rgba(43, 108, 176, 0.3);
}}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXIÓN A SUPABASE & MODELO ML
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
def load_ml_model():
    if os.path.exists("modelo_fisioterapia.pkl"):
        return joblib.load("modelo_fisioterapia.pkl")
    return None

model = load_ml_model()

if "tabla_pacientes_local" not in st.session_state:
    st.session_state.tabla_pacientes_local = pd.DataFrame()

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ---------------------------------------------------------
# BARRA LATERAL (RELOJ + LOGIN/LOGOUT)
# ---------------------------------------------------------
st.sidebar.title("🏥 Portal Clínico")

# Reloj Digital Activo (Verde Esmeralda)
ahora = datetime.datetime.now()
st.sidebar.markdown(
    f"""
    <div class="reloj-box">
        <small>HORA Y FECHA OFICIAL</small>
        <h2>{ahora.strftime('%H:%M:%S')}</h2>
        <small>{ahora.strftime('%a, %d %b %Y')}</small>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.write("---")
st.sidebar.write("Seleccione el Perfil de Usuario:")
perfil = st.sidebar.radio("", ["👤 Vista Paciente / Consulta", "🛡️ Vista Administrador / Fisioterapeuta"])

# Lógica de cierre de sesión
if perfil == "🛡️ Vista Administrador / Fisioterapeuta":
    if st.session_state.admin_logged_in:
        if st.sidebar.button("🔒 Cerrar Sesión Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()
    else:
        password = st.sidebar.text_input("Contraseña de Acceso Admin:", type="password")
        if password == "admin123":
            st.session_state.admin_logged_in = True
            st.sidebar.success("Acceso Autorizado")
            st.rerun()

# ---------------------------------------------------------
# ENCABEZADO DE LA PÁGINA
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
        
        # TAB 1: REGISTRO COMPLETO DE DOLENCIAS (IMAGEN 2)
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
                    tsk_total = round((tsk1 + tsk2 + tsk3) * 1.66, 1) # Normalización a escala TSK (10-50)

                with col_pcs:
                    st.markdown("#### Catastrofismo (PCS)")
                    pcs1 = st.slider("1. Dolor perpetuo:", 1, 10, 5)
                    pcs2 = st.slider("2. Rumiación constante:", 1, 10, 5)
                    pcs3 = st.slider("3. Incapacidad de soporte:", 1, 10, 5)
                    pcs_total = round((pcs1 + pcs2 + pcs3) * 1.66, 1) # Normalización a escala PCS (0-50)

                guardar = st.form_submit_button("💾 Guardar Paciente")
                
                if guardar and dni and nombre:
                    # Inferencia ML
                    if model is not None:
                        try:
                            features = np.array([[eva, tsk_total, pcs_total]])
                            pred_sesiones = int(model.predict(features)[0])
                        except Exception:
                            pred_sesiones = int(eva * 1.5 + 4)
                    else:
                        pred_sesiones = int(eva * 1.5 + 4)

                    prob_exito = round(max(30.0, 100.0 - (eva * 3.5 + tsk_total * 0.4 + pcs_total * 0.4)), 1)
                    fecha_alta = date.today() + timedelta(days=pred_sesiones * 2)

                    nuevo_reg = {
                        "dni": dni, "nombre": nombre, "edad": edad, "genero": genero,
                        "eva_inicial": eva, "zona_afectada": zona, 
                        "tsk_score": tsk_total, "pcs_score": pcs_total,
                        "num_sesiones": pred_sesiones, "fecha_alta": fecha_alta.isoformat(),
                        "probabilidad_recuperacion": prob_exito
                    }

                    # Sesión Local
                    st.session_state.tabla_pacientes_local = pd.concat(
                        [st.session_state.tabla_pacientes_local, pd.DataFrame([nuevo_reg])], 
                        ignore_index=True
                    )

                    # Persistencia Supabase
                    if supabase:
                        try:
                            supabase.table("pacientes").insert(nuevo_reg).execute()
                            st.success(f"✅ ¡Paciente {nombre} guardado exitosamente en Supabase y localmente!")
                        except Exception as e:
                            st.warning(f"✅ Paciente guardado en sesión local. Nota Supabase: {e}")
                    else:
                        st.success(f"✅ Paciente {nombre} guardado localmente.")

        # TAB 2: CAPA SILVER
        with tab2:
            st.header("⚙️ Capa Silver: Transformación")
            st.write("Limpieza y estructuración de variables para los algoritmos de Machine Learning.")
            if not st.session_state.tabla_pacientes_local.empty:
                st.dataframe(st.session_state.tabla_pacientes_local, use_container_width=True)
            else:
                st.info("No hay registros en la sesión actual.")

        # TAB 3: CAPA GOLD (INFERENCIA ML)
        with tab3:
            st.header("🏆 Capa Gold: Inferencia ML")
            if not st.session_state.tabla_pacientes_local.empty:
                ultimo = st.session_state.tabla_pacientes_local.iloc[-1]
                st.subheader(f"Expediente Evaluado: {ultimo['nombre']} (DNI: {ultimo['dni']})")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Sesiones Estimadas", f"{ultimo['num_sesiones']} Sesiones")
                    st.metric("Fecha Estimada de Alta", str(ultimo['fecha_alta']))
                with c2:
                    st.metric("Probabilidad de Éxito", f"{ultimo['probabilidad_recuperacion']}%")
                    st.progress(float(ultimo['probabilidad_recuperacion']) / 100.0)
            else:
                st.info("Registra un paciente en la Capa Bronze para generar su inferencia.")

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
                st.info("No hay registros guardados en la base de datos.")

    else:
        st.warning("🔒 Ingrese la contraseña de administrador en la barra lateral para acceder al sistema.")