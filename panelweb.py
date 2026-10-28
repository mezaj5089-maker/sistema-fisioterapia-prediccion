import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="KineData Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar elementos de la interfaz nativa de Streamlit
st.markdown("""
    <style>
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def load_modular_web():
    html_path = os.path.join(STATIC_DIR, "index.html")
    css_path = os.path.join(STATIC_DIR, "styles.css")
    js_path = os.path.join(STATIC_DIR, "app.js")
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    with open(js_path, "r", encoding="utf-8") as f:
        js_content = f.read()
        
    full_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>{css_content}</style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    </head>
    <body>
        {html_content}
        <script>{js_content}</script>
    </body>
    </html>
    """
    components.html(full_code, height=950, scrolling=True)

if __name__ == "__main__":
    load_modular_web()