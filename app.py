import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración a pantalla completa (Wide Mode)
st.set_page_config(
    page_title="Sistema Clínico de Fisioterapia e Inferencia IA",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Eliminar todos los márgenes y paddings por defecto de Streamlit mediante CSS inyectado
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

def cargar_interfaz():
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
                html_content = html_content.replace(
                    '<script src="app.js"></script>',
                    f'<script>{js_content}</script>'
                )

        components.html(html_content, height=1000, scrolling=True)
    else:
        st.error("No se encontró 'static/index.html'. Verifique la estructura del repositorio.")

if __name__ == "__main__":
    cargar_interfaz()