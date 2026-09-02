import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Sistema Fisioterapia Predictiva", layout="wide", page_icon="🏥")

# Título Principal
st.title("🏥 Portal Clínico de Fisioterapia Predictiva")
st.markdown("---")

# Selección de Rol en la Barra Lateral
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=100)
st.sidebar.title("Navegación")
rol = st.sidebar.radio("Selecciona tu Rol:", ["👤 Paciente / Visitante", "🛡️ Administrador / Fisioterapeuta"])

# ==========================================
# VISTA 1: PACIENTE / VISITANTE
# ==========================================
if rol == "👤 Paciente / Visitante":
    st.header("👤 Consulta de Pronóstico del Paciente")
    st.info("Ingresa tus datos o código de evaluación para visualizar el estado de tu tratamiento.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 Datos de la Evaluación")
        dni = st.text_input("DNI o Código de Paciente:", "12345678")
        eva = st.slider("Nivel de Dolor (EVA 1-10):", 1, 10, 6)
        asistencia = st.slider("Asistencia a Sesiones (%):", 0, 100, 80)
        
    with col2:
        st.subheader("📊 Pronóstico Estimado")
        
        # Simulación de Predicción
        probabilidad = (asistencia * 0.6) + ((10 - eva) * 4)
        
        if probabilidad >= 65:
            st.success(f"**Pronóstico Favorable:** {probabilidad:.1f}% de probabilidad de pronta recuperación.")
            st.balloons()
        else:
            st.warning(f"**Pronóstico Reservado:** {probabilidad:.1f}% de recuperación. Se requiere ajustar el plan biomecánico.")
            
        # Gráfico Amigable
        st.subheader("📈 Avance Biopsicosocial")
        df_chart = pd.DataFrame({
            "Métrica": ["Asistencia", "Control de Dolor", "Movilidad"],
            "Porcentaje": [asistencia, (10 - eva) * 10, probabilidad]
        })
        st.bar_chart(df_chart.set_index("Métrica"))

# ==========================================
# VISTA 2: ADMINISTRADOR / FISIOTERAPEUTA
# ==========================================
else:
    st.header("🛡️ Panel de Control Administrativo (Medallion System)")
    st.warning("Acceso restringido para edición de datos y recalibración de modelos.")
    
    tab1, tab2, tab3 = st.tabs(["📥 Capa Bronze (Raw)", "⚙️ Capa Silver (Limpieza)", "🏆 Capa Gold (Predicciones)"])
    
    with tab1:
        st.subheader("Registro de Nuevos Pacientes")
        nombre = st.text_input("Nombre Completo:")
        edad = st.number_input("Edad:", 18, 90, 30)
        if st.button("Guardar en Supabase (Bronze)"):
            st.success("✅ Registro guardado exitosamente en la base de datos.")
            
    with tab2:
        st.subheader("Transformación y Métricas (Silver)")
        st.write("Cálculo automático de TSK (Kinesiofobia) y PCS (Catastrofismo).")
        
    with tab3:
        st.subheader("Dashboard General de Analítica (Gold)")
        col_a, col_b = st.columns(2)
        col_a.metric("Total Pacientes", "142", "+12 este mes")
        col_b.metric("Efectividad del Modelo ML", "81%", "Random Forest Classifier")