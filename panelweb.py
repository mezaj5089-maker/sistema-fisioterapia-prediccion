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
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Fisioterapia y Inferencia ML",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------------------------------------
# CARGA DE IMAGEN DE FONDO EN BASE64 (LOCAL / GITHUB)
# ---------------------------------------------------------
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_base64 = get_base64_image("fisio.png")

bg_style = ""
if img_base64:
    bg_style = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(240, 248, 255, 0.82), rgba(240, 248, 255, 0.90)), 
                    url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """

custom_css = f"""
{bg_style}
<style>
/* Estilos modernos y llamativos sin alterar la estructura */
h1, h2, h3 {{
    color: #0E4B75 !important;
    font-family: 'Segoe UI', Roboto, sans-serif;
}}
div[data-testid="stSidebar"] {{
    background-color: rgba(255, 255, 255, 0.95);
}}
.stButton>button {{
    background-color: #0E4B75;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
}}
.stButton>button:hover {{
    background-color: #0077B6;
    color: white;
}}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXIÓN A SUPABASE
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

# ---------------------------------------------------------
# CARGAR MODELO ENTRENADO (.PKL)
# ---------------------------------------------------------
@st.cache_resource
def load_ml_model():
    if os.path.exists("modelo_fisioterapia.pkl"):
        return joblib.load("modelo_fisioterapia.pkl")
    return None

model = load_ml_model()

if "tabla_pacientes_local" not in st.session_state:
    st.session_state.tabla_pacientes_local = pd.DataFrame()

# ---------------------------------------------------------
# BARRA LATERAL (RELOJ Y PERFILES)
# ---------------------------------------------------------
st.sidebar.title("🏥 Portal Clínico")

ahora = datetime.datetime.now()
st.sidebar.markdown(
    f"""
    <div style="background-color: #0E4B75; color: white; padding: 12px; border-radius: 10px; text-align: center;">
        <small style="text-transform: uppercase;">Hora y Fecha Oficial</small>
        <h2 style="color: white !important; margin: 5px 0 0 0;">{ahora.strftime('%H:%M:%S')}</h2>
        <small>{ahora.strftime('%a, %d %b %Y')}</small>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.write("---")
st.sidebar.write("Seleccione el Perfil de Usuario:")
perfil = st.sidebar.radio("", ["👤 Vista Paciente / Consulta", "🛡️ Vista Administrador / Fisioterapeuta"])

# ---------------------------------------------------------
# VISTA 1: PACIENTE / CONSULTA
# ---------------------------------------------------------
if perfil == "👤 Vista Paciente / Consulta":
    st.title("📋 Consulta de Expediente Médico")
    dni_buscar = st.text_input("Ingrese su número de DNI para consultar su estado:")
    
    if st.button("Buscar Expediente"):
        if dni_buscar:
            encontrado = False
            if supabase:
                try:
                    res = supabase.table("pacientes").select("*").eq("dni", dni_buscar).execute()
                    if res.data:
                        paciente = res.data[0]
                        st.success(f"Bienvenido(a), {paciente['nombre']}")
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
                    st.success(f"Bienvenido(a), {paciente['nombre']}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Sesiones Estimadas", f"{paciente['num_sesiones']} Sesiones")
                    c2.metric("Fecha Estimada de Alta", str(paciente['fecha_alta']))
                    c3.metric("Probabilidad de Éxito", f"{paciente['probabilidad_recuperacion']}%")
                    encontrado = True
                    
            if not encontrado:
                st.warning("No se encontró ningún expediente asociado al DNI ingresado.")
        else:
            st.info("Por favor ingrese un DNI válido.")

# ---------------------------------------------------------
# VISTA 2: ADMINISTRADOR / FISIOTERAPEUTA (PROTEGIDO)
# ---------------------------------------------------------
else:
    password = st.sidebar.text_input("Contraseña de Acceso Admin:", type="password")
    if password == "admin123":
        tab1, tab2, tab3, tab4 = st.tabs([
            "📥 Capa Bronze: Registro", 
            "⚙️ Capa Silver: Transformación", 
            "🏆 Capa Gold: Inferencia ML", 
            "📁 Base de Datos / Dashboard"
        ])
        
        # TAB 1: REGISTRO BRONZE
        with tab1:
            st.header("📋 Registro de Pacientes (Capa Bronze)")
            with st.form("form_bronze"):
                col1, col2 = st.columns(2)
                with col1:
                    dni = st.text_input("DNI del Paciente:")
                    nombre = st.text_input("Nombre Completo:")
                    edad = st.number_input("Edad:", 1, 100, 30)
                    genero = st.selectbox("Género:", ["Masculino", "Femenino", "Otro"])
                with col2:
                    eva = st.slider("Escala EVA (Dolor 1-10):", 1, 10, 5)
                    zona = st.selectbox("Zona Afectada:", ["Lumbar", "Cervical", "Hombro", "Rodilla", "Tobillo", "Otro"])
                    tsk = st.number_input("Escala TSK (Kinesiofobia 10-50):", 10.0, 50.0, 25.0)
                    pcs = st.number_input("Escala PCS (Catastrofización 0-50):", 0.0, 50.0, 15.0)
                
                guardar = st.form_submit_button("💾 Guardar Paciente")
                
                if guardar and dni and nombre:
                    # Predicción usando modelo local si existe
                    if model is not None:
                        try:
                            features = np.array([[eva, tsk, pcs]])
                            pred_sesiones = int(model.predict(features)[0])
                        except Exception:
                            pred_sesiones = int(eva * 1.5 + 5)
                    else:
                        pred_sesiones = int(eva * 1.5 + 5)

                    prob_exito = round(max(30.0, 100.0 - (eva * 4 + tsk * 0.5)), 1)
                    fecha_alta = date.today() + timedelta(days=pred_sesiones * 2)

                    nuevo_reg = {
                        "dni": dni, "nombre": nombre, "edad": edad, "genero": genero,
                        "eva_inicial": eva, "zona_afectada": zona, "tsk_score": tsk, "pcs_score": pcs,
                        "num_sesiones": pred_sesiones, "fecha_alta": fecha_alta.isoformat(),
                        "probabilidad_recuperacion": prob_exito
                    }

                    # Actualizar sesión local
                    st.session_state.tabla_pacientes_local = pd.concat(
                        [st.session_state.tabla_pacientes_local, pd.DataFrame([nuevo_reg])], 
                        ignore_index=True
                    )

                    # Guardar Supabase
                    if supabase:
                        try:
                            supabase.table("pacientes").insert(nuevo_reg).execute()
                            st.success(f"¡Paciente {nombre} guardado correctamente en Supabase!")
                        except Exception as e:
                            st.warning(f"Guardado local. Nota Supabase: {e}")
                    else:
                        st.success(f"¡Paciente {nombre} guardado localmente!")

        # TAB 2: CAPA SILVER
        with tab2:
            st.header("⚙️ Capa Silver: Procesamiento e Pre-procesado")
            st.write("Limpieza y normalización de variables para preparación del modelo ML.")
            if not st.session_state.tabla_pacientes_local.empty:
                st.dataframe(st.session_state.tabla_pacientes_local, use_container_width=True)
            else:
                st.info("No hay registros cargados en la sesión actual.")

        # TAB 3: CAPA GOLD (INFERENCIA ML)
        with tab3:
            st.header("🏆 Inferencia ML del Expediente (Capa Gold)")
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
            st.header("📁 Historial de Pacientes y Dashboard")
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
                st.subheader("📊 Dashboard de Gestión")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig1 = px.histogram(df_final, x="zona_afectada", title="Distribución por Zona Afectada", color="zona_afectada")
                    st.plotly_chart(fig1, use_container_width=True)
                with col_g2:
                    fig2 = px.scatter(df_final, x="eva_inicial", y="num_sesiones", color="genero", title="Relación Dolor EVA vs Sesiones")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No hay registros disponibles en la base de datos.")

    else:
        st.warning("🔒 Ingrese la contraseña de administrador en la barra lateral para acceder a la gestión completa.")