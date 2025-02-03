# main.py
import streamlit as st
from PIL import Image
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="Aplicación de Detección de Melanoma",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# def check_server_health():
#     try:
#         response = requests.get(f"{BASE_URL}/healthz", timeout=5)
#         if response.status_code == 200:
#             return True
#         else:
#             return False
#     except requests.RequestException:
#         return False
    
# Función para cargar CSS local
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Cargar el CSS
load_css("assets/style.css")

# Cargar y mostrar el logo
logo = Image.open("assets/logo.png")
st.sidebar.image(logo, width=150)

# Título de la Aplicación
st.title("Bienvenido a la Aplicación de Detección de Melanoma 🩺")

# Introducción
st.markdown("""
### Detección de Melanoma con Precisión

Esta aplicación permite a los usuarios subir imágenes de la piel para la detección de melanoma y realizar análisis avanzados sobre los datos procesados.

Usa la barra lateral para navegar entre las funcionalidades disponibles:
- **Subir y Segmentar**: Sube tu imagen de la piel y obtén resultados de segmentación y clasificación.
- **Análisis Avanzado y Listado**: Realiza análisis avanzados y visualiza todos los datos de los usuarios.
""")


# if st.button('Check Server Health'):
#     is_healthy = check_server_health()
#     if is_healthy:
#         st.success('✅ Server is up and running!')
#     else:
#         st.error('❌ Server is down or unresponsive.')
# Pie de Página
st.markdown("---")
st.markdown("© 2025 Equipo de Detección de Melanoma. Todos los derechos reservados.")
