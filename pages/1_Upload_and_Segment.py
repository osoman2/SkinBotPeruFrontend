import streamlit as st
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime
import base64
from streamlit_js_eval import streamlit_js_eval
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Subir y Segmentar",
    layout="wide",
    initial_sidebar_state="auto"
)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("./assets/style.css")

st.title("🖼️ Subir y Segmentar")
st.markdown("### Sube una imagen para la detección y segmentación de melanoma")

username = st.text_input("Nombre de usuario", placeholder="ej. juan_perez")
age = st.number_input("Edad (opcional)", min_value=0, max_value=120, value=0, step=1)

# 1) Lista cerrada de partes del cuerpo
body_part_options = [
    "Brazo izquierdo",
    "Brazo derecho",
    "Tórax",
    "Espalda",
    "Pierna izquierda",
    "Pierna derecha",
    "Cuello",
    "Cabeza/Cara",
    "Otra",            # <-- Para permitir un texto libre
    "No especificar"   # <-- Por si el usuario no quiere dar info
]

selected_body_part = st.selectbox("Seleccione la parte del cuerpo", options=body_part_options, index=len(body_part_options)-1)

# 2) Si el usuario elige "Otra", mostramos un input adicional
body_part = None
if selected_body_part == "Otra":
    body_part_custom = st.text_input("Describe la parte del cuerpo")
    if body_part_custom:
        body_part = body_part_custom
elif selected_body_part == "No especificar":
    body_part = None
else:
    body_part = selected_body_part

diameter_larger_than_pencil = st.checkbox("¿Crees que el diámetro supera el grosor de un lápiz?")

# Obtener geolocalización del navegador
location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition", key="get_location")

geolocation_city = st.text_input("Ciudad (opcional)")
geolocation_region = st.text_input("Región (opcional)")

geolocation_lat = None
geolocation_lon = None

if location:
    geolocation_lat = location.coords.latitude
    geolocation_lon = location.coords.longitude

    # Realizar geocodificación inversa para obtener ciudad y región
    try:
        response = requests.get(f'https://ipapi.co/{geolocation_lat},{geolocation_lon}/json/')
        if response.status_code == 200:
            data = response.json()
            geolocation_city = data.get('city', '')
            geolocation_region = data.get('region', '')
    except requests.RequestException as e:
        st.error(f"Error al obtener la ubicación: {e}")

additional_comment = st.text_area("Comentario adicional (opcional)", help="¿Sientes picazón, cambio de color, etc.?")
selected_date = st.date_input("Fecha de subida (opcional)", value=datetime.now().date())
selected_time = st.time_input("Hora de subida (opcional)", value=datetime.now().time())
timestamp = datetime.combine(selected_date, selected_time) if selected_date and selected_time else None

uploaded_file = st.file_uploader("Selecciona una imagen (JPG o PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="🖼️ Imagen original subida", use_container_width=True, clamp=True)

if st.button("🚀 Enviar para segmentación y clasificación"):
    if not username:
        st.warning("⚠️ Por favor, ingresa un nombre de usuario.")
    elif not uploaded_file:
        st.warning("⚠️ Por favor, sube una imagen.")
    else:
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }
        data = {
            "username": username,
            "age": str(age) if age else "",
            "body_part": body_part if body_part else "",
            "diameter_larger_than_pencil": str(diameter_larger_than_pencil),
            "geolocation_city": geolocation_city,
            "geolocation_region": geolocation_region,
            "geolocation_lat": geolocation_lat,
            "geolocation_lon": geolocation_lon,
            "additional_comment": additional_comment
        }

        if timestamp:
            data["timestamp"] = timestamp.isoformat()

        with st.spinner("Procesando..."):
            try:
                resp = requests.post(f"{BASE_URL}/upload_image", files=files, data=data, timeout=60)
                if resp.status_code == 200:
                    result_json = resp.json()
                    st.success("✅ ¡Imagen procesada exitosamente!")
                    
                    first_class = result_json.get("first_classification", "N/A")
                    seg_result = result_json.get("segmentation_result", {})
                    seg_b64 = result_json.get("segmented_image_b64", None)

                    st.markdown(f"**Primera clasificación**: `{first_class}`")
                    with st.expander("🔍 Ver segmentación JSON", expanded=False):
                        st.json(seg_result)

                    if seg_b64:
                        overlay_bytes = base64.b64decode(seg_b64)
                        overlay_img = Image.open(BytesIO(overlay_bytes))
                        st.image(
                            overlay_img,
                            caption="🖌️ Imagen segmentada",
                            use_container_width=True,
                            clamp=True
                        )
                else:
                    st.error(f"❌ Error {resp.status_code}: {resp.text}")
            except requests.RequestException as e:
                st.error(f"❌ Error al conectar con el servidor: {e}")
