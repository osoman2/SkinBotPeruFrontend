# frontend/main.py
import os
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Aplicación de Detección de Melanoma",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Optional: define a function to load local CSS
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("assets/style.css")

# Sidebar logo
try:
    logo = Image.open("assets/logo.png")
    st.sidebar.image(logo, width=150)
except:
    st.sidebar.write("Logo here")

st.title("Bienvenido a la Aplicación de Detección de Melanoma 🩺")

st.markdown("""
### Detección de Melanoma con Precisión

Esta aplicación permite a los usuarios subir imágenes de la piel para la alerta de examinación para el despistaje de melanoma.
No solo eso! En MELIA ofrecemos un seguimiento de las lesiones detectadas, permitiendo a los pacientes monitorear el progreso y el tratamiento y hacerlo parte del proceso.

Navegación:
- Usa el menú de la izquierda para **Iniciar sesión**, **Subir** una imagen, realizar **Análisis Avanzado**, o ver tu **Historial**.
- Si no tienes una cuenta, regístrate en la sección [Login / Register].
""")

st.markdown("---")
st.markdown("© 2025 Equipo de Detección de Melanoma. Todos los derechos reservados.")
