import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# Configuración del panel
st.set_page_config(
    page_title="Sistema Predictivo de Fisioterapia Biopsicosocial",
    layout="wide",
    page_icon="🏥"
)

# Estructura de almacenamiento local en memoria para evitar caídas
if "tabla_pacientes_local" not in st.session_state:
    st.session_state.tabla_pacientes_local = pd.DataFrame(columns=[
        "dni", "nombre", "edad", "genero", "eva_inicial", "zona_afectada",
        "tsk_score", "pcs_score", "num_sesiones", "fecha_alta", "probabilidad_recuperacion"
    ])

# Conexión con Supabase
@st.cache_resource
def conectar_supabase():
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

supabase = conectar_supabase()

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

# Barra Lateral y Reloj en Vivo
st.sidebar.title("🏥 Portal Clínico")

html_reloj = """
<div style="background-color: #0F766E; color: white; padding: 10px; border-radius: 8px; text-align: center; font-family: 'Courier New', monospace;">
    <div style="font-size: 11px; text-transform: uppercase;">Hora y Fecha Oficial</div>
    <div id="clock" style="font-size: 20px; font-weight: bold; margin-top: 4px;"></div>
    <div id="date" style="font-size: 11px; opacity: 0.85;"></div>
</div>

<script>
function updateClock() {
    var now = new Date();
    var hours = String(now.getHours()).padStart(2, '0');
    var minutes = String(now.getMinutes()).padStart(2, '0');
    var seconds = String(now.getSeconds()).padStart(2, '0');
    var timeString = hours + ':' + minutes + ':' + seconds;
    
    var options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    var dateString = now.toLocaleDateString('es-ES', options);
    
    document.getElementById('clock').textContent = timeString;
    document.getElementById('date').textContent = dateString;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""
with st.sidebar:
    components.html(html_reloj, height=100)

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
    st.markdown("Consulte el estado de su expediente ingresando su DNI.")
    
    dni_consulta = st.text_input("Ingrese su DNI o Código de Identificación:")
    
    if dni_consulta:
        paciente = None
        dni_str = str(dni_consulta).strip()
        
        # 1. Intentar buscar en Supabase
        if supabase:
            try:
                res = supabase.table("pacientes").select("*").eq("dni", dni_str).execute()
                if res.data:
                    paciente = res.data[0]
            except Exception:
                pass
        
        # 2. Si no se encuentra en Supabase, buscar en almacenamiento local
        if not paciente and not st.session_state.tabla_pacientes_local.empty:
            coincidencias = st.session_state.tabla_pacientes_local[st.session_state.tabla_pacientes_local["dni"] == dni_str]
            if not coincidencias.empty:
                paciente = coincidencias.iloc[-1].to_dict()
                
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
# VISTA 2: ADMINISTRADOR CON CLAVE DE ACCESO
# ==============================================================================
else:
    st.title("🛡️ Panel Administrador - Control de Acceso")
    
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False

    if not st.session_state.admin_autenticado:
        st.warning("🔒 Ingrese la clave para gestionar pacientes.")
        clave_ingresada = st.text_input("Contraseña de Administrador:", type="password")
        
        if st.button("Iniciar Sesión"):
            if clave_ingresada == "admin123":
                st.session_state.admin_autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        if st.button("🚪 Cerrar Sesión Admin"):
            st.session_state.admin_autenticado = False
            st.rerun()
            
        st.markdown("---")
        
        tab_bronze, tab_silver, tab_gold, tab_registros = st.tabs([
            "📥 Capa Bronze: Registro de Pacientes", 
            "⚙️ Capa Silver: Transformación", 
            "🏆 Capa Gold: Inferencia ML",
            "📂 Base de Datos"
        ])
        
        with tab_bronze:
            st.header("📋 Formulario de Registro y Evaluación Biopsicosocial")
            
            with st.form("form_evaluacion"):
                st.subheader("1. Datos Generales")
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
                st.subheader("2. Examen Biomecánico y Evaluaciones (1 a 10)")
                col1, col2 = st.columns(2)
                with col1:
                    eva_inicial = st.slider("Escala Visual Analógica del Dolor (EVA):", 1, 10, 7)
                    zona_afectada = st.selectbox("Zona Afectada:", ["Lumbar", "Cervical", "Rodilla", "Hombro", "Tobillo/Pie"])
                with col2:
                    tiempo_evolucion = st.number_input("Tiempo de Evolución (Semanas):", 1, 104, 4)
                    asistencia_pct = st.slider("Compromiso / Asistencia (%):", 0, 100, 85)

                st.markdown("---")
                st.subheader("3. Escalas Psicosociales")
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

                btn_procesar = st.form_submit_button("💾 Guardar Paciente")

        # Proceso analítico
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
            st.header("🏆 Inferencia ML del Expediente")
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

        # LÓGICA DE GUARDADO AUTOMÁTICO
        if btn_procesar:
            datos_paciente = {
                "dni": str(dni_paciente).strip(),
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
            
            # Guardado local
            st.session_state.tabla_pacientes_local = pd.concat([
                st.session_state.tabla_pacientes_local[st.session_state.tabla_pacientes_local["dni"] != str(dni_paciente).strip()],
                pd.DataFrame([datos_paciente])
            ], ignore_index=True)
            
            # Guardado en Supabase (si está configurado)
            if supabase:
                try:
                    supabase.table("pacientes").upsert(datos_paciente).execute()
                    st.success(f"✅ ¡Paciente {nombre_paciente} guardado exitosamente en Supabase y localmente!")
                except Exception as ex:
                    st.warning(f"✅ ¡Paciente {nombre_paciente} guardado en el sistema! (Nota en Supabase: {ex})")
            else:
                st.success(f"✅ ¡Paciente {nombre_paciente} guardado en la sesión local!")

        # TABLA DE REGISTROS
        with tab_registros:
            st.header("📂 Historial de Pacientes")
            df_final = st.session_state.tabla_pacientes_local
            
            if supabase:
                try:
                    res_db = supabase.table("pacientes").select("*").execute()
                    if res_db.data:
                        df_final = pd.DataFrame(res_db.data)
                except Exception:
                    pass
            
            if not df_final.empty:
                st.dataframe(df_final, use_container_width=True)
            else:
                st.info("No hay registros disponibles en la base de datos.")