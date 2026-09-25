import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from supabase import create_client, Client

# Configuración de Streamlit
st.set_page_config(
    page_title="KineData Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu, header, footer { visibility: hidden; }
        .block-container { padding: 0rem !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# Conexión a Supabase
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def load_modular_web():
    html_path = os.path.join(STATIC_DIR, "index.html")
    css_path = os.path.join(STATIC_DIR, "styles.css")
    js_path = os.path.join(STATIC_DIR, "app.js")

    if not os.path.exists(html_path):
        st.error("No se encontró la carpeta static/index.html")
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

    # Inyección limpia
    full_html = html_content.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>{css_content}</style>'
    ).replace(
        '<script src="app.js"></script>',
        f'<script>{js_content}</script>'
    )
    return full_html

web_content = load_modular_web()
if web_content:
    components.html(web_content, height=960, scrolling=True)