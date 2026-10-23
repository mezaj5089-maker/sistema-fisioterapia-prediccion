import streamlit as st
import streamlit.components.v1 as components
import os
import joblib
import pandas as pd

# Configuración estricta de página a pantalla completa (Wide Mode)
st.set_page_config(
    page_title="KineData Analytics - Fisioterapia e Inferencia IA",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS globales de Streamlit para eliminar padding por defecto
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

# Carga segura del modelo predictivo Serializado (Machine Learning)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_fisioterapia.pkl")
ml_model = None
try:
    if os.path.exists(MODEL_PATH):
        ml_model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Aviso de carga de modelo ML: {e}")

def main_engine():
    base_dir = os.path.dirname(__file__)
    path_html = os.path.join(base_dir, "static", "index.html")
    path_css = os.path.join(base_dir, "static", "styles.css")
    path_js = os.path.join(base_dir, "static", "app.js")

    if os.path.exists(path_html):
        with open(path_html, "r", encoding="utf-8") as f_html:
            html_content = f_html.read()

        # Inyección avanzada de CSS externo
        if os.path.exists(path_css):
            with open(path_css, "r", encoding="utf-8") as f_css:
                css_content = f_css.read()
                html_content = html_content.replace(
                    '<link rel="stylesheet" href="styles.css">',
                    f'<style>{css_content}</style>'
                )

        # Inyección de JavaScript principal del cliente
        if os.path.exists(path_js):
            with open(path_js, "r", encoding="utf-8") as f_js:
                js_content = f_js.read()
                html_content = html_content.replace(
                    '<script src="app.js"></script>',
                    f'<script>{js_content}</script>'
                )

        # Renderizado del DOM completo optimizado
        components.html(html_content, height=1000, scrolling=True)
    else:
        st.error("Error crítico: No se encuentra el archivo 'static/index.html'. Verifique su repositorio en GitHub.")

if __name__ == "__main__":
    main_engine()