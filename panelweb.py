import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import base64
import datetime
from datetime import date, timedelta
import plotly.express as px
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Fisioterapia Predictiva",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------------------------------------
# CARGA DE IMAGEN LOCAL FISIO.PNG
# ---------------------------------------------------------
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_b64 = get_base64_image("fisio.png")

# Inyección limpia de CSS sin imprimir texto en pantalla
if img_b64:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(244, 247, 246, 0.88), rgba(244, 247, 246, 0.92)), url("data:image/png;base64,{img_b64}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <style>
    /* Títulos principales */
    h1, h2, h3 {
        color: #1A365D !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 700;
    }

    /* Reloj Digital Esmeralda */
    .reloj-box {
        background-color: #007A60;
        color: white;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 122, 96, 0.25);
        margin-bottom: 15px;
    }
    .reloj-box h2 {
        color: white !important;
        margin: 4px 0 0 0;
        font-size: 26px;
        letter-spacing: 1px;
    }
    .reloj-box small {
        color: #D1FAE5;
        font-weight: 600;
    }

    /* Tarjetas traslúcidas */
    div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.90);
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #E2E8F0;
    }

    /* Botones */
    .stButton>button {
        background-color: #2B6CB0;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.2rem;
    }
    .stButton>button:hover {
        background-color: #2C5282;
    }
    </style>
    """,
    unsafe_allow_html=True
)