import streamlit as st
import streamlit.components.v1 as components
import os
import json
import joblib

st.set_page_config(
    page_title="KineData Analytics Pro - Centro de Fisioterapia & IA",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# CONSULTAR PACIENTES DESDE SUPABASE O CARGAR DATOS COMPLETOS (SINTAXIS CORREGIDA)
pacientes_db = [
    {
        "dni": "45446678",
        "nombre": "Roberto Mamani Quispe",
        "edad": 26,
        "genero": "Masculino",
        "zona": "Lumbalgia / Zona Lumbar",
        "eva": 7,
        "fecha_inicio": "2026-10-15",
        "citas_totales": 10,
        "citas_asistidas": 6,
        "citas_faltantes": 4,
        "citas_reprogramadas": 0,
        "reprog_estado": "Aceptada",
        "ocupacion": "Independiente",
        "sueldo": 2500,
        "hijos": 1,
        "esposas": 1,
        "movilidad": "Propia (Carro/Moto)",
        "vivienda": "Propia",
        "email": "roberto.mamani@gmail.com",
        "tlf": "987654321",
        "tutor": "Ana Quispe (Madre)",
        "tutor_tlf": "912345678",
        "horario": "09:00 AM - 10:00 AM",
        "prediccion_continuidad": "Alta (94.2% - Favorable)",
        "historial_eva": [8, 7, 6, 5, 4]
    },
    {
        "dni": "72849102",
        "nombre": "Juan Pérez",
        "edad": 45,
        "genero": "Masculino",
        "zona": "Cervicalgia / Cuello",
        "eva": 6,
        "fecha_inicio": "2026-10-16",
        "citas_totales": 10,
        "citas_asistidas": 7,
        "citas_faltantes": 3,
        "citas_reprogramadas": 1,
        "reprog_estado": "Aceptada",
        "ocupacion": "Empleado",
        "sueldo": 2800,
        "hijos": 2,
        "esposas": 1,
        "movilidad": "Transporte Público",
        "vivienda": "Alquilada",
        "email": "juan.perez@gmail.com",
        "tlf": "987123456",
        "tutor": "María Pérez (Esposa)",
        "tutor_tlf": "999888777",
        "horario": "10:00 AM - 11:00 AM",
        "prediccion_continuidad": "Alta (92.4% - Favorable)",
        "historial_eva": [8, 7, 5, 4, 3]
    },
    {
        "dni": "41920384",
        "nombre": "María Rodríguez",
        "edad": 32,
        "genero": "Femenino",
        "zona": "Tendinitis de Hombro",
        "eva": 5,
        "fecha_inicio": "2026-10-18",
        "citas_totales": 12,
        "citas_asistidas": 10,
        "citas_faltantes": 2,
        "citas_reprogramadas": 0,
        "reprog_estado": "N/A",
        "ocupacion": "Docente",
        "sueldo": 3100,
        "hijos": 1,
        "esposas": 0,
        "movilidad": "Transporte Público",
        "vivienda": "Alquilada",
        "email": "maria.rod@gmail.com",
        "tlf": "998877665",
        "tutor": "Jorge Rodríguez (Padre)",
        "tutor_tlf": "955443322",
        "horario": "11:00 AM - 12:00 PM",
        "prediccion_continuidad": "Muy Alta (95.1% - Favorable)",
        "historial_eva": [7, 5, 4, 3, 2]
    }
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_fisioterapia.pkl")
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Aviso de IA: {e}")

def main():
    base_dir = os.path.dirname(__file__)
    path_html = os.path.join(base_dir, "static", "index.html")
    path_css = os.path.join(base_dir, "static", "styles.css")
    path_js = os.path.join(base_dir, "static", "app.js")

    if os.path.exists(path_html):
        with open(path_html, "r", encoding="utf-8") as f_html:
            html_content = f_html.read()

        if os.path.exists(path_css):
            with open(path_css, "r", encoding="utf-8") as f_css:
                css_content = f_css.read()
                html_content = html_content.replace(
                    '<link rel="stylesheet" href="styles.css">',
                    f'<style>{css_content}</style>'
                )

        if os.path.exists(path_js):
            with open(path_js, "r", encoding="utf-8") as f_js:
                js_content = f_js.read()
                injection_script = f"<script>window.pacientesSupabaseData = {json.dumps(pacientes_db)};</script>\n<script>{js_content}</script>"
                html_content = html_content.replace(
                    '<script src="app.js"></script>',
                    injection_script
                )

        components.html(html_content, height=1000, scrolling=True)
    else:
        st.error("No se encontró 'static/index.html'. Verifique la estructura de carpetas.")

if __name__ == "__main__":
    main()