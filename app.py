import streamlit as st
import pandas as pd
import joblib
import os
from src.db_connector import get_supabase_client, buscar_paciente_por_id, obtener_datos_gold

st.set_page_config(
    page_title="Sistema Predicción Fisioterapia",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Sistema Inteligente de Predicción y Seguimiento en Fisioterapia")
st.caption("Plataforma Clínica impulsada por la Arquitectura Medallion en Supabase y Machine Learning")

# Control de estado de conexión
supabase_activo = False
try:
    client = get_supabase_client()
    supabase_activo = True
    st.sidebar.success("🟢 Conectado a Supabase (Capa Gold)")
except Exception:
    st.sidebar.warning("🔴 Modo Local / Supabase Desconectado")

# Cargar modelo ML
@st.cache_resource
def cargar_modelo():
    ruta = "models/modelo_fisioterapia.joblib"
    if os.path.exists(ruta):
        return joblib.load(ruta)
    return None

modelo = cargar_modelo()

tab1, tab2, tab3 = st.tabs(["⚡ Predicción e Inferencia", "🔍 Consulta de Pacientes", "📊 Dashboard Analítico"])

# TAB 1: PREDICCIÓN
with tab1:
    st.subheader("Evaluación de Paciente e Inferencia Clinica")
    
    with st.form("form_evaluacion"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Datos Demográficos")
            edad = st.number_input("Edad", 18, 80, 45)
            genero = st.selectbox("Género", ["Masculino", "Femenino"])
            imc = st.number_input("IMC", 18.0, 40.0, 25.0, step=0.1)
            ocupacion = st.selectbox("Demanda Ocupacional", ["Sedentaria", "Ligera", "Moderada", "Pesada"])
            actividad = st.selectbox("Actividad Física Previa", ["Nula", "Ocasional", "Regular"])

        with col2:
            st.markdown("#### Evaluación Física")
            tipo_lesion = st.selectbox("Tipo de Lesión", ["Articular", "Muscular", "Postquirurgica", "Tendinosa", "Neurologica"])
            cronicidad = st.selectbox("Cronicidad", ["Agudo", "Subagudo", "Cronico"])
            dolor = st.slider("Dolor Inicial (EVA 0-10)", 0, 10, 6)
            fuerza = st.slider("Fuerza Inicial (Daniels 1-5)", 1, 5, 3)
            rom = st.slider("ROM Inicial (%)", 10, 100, 60)
            cirugias = st.selectbox("Cirugías Previas", [0, 1], format_func=lambda x: "Sí" if x == 1 else "No")
            comorbilidades = st.number_input("Comorbilidades", 0, 5, 0)

        with col3:
            st.markdown("#### Factores Psicosociales")
            tsk = st.slider("Kinesiofobia (TSK 17-68)", 17, 68, 38)
            pcs = st.slider("Catastrofismo (PCS 0-52)", 0, 52, 25)
            asistencia = st.slider("Asistencia Estimada (%)", 0, 100, 80)
            cumplimiento = st.slider("Cumplimiento Ejercicios Casa (1-5)", 1, 5, 3)
            num_sesiones = st.number_input("Sesiones Planificadas", 1, 30, 12)

        btn_evaluar = st.form_submit_button("🧪 Calcular Predicción de Riesgo")

    if btn_evaluar:
        indice_psico = tsk + pcs
        
        datos_entrada = pd.DataFrame([{
            'genero': genero,
            'ocupacion_demanda': ocupacion,
            'tipo_lesion': tipo_lesion,
            'cronicidad': cronicidad,
            'actividad_fisica_previa': actividad,
            'edad': edad,
            'imc': imc,
            'dolor_inicial_eva': dolor,
            'cirugias_previas': cirugias,
            'comorbilidades_num': comorbilidades,
            'rom_inicial_pct': rom,
            'fuerza_inicial_daniels': fuerza,
            'kinesiofobia_tsk': tsk,
            'catastrofismo_pcs': pcs,
            'indice_vulnerabilidad_psicosocial': indice_psico,
            'asistencia_sesiones_pct': asistencia,
            'cumplimiento_ejercicios_casa': cumplimiento,
            'num_sesiones_totales': num_sesiones
        }])

        if modelo is not None:
            prob_exito = modelo.predict_proba(datos_entrada)[0][1]
            prob_riesgo = (1 - prob_exito) * 100

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Probabilidad de Éxito", f"{(prob_exito * 100):.1f}%")
            c2.metric("Riesgo de Fracaso Terapéutico", f"{prob_riesgo:.1f}%")
            c3.metric("Índice Vulnerabilidad (TSK+PCS)", f"{indice_psico} pts")

            if prob_exito >= 0.70:
                st.success("✅ Pronóstico Favorable: Alta tasa de recuperación esperada.")
            elif prob_exito >= 0.40:
                st.warning("⚠️ Pronóstico Moderado: Monitorear adherencia y factores emocionales.")
            else:
                st.error("🚨 Alto Riesgo: Se sugiere intervención personalizada intensiva.")
        else:
            st.error("El modelo no está cargado. Ejecute `python src/train_model.py` en la terminal.")

# TAB 2: CONSULTA SUPABASE
with tab2:
    st.subheader("Buscador de Pacientes en Supabase (Capa Gold)")
    id_input = st.text_input("Ingrese ID del Paciente (Ej: ID-2023001):")
    
    if st.button("Buscar Paciente"):
        if id_input and supabase_activo:
            res = buscar_paciente_por_id(id_input.strip())
            if res:
                p = res[0]
                st.success(f"Paciente Encontrado: {p['id_paciente']}")
                st.json(p)
            else:
                st.error("No se encontró ningún registro para el ID proporcionado.")
        elif not supabase_activo:
            st.warning("Requiere configurar credenciales de Supabase en el archivo .env")

# TAB 3: DASHBOARD
with tab3:
    st.subheader("Métricas Globales (Capa Gold)")
    if supabase_activo:
        try:
            df_g = obtener_datos_gold()
            st.write(f"Total de evaluaciones registradas: **{len(df_g)}**")
            
            m1, m2 = st.columns(2)
            with m1:
                st.markdown("#### Resultado por Tipo de Lesión")
                st.bar_chart(df_g.groupby('tipo_lesion')['resultado_tratamiento'].mean())
            with m2:
                st.markdown("#### Distribución por Cronicidad")
                st.bar_chart(df_g['cronicidad'].value_counts())
        except Exception as err:
            st.error(f"Error al cargar tablero: {err}")
    else:
        st.info("Conecte Supabase para activar el panel en vivo.")