# frontend/main.py
import os
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Evaluación Preventiva de manchas cutáneas",
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

st.title("Bienvenido a MELIA: Evaluación Preventiva de manchas cutáneas 🩺")

st.markdown("""
### Evaluación Preventiva con Tecnología de IA

MELIA es una herramienta de apoyo para la evaluación preventiva de manchas cutáneas. 
⚠️ **Importante**: Esta herramienta NO realiza diagnósticos médicos y no sustituye la evaluación profesional.

Lo que ofrecemos:
- Análisis preliminar asistido por IA de imágenes de manchas cutáneas
- Seguimiento temporal de cambios en las manchas
- Recomendaciones para el cuidado preventivo de la piel

Navegación:
- Usa el menú de la izquierda para **Iniciar sesión**, **Subir** una imagen, realizar una **Evaluación Preventiva**, o ver tu **Historial**.
- Si no tienes una cuenta, regístrate en la sección [Login / Register].

💡 **Recuerda**: La mejor prevención es la revisión regular con un profesional de la salud.
""")

st.markdown("---")
st.markdown("© 2025 Equipo MELIA. Todos los derechos reservados.")
