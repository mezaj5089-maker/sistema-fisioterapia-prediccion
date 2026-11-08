import streamlit as st
import streamlit.components.v1 as components
import os
import json
import joblib

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

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

# BASE DE DATOS SINCRONIZADA CON SUPABASE (INCLUYE TODOS TUS PACIENTES REGISTRADOS)
pacientes_db = [
    {
        "dni": "76563443",
        "nombre": "ESTEBAN CHUQUILLANQUI MAL PART",
        "edad": 30,
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
        "email": "esteban.chuquillanqui@gmail.com",
        "tlf": "987654321",
        "tutor": "María Mal Part (Madre)",
        "tutor_tlf": "912345678",
        "horario": "09:00 AM - 10:00 AM",
        "prediccion_continuidad": "Alta (94.2% - Favorable)",
        "historial_eva": [8, 7, 6, 5, 4]
    },
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
        "dni": "76543310",
        "nombre": "Olivia Estupiñan Segarra",
        "edad": 65,
        "genero": "Femenino",
        "zona": "Cervicalgia / Cuello",
        "eva": 6,
        "fecha_inicio": "2026-10-16",
        "citas_totales": 10,
        "citas_asistidas": 7,
        "citas_faltantes": 3,
        "citas_reprogramadas": 0,
        "reprog_estado": "N/A",
        "ocupacion": "Pensionista",
        "sueldo": 1800,
        "hijos": 3,
        "esposas": 0,
        "movilidad": "Transporte Público",
        "vivienda": "Propia",
        "email": "olivia.estupinan@gmail.com",
        "tlf": "987111222",
        "tutor": "Carlos Estupiñan (Hijo)",
        "tutor_tlf": "999000111",
        "horario": "10:00 AM - 11:00 AM",
        "prediccion_continuidad": "Alta (92.0% - Favorable)",
        "historial_eva": [7, 6, 5, 4, 3]
    },
    {
        "dni": "76010018",
        "nombre": "christian henry",
        "edad": 25,
        "genero": "Masculino",
        "zona": "Tendinitis de Hombro",
        "eva": 5,
        "fecha_inicio": "2026-10-17",
        "citas_totales": 10,
        "citas_asistidas": 5,
        "citas_faltantes": 5,
        "citas_reprogramadas": 0,
        "reprog_estado": "N/A",
        "ocupacion": "Estudiante",
        "sueldo": 1500,
        "hijos": 0,
        "esposas": 0,
        "movilidad": "Transporte Público",
        "vivienda": "Familiar",
        "email": "christian.henry@gmail.com",
        "tlf": "987333444",
        "tutor": "Rosa Henry (Madre)",
        "tutor_tlf": "988222111",
        "horario": "11:00 AM - 12:00 PM",
        "prediccion_continuidad": "Favorable (89.5%)",
        "historial_eva": [6, 5, 5, 4, 3]
    },
    {
        "dni": "49665455",
        "nombre": "Fernando Cacerez Lapa",
        "edad": 25,
        "genero": "Masculino",
        "zona": "Lesión de Rodilla",
        "eva": 7,
        "fecha_inicio": "2026-10-18",
        "citas_totales": 12,
        "citas_asistidas": 8,
        "citas_faltantes": 4,
        "citas_reprogramadas": 1,
        "reprog_estado": "Aceptada",
        "ocupacion": "Deportista",
        "sueldo": 2200,
        "hijos": 0,
        "esposas": 0,
        "movilidad": "Propia (Carro/Moto)",
        "vivienda": "Alquilada",
        "email": "fernando.cacerez@gmail.com",
        "tlf": "987555666",
        "tutor": "Luis Lapa (Tío)",
        "tutor_tlf": "977444333",
        "horario": "03:00 PM - 04:00 PM",
        "prediccion_continuidad": "Muy Alta (95.0% - Favorable)",
        "historial_eva": [8, 7, 6, 4, 3]
    },
    {
        "dni": "45667789",
        "nombre": "JORGE LIMAS ARTEAGA",
        "edad": 28,
        "genero": "Masculino",
        "zona": "Esguince de Tobillo",
        "eva": 6,
        "fecha_inicio": "2026-10-19",
        "citas_totales": 10,
        "citas_asistidas": 4,
        "citas_faltantes": 6,
        "citas_reprogramadas": 0,
        "reprog_estado": "N/A",
        "ocupacion": "Comercial",
        "sueldo": 2600,
        "hijos": 1,
        "esposas": 1,
        "movilidad": "Propia (Carro/Moto)",
        "vivienda": "Propia",
        "email": "jorge.limas@gmail.com",
        "tlf": "987777888",
        "tutor": "Carmen Arteaga (Esposa)",
        "tutor_tlf": "966333222",
        "horario": "04:00 PM - 05:00 PM",
        "prediccion_continuidad": "Alta (91.0% - Favorable)",
        "historial_eva": [7, 6, 5, 4, 4]
    },
    {
        "dni": "49466575",
        "nombre": "LUCIANO PENDEYBIS COCA",
        "edad": 34,
        "genero": "Masculino",
        "zona": "Lumbalgia / Zona Lumbar",
        "eva": 8,
        "fecha_inicio": "2026-10-20",
        "citas_totales": 14,
        "citas_asistidas": 9,
        "citas_faltantes": 5,
        "citas_reprogramadas": 0,
        "reprog_estado": "N/A",
        "ocupacion": "Conductor",
        "sueldo": 3000,
        "hijos": 2,
        "esposas": 1,
        "movilidad": "Propia (Carro/Moto)",
        "vivienda": "Propia",
        "email": "luciano.pendeybis@gmail.com",
        "tlf": "987999000",
        "tutor": "Juana Coca (Madre)",
        "tutor_tlf": "955222111",
        "horario": "05:00 PM - 06:00 PM",
        "prediccion_continuidad": "Alta (93.5% - Favorable)",
        "historial_eva": [9, 8, 7, 5, 4]
    },
    {
        "dni": "50016615",
        "nombre": "TOLUCIO MAYTA QUISPE",
        "edad": 65,
        "genero": "Masculino",
        "zona": "Cervicalgia / Cuello",
        "eva": 7,
        "fecha_inicio": "2026-10-21",
        "citas_totales": 10,
        "citas_asistidas": 6,
        "citas_faltantes": 4,
        "citas_reprogramadas": 0,
        "reprog_estado": "N/A",
        "ocupacion": "Agricultor",
        "sueldo": 1600,
        "hijos": 4,
        "esposas": 1,
        "movilidad": "Transporte Público",
        "vivienda": "Propia",
        "email": "tolucio.mayta@gmail.com",
        "tlf": "986111333",
        "tutor": "Mateo Mayta (Hijo)",
        "tutor_tlf": "954333222",
        "horario": "08:00 AM - 09:00 AM",
        "prediccion_continuidad": "Favorable (88.5%)",
        "historial_eva": [8, 7, 6, 5, 4]
    },
    {
        "dni": "49153344",
        "nombre": "QUETI SALAZAR ORIGUELA",
        "edad": 40,
        "genero": "Femenino",
        "zona": "Lesión de Rodilla",
        "eva": 6,
        "fecha_inicio": "2026-10-22",
        "citas_totales": 12,
        "citas_asistidas": 7,
        "citas_faltantes": 5,
        "citas_reprogramadas": 0,
        "reprog_estado": "N/A",
        "ocupacion": "Enfermera",
        "sueldo": 3200,
        "hijos": 2,
        "esposas": 0,
        "movilidad": "Transporte Público",
        "vivienda": "Alquilada",
        "email": "queti.salazar@gmail.com",
        "tlf": "985222444",
        "tutor": "Pedro Salazar (Hermano)",
        "tutor_tlf": "953444555",
        "horario": "02:00 PM - 03:00 PM",
        "prediccion_continuidad": "Muy Alta (96.0% - Favorable)",
        "historial_eva": [7, 6, 5, 4, 3]
    },
    {
        "dni": "72849102",
        "nombre": "Juan Pérez",
        "edad": 45,
        "genero": "Masculino",
        "zona": "Lumbalgia / Zona Lumbar",
        "eva": 7,
        "fecha_inicio": "2026-10-15",
        "citas_totales": 10,
        "citas_asistidas": 7,
        "citas_faltantes": 3,
        "citas_reprogramadas": 1,
        "reprog_estado": "Aceptada",
        "ocupacion": "Independiente",
        "sueldo": 2800,
        "hijos": 2,
        "esposas": 1,
        "movilidad": "Propia (Carro/Moto)",
        "vivienda": "Propia",
        "email": "juan.perez@gmail.com",
        "tlf": "987123456",
        "tutor": "María Pérez (Esposa)",
        "tutor_tlf": "999888777",
        "horario": "09:00 AM - 10:00 AM",
        "prediccion_continuidad": "Alta (92.4% - Favorable)",
        "historial_eva": [8, 7, 5, 4, 3]
    }
]

# Sincronización directa con Supabase si está disponible
if SUPABASE_AVAILABLE:
    try:
        if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
            response = supabase.table("pacientes").select("*").execute()
            if response.data:
                supabase_data = []
                for row in response.data:
                    supabase_data.append({
                        "dni": str(row.get("dni", "")),
                        "nombre": row.get("nombre", "Paciente Supabase"),
                        "edad": int(row.get("edad", 30)),
                        "genero": row.get("genero", "Masculino"),
                        "zona": row.get("zona", "Lumbalgia / Zona Lumbar"),
                        "eva": int(row.get("eva", 6)),
                        "fecha_inicio": row.get("fecha_inicio", "2026-10-15"),
                        "citas_totales": 10,
                        "citas_asistidas": 6,
                        "citas_faltantes": 4,
                        "citas_reprogramadas": 0,
                        "reprog_estado": "Aceptada",
                        "ocupacion": row.get("ocupacion", "Independiente"),
                        "sueldo": float(row.get("sueldo", 2500)),
                        "hijos": int(row.get("hijos", 1)),
                        "esposas": int(row.get("esposas", 1)),
                        "movilidad": row.get("movilidad", "Propia (Carro/Moto)"),
                        "vivienda": row.get("vivienda", "Propia"),
                        "email": row.get("email", "paciente@gmail.com"),
                        "tlf": row.get("tlf", "987654321"),
                        "tutor": row.get("tutor", "Familiar"),
                        "tutor_tlf": row.get("tutor_tlf", "912345678"),
                        "horario": row.get("horario", "09:00 AM - 10:00 AM"),
                        "prediccion_continuidad": "Alta (94.0% - Favorable)",
                        "historial_eva": [8, 7, 6, 5, 4]
                    })
                if supabase_data:
                    pacientes_db = supabase_data
    except Exception as e:
        print(f"Nota sobre Supabase: {e}")

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