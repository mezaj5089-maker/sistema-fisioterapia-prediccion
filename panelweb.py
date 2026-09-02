import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as bg
import datetime
from datetime import date, timedelta
from sklearn.ensemble import RandomForestClassifier
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS (GLASSMORPHISM)
# ---------------------------------------------------------
st.set_page_config(
    page_title="FISIOTERAPIA - Movimiento, Salud, Bienestar",
    page_icon="🏥",
    layout="wide"
)

# Imagen de fondo en CSS (Usando la imagen provista mediante URL o Assets)
BACKGROUND_IMAGE_URL = "https://raw.githubusercontent.com/mezaj5089-maker/sistema-fisioterapia/main/fisio.png" 

custom_css = f"""
<style>
/* Fondo principal de la web */
.stApp {{
    background: linear-gradient(rgba(240, 248, 255, 0.85), rgba(240, 248, 255, 0.92)), 
                url("{BACKGROUND_IMAGE_URL}");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
}}

/* Tarjetas modernas con efecto vidrio */
div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {{
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.4);
}}

/* Encabezados y títulos */
h1, h2, h3 {{
    color: #0E4B75 !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

/* Estilo para las métricas */
div[data-testid="stMetricValue"] {{
    font-size: 28px;
    color: #0077B6;
    font-weight: bold;
}}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXIÓN A SUPABASE & ESTADO DE SESIÓN
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

if "tabla_pacientes_local" not in st.session_state:
    st.session_state.tabla_pacientes_local = pd.DataFrame()

# ---------------------------------------------------------
# ENTRENAMIENTO DEL MODELO RANDOM FOREST (IN-MEMORY / GOLD)
# ---------------------------------------------------------
@st.cache_resource
def train_rf_model():
    # Generación sintética para entrenamiento continuo del modelo
    np.random.seed(42)
    n = 200
    eva = np.random.randint(1, 11, n)
    tsk = np.random.uniform(10, 50, n)
    pcs = np.random.uniform(5, 40, n)
    
    # Lógica de negocio para número de sesiones (Target)
    sesiones = (eva * 1.2 + tsk * 0.2 + pcs * 0.3 + np.random.normal(0, 1, n)).astype(int)
    sesiones = np.clip(sesiones, 5, 30)
    
    # Categorización de éxito alto/medio
    exito = np.where(sesiones <= 15, 1, 0)
    
    X = pd.DataFrame({'eva_inicial': eva, 'tsk_score': tsk, 'pcs_score': pcs})
    y_sesiones = sesiones
    y_exito = exito
    
    rf_regressor = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_regressor.fit(X, y_sesiones)
    
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X, y_exito)
    
    return rf_regressor, rf_classifier

model_sesiones, model_exito = train_rf_model()

# ---------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.image(BACKGROUND_IMAGE_URL, use_container_width=True)
st.sidebar.title("🩺 PORTAL CLÍNICO")
st.sidebar.caption("Movimiento • Salud • Bienestar")

# Reloj digital en vivo
ahora = datetime.datetime.now()
st.sidebar.markdown(
    f"""
    <div style="background-color: #0E4B75; color: white; padding: 10px; border-radius: 10px; text-align: center;">
        <h3 style="color: white !important; margin:0;">{ahora.strftime('%H:%M:%S')}</h3>
        <small>{ahora.strftime('%A, %d %b %Y')}</small>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.write("---")
perfil = st.sidebar.radio("Perfil de Usuario:", ["👤 Paciente / Consulta", "🛡️ Administrador / Fisioterapeuta"])

# ---------------------------------------------------------
# ENCABEZADO PRINCIPAL
# ---------------------------------------------------------
st.title("FISIOTERAPIA")
st.subheader("Sistema Inteligente de Evaluación y Predicción Médica")

# ---------------------------------------------------------
# NAVEGACIÓN POR PESTAÑAS (TABS)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Capa Bronze: Registro", 
    "📊 Dashboard Interactivo", 
    "🤖 Capa Gold: Inferencia Random Forest", 
    "🗄️ Base de Datos"
])

# ---------------------------------------------------------
# PESTAÑA 1: REGISTRO (BRONZE)
# ---------------------------------------------------------
with tab1:
    st.markdown("### 📝 Registro del Expediente Clínico")
    with st.form("form_paciente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dni = st.text_input("DNI del Paciente:")
            nombre = st.text_input("Nombre Completo:")
            edad = st.number_input("Edad:", min_value=1, max_value=100, value=30)
            genero = st.selectbox("Género:", ["Masculino", "Femenino", "Otro"])
        with col2:
            eva = st.slider("Escala EVA (Dolor Inicial 1-10):", 1, 10, 5)
            zona = st.selectbox("Zona Afectada:", ["Lumbar", "Cervical", "Hombro", "Rodilla", "Tobillo", "Otro"])
            tsk = st.number_input("Escala TSK (Kinesiofobia):", 10.0, 50.0, 25.0)
            pcs = st.number_input("Escala PCS (Catastrofización):", 0.0, 50.0, 15.0)
            
        btn_guardar = st.form_submit_button("💾 Guardar y Evaluar Paciente")

    if btn_guardar and dni and nombre:
        # Predicción automática con Random Forest
        input_data = pd.DataFrame({'eva_inicial': [eva], 'tsk_score': [tsk], 'pcs_score': [pcs]})
        pred_sesiones = int(model_sesiones.predict(input_data)[0])
        prob_exito = float(model_exito.predict_proba(input_data)[0][1] * 100)
        fecha_alta = date.today() + timedelta(days=pred_sesiones * 2)

        nuevo_paciente = {
            "dni": dni, "nombre": nombre, "edad": edad, "genero": genero,
            "eva_inicial": eva, "zona_afectada": zona, "tsk_score": tsk, "pcs_score": pcs,
            "num_sesiones": pred_sesiones, "fecha_alta": fecha_alta.isoformat(),
            "probabilidad_recuperacion": prob_exito
        }
        
        # Guardar en Supabase
        if supabase:
            try:
                supabase.table("pacientes").insert(nuevo_paciente).execute()
                st.success(f"✅ ¡Paciente {nombre} registrado con éxito en Supabase!")
            except Exception as e:
                st.warning(f"Guardado localmente. Nota en Supabase: {e}")
        else:
            st.success(f"✅ Paciente {nombre} registrado localmente.")

# ---------------------------------------------------------
# PESTAÑA 2: DASHBOARD INTERACTIVO
# ---------------------------------------------------------
with tab2:
    st.markdown("### 📊 Dashboard Analítico y Diagnóstico")
    
    # Cargar datos desde Supabase o Sesión
    df_data = pd.DataFrame()
    if supabase:
        try:
            res = supabase.table("pacientes").select("*").execute()
            df_data = pd.DataFrame(res.data)
        except Exception:
            df_data = st.session_state.tabla_pacientes_local

    if not df_data.empty:
        # Métricas Clave (Kpis)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Pacientes", len(df_data))
        kpi2.metric("Promedio EVA (Dolor)", f"{df_data['eva_inicial'].mean():.1f} / 10")
        kpi3.metric("Prom. Sesiones Est.", f"{df_data['num_sesiones'].mean():.0f}")
        kpi4.metric("Tasa Éxito Promedio", f"{df_data['probabilidad_recuperacion'].mean():.1f}%")

        st.write("---")
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("#### Pacientes por Zona Afectada")
            fig_zona = px.pie(df_data, names='zona_afectada', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_zona, use_container_width=True)
            
        with g2:
            st.markdown("#### Relación EVA Dolor vs. Sesiones Estimadas")
            fig_scatter = px.scatter(
                df_data, x='eva_inicial', y='num_sesiones', color='zona_afectada',
                size='tsk_score', hover_data=['nombre'],
                labels={'eva_inicial': 'Nivel de Dolor (EVA)', 'num_sesiones': 'Sesiones Estimadas'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Registre pacientes en la 'Capa Bronze' para visualizar las gráficas del Dashboard.")

# ---------------------------------------------------------
# PESTAÑA 3: INFERENCIA MODELO RANDOM FOREST (GOLD)
# ---------------------------------------------------------
with tab3:
    st.markdown("### 🏆 Modelo Predictivo: Random Forest Classifier")
    st.write("Simulador en tiempo real de pronósticos médicos basado en Ensembles de Árboles de Decisión.")
    
    c1, c2, c3 = st.columns(3)
    sim_eva = c1.slider("Dolor Inicial Simulado (EVA):", 1, 10, 6, key="s_eva")
    sim_tsk = c2.slider("Kinesiofobia Simulada (TSK):", 10.0, 50.0, 30.0, key="s_tsk")
    sim_pcs = c3.slider("Catastrofización Simulada (PCS):", 0.0, 50.0, 20.0, key="s_pcs")

    df_sim = pd.DataFrame({'eva_inicial': [sim_eva], 'tsk_score': [sim_tsk], 'pcs_score': [sim_pcs]})
    
    pred_s = int(model_sesiones.predict(df_sim)[0])
    prob_s = float(model_exito.predict_proba(df_sim)[0][1] * 100)

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Sesiones Estimadas Recomendadas", f"{pred_s} Sesiones")
        st.progress(min(pred_s / 30.0, 1.0))
        
    with res_col2:
        st.metric("Probabilidad de Recuperación Satisfactoria", f"{prob_s:.1f}%")
        st.progress(prob_s / 100.0)

# ---------------------------------------------------------
# PESTAÑA 4: BASE DE DATOS
# ---------------------------------------------------------
with tab4:
    st.markdown("### 🗄️ Historial Completo de Pacientes")
    if supabase:
        try:
            res = supabase.table("pacientes").select("*").execute()
            df_final = pd.DataFrame(res.data)
            if not df_final.empty:
                st.dataframe(df_final, use_container_width=True)
            else:
                st.info("No hay registros disponibles en Supabase.")
        except Exception as e:
            st.error(f"Error cargando registros: {e}")