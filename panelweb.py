import os
import streamlit as st
import streamlit.components.v1 as components

# Configuración del panel de Streamlit
st.set_page_config(
    page_title="Sistema Fisioterapia - Predicción",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ruta a la carpeta estática
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def load_frontend():
    """Lee el archivo HTML, inyecta el CSS y JS desde la carpeta static."""
    html_path = os.path.join(STATIC_DIR, "index.html")
    css_path = os.path.join(STATIC_DIR, "styles.css")
    js_path = os.path.join(STATIC_DIR, "app.js")

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    with open(js_path, "r", encoding="utf-8") as f:
        js_content = f.read()

    # Inyección limpia de CSS y JS en la plantilla HTML
    full_html = html_content.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>{css_content}</style>'
    ).replace(
        '<script src="app.js"></script>',
        f'<script>{js_content}</script>'
    )
    
    return full_html

# Barra lateral (Sidebar) para control y autenticación
st.sidebar.title("Menú de Administración")
password = st.sidebar.text_input("Contraseña de Acceso", type="password")

if password == "admin123":  # Ajusta tu contraseña
    st.sidebar.success("Acceso concedido")
    
    # Cargar frontend modular
    dashboard_html = load_frontend()
    components.html(dashboard_html, height=1000, scrolling=True)
else:
    st.warning("🔒 Ingrese la contraseña de administrador en la barra lateral para acceder.")