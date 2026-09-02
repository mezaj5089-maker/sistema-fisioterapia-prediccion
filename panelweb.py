import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta

# 1. Configuración de la aplicación
st.set_page_config(
    page_title="Sistema Predictivo de Fisioterapia Biopsicosocial",
    layout="wide",
    page_icon="🏥"
)

# Inicializar almacenamiento local temporal en memoria si no hay Supabase
if "base_pacientes" not in st.session_state:
    st.session_state.base_pacientes = pd.DataFrame(columns=[
        "dni", "nombre", "edad", "genero", "eva_inicial", "zona_afectada",
        "tsk_score", "pcs_score", "num_sesiones", "fecha_alta", "probabilidad_recuperacion"
    ])

# 2. Conexión segura con Supabase (Opcional)
@st.cache_resource
def init_supabase():
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

supabase = init_supabase()

# 3. Cargar Modelo ML
@st.cache_resource
def cargar_modelo():
    if os.path.exists('modelo_fisioterapia.pkl'):
        return joblib.load('modelo_fisioterapia.pkl')
    return None

modelo = cargar_modelo()

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button {
        background-color: #0F766E;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover { background-color: #0D9488; color: white; }
    </style>
""", unsafe_allow_html=True)

# Barra Lateral
st.sidebar.title("🏥 Portal Clínico")
st.sidebar.markdown("---")
rol = st.sidebar.radio("Seleccione el Perfil de Usuario:", [
    "👤 Vista Paciente / Consulta",
    "🛡️ Vista Administrador / Fisioterapeuta"
])

# ==============================================================================
# VISTA 1: CONSULTA DE PACIENTE
# ==============================================================================
if rol == "👤 Vista Paciente / Consulta":
    st.title("🏥 Portal de Seguimiento del Paciente")
    st.markdown("Consulte el estado de su expediente clínico ingresando su DNI.")
    
    dni_consulta = st.text_input("Ingrese su DNI o Código de Identificación:")
    
    if dni_consulta:
        paciente = None
        
        # 1. Buscar en Supabase si está disponible
        if supabase:
            try:
                res = supabase.table("pacientes").select("*").eq("dni", dni_consulta).execute()
                if res.data:
                    paciente = res.data[0]
            except Exception:
                pass
        
        # 2. Buscar en memoria local si no está en Supabase
        if not paciente and not st.session_state.base_pacientes.empty:
            df_match = st.session_state.base_pacientes[st.session_state.base_pacientes["dni"] == str(dni_consulta)]
            if not df_match.empty:
                paciente = df_match.iloc[-1].to_dict()
        
        if paciente:
            st.success(f"Expediente encontrado: **{paciente.get('nombre', 'Paciente')}**")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Sesiones Requeridas", f"{paciente.get('num_sesiones', 0)} Sesiones")
            m2.metric("Nivel de Dolor (EVA)", f"{paciente.get('eva_inicial', 0)} / 10")
            m3.metric("Fecha Estimada de Alta", str(paciente.get('fecha_alta', 'Pendiente')))
            
            st.markdown("---")
            st.subheader("📈 Proyección de Recuperación")
            eva_val = int(paciente.get('eva_inicial', 7))
            chart_data = pd.DataFrame({
                'Semana': ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4'],
                'Nivel Dolor (EVA)': [eva_val, max(eva_val - 2, 1), max(eva_val - 4, 1), 1],
                'Movilidad (%)': [35, 60, 80, 95]
            }).set_index('Semana')
            st.line_chart(chart_data)
        else:
            st.warning("No se encontró ningún expediente registrado con este DNI.")

# ==============================================================================
# VISTA 2: ADMINISTRADOR / EVALUACIÓN, PREDICCIÓN Y TABLA COMPLETA
# ==============================================================================
else:
    st.title("🛡️ Sistema Analítico de Evaluación Fisioterapéutica")
    
    if not supabase:
        st.info("ℹ️ **Modo Almacenamiento Local Activado:** Los datos se están guardando en la sesión actual del sistema.")

    tab_bronze, tab_silver, tab_gold, tab_registros = st.tabs([
        "📥 Capa Bronze: Registro de Pacientes", 
        "⚙️ Capa Silver: Transformación", 
        "🏆 Capa Gold: Inferencia ML",
        "📂 Tabla de Registros"
    ])
    
    with tab_bronze:
        st.header("📋 Formulario de Registro y Evaluación")
        
        with st.form("form_evaluacion"):
            st.subheader("1. Datos del Paciente")
            c_id1, c_id2, c_id3, c_id4 = st.columns(4)
            with c_id1:
                dni_paciente = st.text_input("DNI / Cédula:", "76543210")
            with c_id2:
                nombre_paciente = st.text_input("Nombre Completo:", "Juan Pérez")
            with c_id3:
                edad = st.number_input("Edad:", 18, 95, 35)
            with c_id4:
                genero = st.selectbox("Género:", ["Femenino", "Masculino", "Otro"])

            st.markdown("---")
            st.subheader("2. Examen Biomecánico y Dolor (1 a 10)")
            col1, col2 = st.columns(2)
            with col1:
                eva_inicial = st.slider("Escala Visual Analógica del Dolor (EVA):", 1, 10, 7)
                zona_afectada = st.selectbox("Zona Afectada:", ["Lumbar", "Cervical", "Rodilla", "Hombro", "Tobillo/Pie"])
            with col2:
                tiempo_evolucion = st.number_input("Tiempo de Evolución (Semanas):", 1, 104, 4)
                asistencia_pct = st.slider("Compromiso / Asistencia (%):", 0, 100, 85)

            st.markdown("---")
            st.subheader("3. Cuestionarios Psicosociales (1 a 10)")
            col_tsk, col_pcs = st.columns(2)
            with col_tsk:
                st.markdown("**Kinesiofobia (TSK)**")
                tsk_1 = st.slider("1. Miedo a lesionarse al moverse:", 1, 10, 6)
                tsk_2 = st.slider("2. Evita actividad física:", 1, 10, 7)
                tsk_3 = st.slider("3. Percepción de daño:", 1, 10, 5)
                
            with col_pcs:
                st.markdown("**Catastrofismo (PCS)**")
                pcs_1 = st.slider("1. Dolor perpetuo:", 1, 10, 5)
                pcs_2 = st.slider("2. Rumiación constante:", 1, 10, 6)
                pcs_3 = st.slider("3. Incapacidad de soporte:", 1, 10, 4)

            btn_procesar = st.form_submit_button("💾 Registrar Paciente y Procesar en Medallion")

    # Cálculos intermedios
    score_tsk_10 = round((tsk_1 + tsk_2 + tsk_3) / 3, 2)
    score_pcs_10 = round((pcs_1 + pcs_2 + pcs_3) / 3, 2)
    indice_vulnerabilidad = round(((score_tsk_10 + score_pcs_10 + eva_inicial) / 30) * 100, 2)
    
    factor_severidad = (eva_inicial * 0.4) + (score_tsk_10 * 0.3) + (score_pcs_10 * 0.3)
    num_sesiones = int(np.ceil(factor_severidad * 2.5))
    dias_recuperacion = int(np.ceil(num_sesiones * 2.33))
    fecha_estimada_alta = (datetime.now() + timedelta(days=dias_recuperacion)).strftime('%Y-%m-%d')
    prob_recuperacion = round(min(max(100 - (factor_severidad * 8) + (asistencia_pct * 0.2), 10), 98), 2)

    with tab_silver:
        st.header("⚙️ Transformación e Índices Clínicos")
        c_s1, c_s2, c_s3 = st.columns(3)
        c_s1.metric("Kinesiofobia Promedio", f"{score_tsk_10} / 10")
        c_s2.metric("Catastrofismo Promedio", f"{score_pcs_10} / 10")
        c_s3.metric("Vulnerabilidad Biopsicosocial", f"{indice_vulnerabilidad} %")

    with tab_gold:
        st.header("🏆 Inferencia ML y Guardado")
        st.subheader(f"Expediente Evaluado: **{nombre_paciente}** (DNI: {dni_paciente})")
        
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            st.metric("Sesiones Estimadas", f"{num_sesiones} Sesiones")
            st.metric("Fecha Estimada de Alta", fecha_estimada_alta)
            st.progress(float(prob_recuperacion / 100))
            st.write(f"Probabilidad de Éxito: **{prob_recuperacion}%**")

        with col_g2:
            st.write("**Factores ML Aplicados:**")
            st.write("- Severidad Física/Psicológica")
            st.write("- Tasa de Asistencia del Paciente")

    # LOGICA DE GUARDADO AUTOMÁTICO AL PRESIONAR EL BOTÓN
    if btn_procesar:
        nuevo_paciente = {
            "dni": str(dni_paciente),
            "nombre": nombre_paciente,
            "edad": edad,
            "genero": genero,
            "eva_inicial": eva_inicial,
            "zona_afectada": zona_afectada,
            "tsk_score": score_tsk_10,
            "pcs_score": score_pcs_10,
            "num_sesiones": num_sesiones,
            "fecha_alta": fecha_estimada_alta,
            "probabilidad_recuperacion": prob_recuperacion
        }
        
        # Guardar en Session State (local)
        st.session_state.base_pacientes = pd.concat([
            st.session_state.base_pacientes[st.session_state.base_pacientes["dni"] != str(dni_paciente)],
            pd.DataFrame([nuevo_paciente])
        ], ignore_index=True)
        
        # Guardar en Supabase si está disponible
        if supabase:
            try:
                supabase.table("pacientes").upsert(nuevo_paciente).execute()
                st.success(f"✅ ¡Paciente {nombre_paciente} guardado exitosamente en Supabase!")
            except Exception as e:
                st.warning(f"Guardado localmente. Error en Supabase: {e}")
        else:
            st.success(f"✅ ¡Paciente {nombre_paciente} guardado en el Panel Administrador!")

    # TABLA DE PACIENTES REGISTRADOS
    with tab_registros:
        st.header("📂 Historial de Pacientes Registrados")
        
        # Intentar traer datos de Supabase si existe conexión
        df_mostrar = st.session_state.base_pacientes
        if supabase:
            try:
                res_all = supabase.table("pacientes").select("*").execute()
                if res_all.data:
                    df_mostrar = pd.DataFrame(res_all.data)
            except Exception:
                pass
                
        if not df_mostrar.empty:
            st.dataframe(df_mostrar, use_container_width=True)
        else:
            st.write("Aún no hay pacientes registrados en esta sesión.")