import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime

# 1. Configuración de la página
st.set_page_config(
    page_title="KineData Analytics - Medicina Física & IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para el tema oscuro idéntico a las capturas
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. Barra Lateral (Sidebar)
with st.sidebar:
    st.title("⚡ KineData Analytics")
    st.caption("Medicina Física & IA")
    
    st.info(f"🕒 HORA LOCAL (PERÚ)\n\n{datetime.datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}")
    
    st.write("**MODO DE VISTA**")
    modo_vista = st.radio("Seleccione Rol:", ["🔒 Admin/Fisio", "👤 Paciente"], label_visibility="collapsed")

# 3. Vista Principal
if modo_vista == "👤 Paciente":
    st.subheader("🔍 Consulta de Evolución del Paciente")
    st.write("Ingrese su Documento Nacional de Identidad (DNI) para consultar el pronóstico estimado por IA y las métricas de rehabilitación.")
    
    col_dni, col_btn = st.columns([3, 1])
    with col_dni:
        dni_input = st.text_input("DNI del Paciente", placeholder="Ej. 73829104", label_visibility="collapsed")
    with col_btn:
        btn_consultar = st.button("✨ Consultar Diagnóstico", use_container_width=True)
        
    if btn_consultar and dni_input:
        st.success(f"Mostrando información registrada para el DNI: {dni_input}")

else:
    # Modo Admin / Fisio con Arquitectura Medallion (Pestañas superiores)
    tab_bronze, tab_silver, tab_gold, tab_dash = st.tabs([
        "📥 Capa Bronze (Registro)",
        "📊 Capa Silver (Registros Staging)",
        "🧠 Capa Gold (Inferencia ML)",
        "📊 HTML Dashboard Analytics"
    ])
    
    # --- PESTAÑA 1: CAPA BRONZE ---
    with tab_bronze:
        col_form, col_3d = st.columns([3, 2])
        with col_form:
            st.subheader("👤 Capa Bronze: Captura de Datos Clínicos")
            st.caption("Ingreso de variables biomecánicas y psicológicas del paciente.")
            
            c1, c2 = st.columns(2)
            c1.text_input("DNI del Paciente *", placeholder="8 dígitos")
            c2.text_input("Nombre Completo *", placeholder="Nombre Apellido")
            
            c3, c4, c5 = st.columns(3)
            c3.number_input("Edad", value=34)
            c4.selectbox("Género", ["Masculino", "Femenino", "Otro"])
            c5.selectbox("Zona Afectada *", ["Hombro", "Rodilla", "Lumbar", "Cervical", "Tobillo"])
            
            st.slider("Nivel de Dolor (Escala EVA):", 1, 10, 6)
            st.slider("Kinesiofobia (Escala TSK-11):", 11, 44, 28)
            st.slider("Catastrofización (Escala PCS):", 0, 52, 22)
            
            st.button("💾 Guardar e Inferir Pronóstico", use_container_width=True)
            
        with col_3d:
            st.subheader("🧊 Visor 3D Anatómico Interactivo")
            st.caption("Interacción visual biomecánica (Girar / Seleccionar zona)")
            
            # Renderizador de modelo 3D en HTML/Three.js
            three_js_code = """
            <div id="container3d" style="width:100%; height:300px; background-color:#0b0f19; border-radius:10px;"></div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script>
                const container = document.getElementById('container3d');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                renderer.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer.domElement);
                
                const geometry = new THREE.CylinderGeometry(0.8, 0.6, 2.5, 16);
                const material = new THREE.MeshPhongMaterial({ color: 0xa855f7, wireframe: true });
                const mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);
                
                const light = new THREE.DirectionalLight(0xffffff, 1);
                light.position.set(2, 2, 5).normalize();
                scene.add(light);
                
                camera.position.z = 4;
                function animate() {
                    requestAnimationFrame(animate);
                    mesh.rotation.y += 0.01;
                    renderer.render(scene, camera);
                }
                animate();
            </script>
            """
            components.html(three_js_code, height=320)

    # --- PESTAÑA 2: CAPA SILVER ---
    with tab_silver:
        st.subheader("🗄️ Capa Silver: Registros Depurados & Enriquecidos")
        st.caption("Tabla de almacenamiento estructurado de pacientes ingresados.")
        
        datos_silver = pd.DataFrame([
            {"DNI": "73829104", "PACIENTE": "María Torres", "EDAD/GÉNERO": "42 yrs / Femenino", "ZONA": "Hombro", "EVA": "7/10", "TSK/PCS": "32 / 28", "SESIONES ESTIMADAS": "16 ses.", "ALTA PREVISTA": "12/11/2026"},
            {"DNI": "72819203", "PACIENTE": "Carlos Mendoza", "EDAD/GÉNERO": "34 yrs / Masculino", "ZONA": "Lumbar", "EVA": "6/10", "TSK/PCS": "28 / 22", "SESIONES ESTIMADAS": "14 ses.", "ALTA PREVISTA": "28/10/2026"},
            {"DNI": "45129834", "PACIENTE": "Jorge Benítez", "EDAD/GÉNERO": "55 yrs / Masculino", "ZONA": "Rodilla", "EVA": "8/10", "TSK/PCS": "36 / 35", "SESIONES ESTIMADAS": "20 ses.", "ALTA PREVISTA": "05/12/2026"}
        ])
        st.dataframe(datos_silver, use_container_width=True)

    # --- PESTAÑA 3: CAPA GOLD ---
    with tab_gold:
        st.subheader("🧠 Capa Gold: Inferencia del Modelo Random Forest")
        st.caption("Métricas predichas en tiempo real para el último paciente procesado.")
        
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="metric-card"><h4>Paciente Evaluado</h4><h2>Carlos Mendoza</h2><p>DNI: 72819203 | Zona: Lumbar</p></div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="metric-card"><h4>Predicción de Sesiones</h4><h2 style="color:#a855f7;">14 Sesiones</h2><p>R² Score Modelo: 0.92</p></div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="metric-card"><h4>Probabilidad Éxito Rehabilitación</h4><h2 style="color:#10b981;">88%</h2><p>Clasificación: Alta Probabilidad</p></div>', unsafe_allow_html=True)

    # --- PESTAÑA 4: DASHBOARD ANALYTICS ---
    with tab_dash:
        st.subheader("📊 Filtros Avanzados Analytics")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Pacientes", "3", "Base de datos activa")
        k2.metric("Promedio EVA Inicial", "7.0", "Escala de Dolor")
        k3.metric("Sesiones Medias Estimadas", "17", "Duración clínica")
        k4.metric("Tasa Éxito Estimada", "83%", "Terapia efectiva")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.write("**Promedio de Sesiones por Zona Corporal**")
            chart_data_bar = pd.DataFrame({'Zona': ['Hombro', 'Rodilla', 'Lumbar'], 'Sesiones': [16, 20, 14]}).set_index('Zona')
            st.bar_chart(chart_data_bar)
        with col_g2:
            st.write("**Distribución de Pacientes por Zona Afectada**")
            chart_data_pie = pd.DataFrame({'Zona': ['Hombro', 'Rodilla', 'Lumbar', 'Cervical', 'Tobillo'], 'Pacientes': [30, 25, 20, 15, 10]}).set_index('Zona')
            st.line_chart(chart_data_pie)