import os
import streamlit as st
import streamlit.components.v1 as components

# Configuración del panel de Streamlit
st.set_page_config(
    page_title="Sistema Fisioterapia - Predicción",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Obtener la ruta absoluta del directorio del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def load_frontend():
    """Lee el archivo HTML e inyecta CSS y JS desde la carpeta static."""
    html_path = os.path.join(STATIC_DIR, "index.html")
    css_path = os.path.join(STATIC_DIR, "styles.css")
    js_path = os.path.join(STATIC_DIR, "app.js")

    # Verificar que los archivos existan antes de abrir
    if not os.path.exists(html_path):
        st.error(f"No se encontró el archivo HTML en: {html_path}")
        return ""

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    js_content = ""
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

    # Inyección de estilos y scripts dentro del HTML
    full_html = html_content.replace(
        '</head>',
        f'<style>{css_content}</style></head>'
    ).replace(
        '</body>',
        f'<script>{js_content}</script></body>'
    )
    
    return full_html

# Barra lateral (Sidebar) para control y autenticación
st.sidebar.title("Menú de Administración")
password = st.sidebar.text_input("Contraseña de Acceso", type="password")

if password == "admin123":
    st.sidebar.success("Acceso concedido")
    
    dashboard_html = load_frontend()
    if dashboard_html:
        components.html(dashboard_html, height=1000, scrolling=True)
else:
    st.warning("🔒 Ingrese la contraseña de administrador en la barra lateral para acceder.")