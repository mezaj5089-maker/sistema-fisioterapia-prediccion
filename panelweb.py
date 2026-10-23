import streamlit as st
import streamlit.components.v1 as components
import os
import joblib
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de página Streamlit
st.set_page_config(
    page_title="Sistema Inteligente de Fisioterapia",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cargar Credenciales de Secrets de Streamlit Cloud
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_PASS = st.secrets.get("GMAIL_APP_PASSWORD", "")

# Función para enviar correo mediante Gmail SMTP
def enviar_correo_confirmacion(destinatario, nombre, riesgo):
    if not GMAIL_USER or not GMAIL_PASS:
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = "Seguimiento Fisioterapéutico y Confirmación de Plan"

        cuerpo = f"""
        Hola {nombre},

        Se ha registrado exitosamente tu evaluación clínica en nuestra plataforma.
        Clasificación de Seguimiento: {riesgo}

        Saludos cordiales,
        Equipo de Fisioterapia y Inferencia Clínica.
        """
        msg.attach(MIMEText(cuerpo, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False

# Cargar y Servir la Interfaz Web (static/index.html)
def cargar_interfaz_web():
    path_html = os.path.join(os.path.dirname(__file__), "static", "index.html")
    path_css = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    path_js = os.path.join(os.path.dirname(__file__), "static", "app.js")

    if os.path.exists(path_html):
        with open(path_html, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Inyectar CSS directamente para renderizado fluido
        if os.path.exists(path_css):
            with open(path_css, "r", encoding="utf-8") as f_css:
                css_content = f_css.read()
                html_content = html_content.replace(
                    '<link rel="stylesheet" href="styles.css">',
                    f'<style>{css_content}</style>'
                )

        # Inyectar JS directamente
        if os.path.exists(path_js):
            with open(path_js, "r", encoding="utf-8") as f_js:
                js_content = f_js.read()
                html_content = html_content.replace(
                    '<script src="app.js"></script>',
                    f'<script>{js_content}</script>'
                )

        components.html(html_content, height=920, scrolling=True)
    else:
        st.error("No se encontró la carpeta 'static/index.html'. Verifique la estructura del proyecto.")

if __name__ == "__main__":
    cargar_interfaz_web()