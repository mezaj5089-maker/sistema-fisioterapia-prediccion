import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Inicializa la conexión con Supabase usando Secrets de Streamlit o el archivo .env."""
    url = None
    key = None
    
    # 1. Intentar cargar desde secretos de Streamlit
    try:
        import streamlit as st
        if "supabase" in st.secrets:
            url = st.secrets["supabase"]["SUPABASE_URL"]
            key = st.secrets["supabase"]["SUPABASE_KEY"]
    except Exception:
        pass
        
    # 2. Si no existen secretos de Streamlit, usar variables de entorno .env
    if not url or not key:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
    if not url or not key:
        raise ValueError("No se encontraron las credenciales SUPABASE_URL y SUPABASE_KEY en .env o secrets.toml")
        
    return create_client(url, key)

def obtener_datos_gold() -> pd.DataFrame:
    """Consulta la vista Gold desde Supabase."""
    supabase = get_supabase_client()
    response = supabase.table("gold_fisioterapia_features").select("*").execute()
    return pd.DataFrame(response.data)

def buscar_paciente_por_id(id_paciente: str):
    """Consulta un paciente específico por su ID."""
    supabase = get_supabase_client()
    response = supabase.table("gold_fisioterapia_features").select("*").eq("id_paciente", id_paciente).execute()
    return response.data