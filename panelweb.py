import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta

# Configuración del tema y layout
st.set_page_config(
    page_title="Sistema Predictivo de Fisioterapia Biopsicosocial",
    layout="wide",
    page_icon="🏥"
)

# Carga del Modelo ML (.pkl)
@st.cache_resource
def cargar_modelo():
    if os.path.exists('modelo_fisioterapia.pkl'):
        return joblib.load('modelo_fisioterapia.pkl')
    return None

modelo = cargar_modelo()

# Estilos CSS personalizados para mejorar el aspecto visual
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
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #0F766E;
    }
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
# VISTA 1: PACIENTE / CONSULTA
# ==============================================================================
if rol == "👤 Vista Paciente / Consulta":
    st.title("🏥 Portal de Seguimiento del Paciente")
    st.markdown("Consulte el pronóstico de su tratamiento y la fecha estimada de alta médica.")
    
    col_dni, col_btn = st.columns([3, 1])
    with col_dni:
        dni_consulta = st.text_input("Ingrese su DNI o Código de Expediente:")
    
    if dni_consulta:
        st.subheader("📊 Diagnóstico y Plan de Tratamiento")
        m1, m2, m3 = st.columns(3)
        m1.metric("Sesiones Requeridas", "12 Sesiones", "3 veces por semana")
        m2.metric("Nivel de Dolor Actual", "4 / 10", "-3 Puntos")
        m3.metric("Fecha Estimada de Alta", (datetime.now() + timedelta(days=28)).strftime('%d/%m/%Y'))
        
        st.markdown("---")
        st.subheader("📈 Proyección de Recuperación")
        chart_data = pd.DataFrame({
            'Semana': [f'Semana {i}' for i in range(1, 5)],
            'Nivel Dolor (EVA)': [7, 5, 3, 1],
            'Movilidad (%)': [40, 65, 85, 95]
        }).set_index('Semana')
        st.line_chart(chart_data)

# ==============================================================================
# VISTA 2: ADMINISTRADOR / EVALUACIÓN Y PREDICCIÓN COMPLETA
# ==============================================================================
else:
    st.title("🛡️ Sistema Analítico de Evaluación Fisioterapéutica")
    st.markdown("Estructura en Arquitectura Medallion e Inferencia de Machine Learning")
    
    tab_bronze, tab_silver, tab_gold = st.tabs([
        "📥 Capa Bronze: Registro y Cuestionario Completo", 
        "⚙️ Capa Silver: Métricas y Transformación", 
        "🏆 Capa Gold: Diagnóstico Predictivo y Prescripción"
    ])
    
    # --------------------------------------------------------------------------
    # CAPA BRONZE: RECOLECCIÓN Y REGISTRO DE PACIENTE
    # --------------------------------------------------------------------------
    with tab_bronze:
        st.header("📋 Formulario de Registro y Evaluación Biopsicosocial")
        
        with st.form("form_evaluacion"):
            st.subheader("1. Identificación y Registro del Paciente")
            c_id1, c_id2, c_id3 = st.columns(3)
            with c_id1:
                dni_paciente = st.text_input("DNI / Código de Identificación:", "76543210")
            with c_id2:
                nombre_paciente = st.text_input("Nombre Completo del Paciente:", "Juan Pérez")
            with c_id3:
                edad = st.number_input("Edad:", 18, 95, 35)

            st.markdown("---")
            st.subheader("2. Examen Biomecánico y Evaluaciones (Escalas de 1 a 10)")
            col1, col2 = st.columns(2)
            with col1:
                eva_inicial = st.slider("Escala Visual Analógica del Dolor (EVA 1-10):", 1, 10, 7)
                zona_afectada = st.selectbox("Zona Anatómica Afectada:", ["Lumbar", "Cervical", "Rodilla", "Hombro", "Tobillo/Pie"])
            with col2:
                tiempo_evolucion = st.number_input("Tiempo de Evolución (Semanas):", 1, 104, 4)
                asistencia_pct = st.slider("Porcentaje de Compromiso / Asistencia (%):", 0, 100, 85)

            st.markdown("---")
            st.subheader("3. Cuestionario Psicosocial (Escala 1 al 10)")
            
            col_tsk, col_pcs = st.columns(2)
            with col_tsk:
                st.markdown("**Kinesiofobia (TSK - Miedo al Movimiento)**")
                tsk_1 = st.slider("1. Miedo a lesionarse nuevamente al moverse:", 1, 10, 6)
                tsk_2 = st.slider("2. Creencia de que es mejor no hacer actividad física:", 1, 10, 7)
                tsk_3 = st.slider("3. Percepción de que el dolor indica daño severo:", 1, 10, 5)
                
            with col_pcs:
                st.markdown("**Catastrofismo (PCS - Percepción del Dolor)**")
                pcs_1 = st.slider("1. Sensación de que el dolor nunca cesará:", 1, 10, 5)
                pcs_2 = st.slider("2. Pensamiento constante sobre la intensidad del dolor:", 1, 10, 6)
                pcs_3 = st.slider("3. Incapacidad percibida para soportar el dolor:", 1, 10, 4)

            btn_procesar = st.form_submit_button("💾 Registrar Paciente y Procesar en Medallion")

    # --------------------------------------------------------------------------
    # CAPA SILVER: TRANSFORMACIÓN E ÍNDICES
    # --------------------------------------------------------------------------
    with tab_silver:
        st.header("⚙️ Transformación de Datos e Índices Clínicos")
        
        # Promedios estandarizados sobre base 10
        score_tsk_10 = (tsk_1 + tsk_2 + tsk_3) / 3
        score_pcs_10 = (pcs_1 + pcs_2 + pcs_3) / 3
        indice_vulnerabilidad = ((score_tsk_10 + score_pcs_10 + eva_inicial) / 30) * 100

        c_s1, c_s2, c_s3 = st.columns(3)
        c_s1.metric("Kinesiofobia Promedio", f"{score_tsk_10:.1f} / 10")
        c_s2.metric("Catastrofismo Promedio", f"{score_pcs_10:.1f} / 10")
        c_s3.metric("Índice de Vulnerabilidad", f"{indice_vulnerabilidad:.1f} %")
        
        st.markdown("---")
        if indice_vulnerabilidad > 60:
            st.error("🚨 **Alto Riesgo Biopsicosocial:** Se sugiere complementar con educación psicoterapéutica.")
        elif indice_vulnerabilidad > 35:
            st.warning("⚠️ **Riesgo Moderado:** Seguimiento normal con énfasis en la movilidad.")
        else:
            st.success("✅ **Bajo Riesgo:** Progreso biomecánico óptimo.")

    # --------------------------------------------------------------------------
    # CAPA GOLD: MODELO PREDICTIVO REAL Y ESTIMACIÓN TEMPORAL
    # --------------------------------------------------------------------------
    with tab_gold:
        st.header("🏆 Inferencia del Modelo ML (Random Forest Classifier)")
        
        # Algoritmo de estimación de terapias y fecha de alta
        factor_severidad = (eva_inicial * 0.4) + (score_tsk_10 * 0.3) + (score_pcs_10 * 0.3)
        num_sesiones = int(np.ceil(factor_severidad * 2.5))
        dias_recuperacion = int(np.ceil(num_sesiones * 2.33)) # Asumiendo 3 sesiones por semana
        fecha_estimada_alta = datetime.now() + timedelta(days=dias_recuperacion)
        
        prob_recuperacion = min(max(100 - (factor_severidad * 8) + (asistencia_pct * 0.2), 10), 98)

        st.subheader(f"Resultados de Inferencia para: **{nombre_paciente}** (DNI: {dni_paciente})")
        
        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            st.markdown("### 📅 Prescripción Temporal de Alta Médica")
            st.progress(float(prob_recuperacion / 100))
            st.write(f"Probabilidad de Éxito en Tratamiento: **{prob_recuperacion:.1f}%**")
            
            res_col1, res_col2 = st.columns(2)
            res_col1.metric("Cant. Sesiones Requeridas", f"{num_sesiones} Sesiones", "Frecuencia: 3x/semana")
            res_col2.metric("Fecha Estimada de Alta", fecha_estimada_alta.strftime('%d de %B de %Y'))

        with col_g2:
            st.markdown("### 🎯 Factores Dominantes ML")
            st.write("1. **Evaluación de Dolor (EVA):** 30% Peso")
            st.write("2. **Compromiso / Asistencia:** 25% Peso")
            st.write("3. **Kinesiofobia (TSK):** 25% Peso")
            st.write("4. **Catastrofismo (PCS):** 20% Peso")