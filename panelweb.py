import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="PhysioPredict AI — Dashboard Clínico",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px;
        border: none;
    }
    .stButton>button:hover { background-color: #0056b3; }
    </style>
""", unsafe_allow_html=True)

# Inicializar historial de pacientes en sesión
if "historial_pacientes" not in st.session_state:
    st.session_state["historial_pacientes"] = pd.DataFrame(columns=[
        "Paciente", "Edad", "Lesión", "Riesgo Psicosocial", "Prob. Éxito (%)", "Pronóstico"
    ])

# Cargar el modelo entrenado
@st.cache_resource
def load_model():
    return joblib.load("modelo_fisioterapia.pkl")

try:
    model = load_model()
except Exception as e:
    st.error("❌ No se encontró el archivo 'modelo_fisioterapia.pkl'. Asegúrate de haber ejecutado 'train_model.py'.")
    st.stop()

# Header Principal
st.title("🏥 PhysioPredict AI — Plataforma Clínica Inteligente")
st.markdown("Sistema predictivo de efectividad terapéutica y gestión de pacientes en tiempo real.")

# Pestañas de la Aplicación
tab_evaluacion, tab_historial, tab_metricas = st.tabs([
    "📋 Evaluador de Paciente", 
    "👥 Historial & Clasificación de Pacientes", 
    "📊 Métricas & Estadísticas del Modelo AI"
])

# ==========================================
# TAB 1: EVALUADOR DE PACIENTE
# ==========================================
with tab_evaluacion:
    st.sidebar.header("👤 Datos de Identificación")
    nombre_paciente = st.sidebar.text_input("Nombre Completo del Paciente", value="Paciente 1")

    st.sidebar.header("📋 Datos de Evaluación Clínico-Funcional")
    edad = st.sidebar.number_input("Edad", min_value=12, max_value=95, value=35)
    genero = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])
    imc = st.sidebar.slider("IMC (Índice de Masa Corporal)", 15.0, 45.0, 24.5)
    ocupacion = st.sidebar.selectbox("Demanda Física Laboral", ["Baja", "Media", "Alta"])
    tipo_lesion = st.sidebar.selectbox("Tipo de Lesión", ["Lumbago", "Cervicalgia", "Hombro", "Rodilla", "Ancla", "Otra"])
    cronicidad = st.sidebar.selectbox("Cronicidad", ["Agudo", "Subagudo", "Crónico"])
    cirugias = st.sidebar.selectbox("Cirugías Previas", ["0", "1"])

    st.sidebar.divider()
    st.sidebar.subheader("🩺 Evaluación Funcional")
    dolor_eva = st.sidebar.slider("Dolor Inicial (Escala EVA 0-10)", 0, 10, 6)
    comorbilidades = st.sidebar.number_input("Número de Comorbilidades", 0, 5, 1)
    rom_pct = st.sidebar.slider("Rango de Movimiento (% ROM Inicial)", 0, 100, 65)
    fuerza_daniels = st.sidebar.slider("Fuerza Muscular (Escala Daniels 0-5)", 0, 5, 3)

    st.sidebar.divider()
    st.sidebar.subheader("🧠 Factores Psicosociales")
    kinesiofobia = st.sidebar.slider("Escala de Kinesiofobia (TSK 17-68)", 17, 68, 30)
    catastrofismo = st.sidebar.slider("Escala de Catastrofismo (PCS 0-52)", 0, 52, 18)
    actividad_previa = st.sidebar.selectbox("Actividad Física Previa", ["Sedentario", "Ocasional", "Regular", "Alto Rendimiento"])
    asistencia_pct = st.sidebar.slider("Proyección Asistencia a Sesiones (%)", 0, 100, 85)
    cumplimiento_casa = st.sidebar.selectbox("Cumplimiento Ejercicios en Casa", ["Bajo", "Medio", "Alto"])
    num_sesiones = st.sidebar.number_input("Número de Sesiones Planificadas", 1, 60, 12)

    indice_psicosocial = kinesiofobia + catastrofismo

    input_dict = {
        "edad": edad, "genero": genero, "imc": imc, "ocupacion_demanda": ocupacion,
        "tipo_lesion": tipo_lesion, "cronicidad": cronicidad, "cirugias_previas": str(cirugias),
        "dolor_inicial_eva": dolor_eva, "comorbilidades_num": comorbilidades,
        "rom_inicial_pct": rom_pct, "fuerza_inicial_daniels": fuerza_daniels,
        "kinesiofobia_tsk": kinesiofobia, "catastrofismo_pcs": catastrofismo,
        "indice_vulnerabilidad_psicosocial": indice_psicosocial,
        "actividad_fisica_previa": actividad_previa, "asistencia_sesiones_pct": asistencia_pct,
        "cumplimiento_ejercicios_casa": cumplimiento_casa, "num_sesiones_totales": num_sesiones
    }

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader(f"📊 Resumen Clínico: {nombre_paciente}")
        st.write(f"**Vulnerabilidad Psicosocial (TSK + PCS):** {indice_psicosocial} pts")
        
        if indice_psicosocial > 60:
            riesgo_txt = "ALTO"
            st.error("⚠️ **Riesgo Psicosocial ALTO:** Posible evitación del movimiento o sensibilización central.")
        elif indice_psicosocial > 35:
            riesgo_txt = "MODERADO"
            st.warning("⚡ **Riesgo Psicosocial MODERADO:** Requiere educación en neurociencia del dolor.")
        else:
            riesgo_txt = "BAJO"
            st.success("✅ **Riesgo Psicosocial BAJO:** Buen perfil de afrontamiento.")

        # Gráfico Biopsicosocial en Radar (Sintaxis Corregida)
        categories = ['Dolor EVA', '% ROM', 'Fuerza Daniels', 'Kinesiofobia', 'Catastrofismo']
        values = [dolor_eva * 10, rom_pct, fuerza_daniels * 20, (kinesiofobia/68)*100, (catastrofismo/52)*100]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values, 
            theta=categories, 
            fill='toself', 
            fillcolor='rgba(0, 123, 255, 0.4)',
            line=dict(color='#007bff')
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_radar, use_container_width=True)

        btn_predict = st.button("🚀 PREDECIR Y REGISTRAR PACIENTE")

    with col_right:
        st.subheader("📈 Resultado del Diagnóstico IA")

        if btn_predict:
            input_df = pd.DataFrame([input_dict])
            input_encoded = pd.get_dummies(input_df)
            expected_features = model.feature_names_in_
            input_encoded = input_encoded.reindex(columns=expected_features, fill_value=0)

            prediction = model.predict(input_encoded)[0]
            prob_exito = model.predict_proba(input_encoded)[0][1] * 100

            # Guardar en Historial de Sesión
            pronostico_str = "Pronta Recuperación (Fausto)" if (prediction == 1 or prob_exito >= 50) else "Mayor Tiempo de Recuperación (Reservado)"
            nuevo_paciente = {
                "Paciente": nombre_paciente, "Edad": edad, "Lesión": tipo_lesion,
                "Riesgo Psicosocial": riesgo_txt, "Prob. Éxito (%)": f"{prob_exito:.1f}%",
                "Pronóstico": pronostico_str
            }
            st.session_state["historial_pacientes"] = pd.concat([
                st.session_state["historial_pacientes"], pd.DataFrame([nuevo_paciente])
            ], ignore_index=True)

            # Velocímetro
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=prob_exito,
                title={'text': "Probabilidad de Éxito (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#007bff"},
                    'steps': [
                        {'range': [0, 50], 'color': "#ffe6e6"},
                        {'range': [50, 75], 'color': "#fff3cd"},
                        {'range': [75, 100], 'color': "#d4edda"}
                    ],
                }
            ))
            fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

            if pronostico_str == "Pronta Recuperación (Fausto)":
                st.success(f"🎉 **Pronóstico FAUSTO ({prob_exito:.1f}% Éxito)**")
                st.markdown("✅ **Alta velocidad de recuperación.** Proceder con plan de carga progresiva estándar.")
            else:
                st.error(f"⚠️ **Pronóstico RESERVADO ({prob_exito:.1f}% Éxito)**")
                st.markdown("⚠️ **Tomará más tiempo en recuperar.** Se recomienda terapia cognitivo-conductual y modificación de cargas.")
        else:
            st.info("👈 Configura al paciente en la barra lateral y presiona **PREDECIR Y REGISTRAR PACIENTE**.")

# ==========================================
# TAB 2: HISTORIAL Y LISTA DE PACIENTES
# ==========================================
with tab_historial:
    st.subheader("👥 Registro y Clasificación de Pacientes Ingresados")
    
    if not st.session_state["historial_pacientes"].empty:
        col_fausto, col_reservado = st.columns(2)
        
        df_hist = st.session_state["historial_pacientes"]
        
        with col_fausto:
            st.success("🟢 **Pacientes en Pronta Recuperación**")
            st.dataframe(df_hist[df_hist["Pronóstico"] == "Pronta Recuperación (Fausto)"], use_container_width=True)
            
        with col_reservado:
            st.error("🔴 **Pacientes que Requerirán Más Tiempo**")
            st.dataframe(df_hist[df_hist["Pronóstico"] == "Mayor Tiempo de Recuperación (Reservado)"], use_container_width=True)
    else:
        st.info("Aún no se han evaluado pacientes en esta sesión. Completa los datos en la pestaña 'Evaluador de Paciente'.")

# ==========================================
# TAB 3: MÉTRICAS Y DESEMPEÑO DEL MODELO
# ==========================================
with tab_metricas:
    st.subheader("📊 Métricas Globales del Modelo (Capa GOLD Supabase)")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Precisión Global (Accuracy)", "81.0%", "Medallion Architecture")
    m2.metric("Muestra Entrenada", "1,000 Pacientes", "Supabase DB")
    m3.metric("F1-Score Promedio", "0.81", "Alta Fiabilidad")
    m4.metric("Algoritmo", "Random Forest", "Supervisado")
    
    st.divider()
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("### Importancia de Variables en la Predicción")
        importance_df = pd.DataFrame({
            "Variable": ["Vulnerabilidad Psicosocial", "Asistencia a Sesiones", "Dolor EVA Inicial", "% ROM Inicial", "Cumplimiento Casa"],
            "Importancia (%)": [35, 25, 18, 12, 10]
        })
        fig_imp = px.bar(importance_df, x="Importancia (%)", y="Variable", orientation='h', color="Importancia (%)", color_continuous_scale="Blues")
        st.plotly_chart(fig_imp, use_container_width=True)
        
    with col_g2:
        st.markdown("### Matriz de Confusión del Entrenamiento")
        conf_matrix = pd.DataFrame([[73, 23], [15, 89]], columns=["Pred: No Exitoso", "Pred: Exitoso"], index=["Real: No Exitoso", "Real: Exitoso"])
        fig_cm = px.imshow(conf_matrix, text_auto=True, color_continuous_scale="Blues")
        st.plotly_chart(fig_cm, use_container_width=True)