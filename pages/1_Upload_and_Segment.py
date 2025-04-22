# frontend/pages/1_Upload_and_Segment.py
import streamlit as st
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime
import base64
from streamlit_js_eval import streamlit_js_eval
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Subir y Segmentar",
    layout="wide",
    initial_sidebar_state="auto"
)

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass

load_css("./assets/style.css")

# Check if user is logged in
if "access_token" not in st.session_state or not st.session_state["access_token"]:
    st.warning("Necesitas iniciar sesión antes de subir imágenes.")
    st.stop()

st.title("🖼️ Subir y Segmentar")
st.markdown("### Sube una imagen para la detección y segmentación de melanoma")

token = st.session_state["access_token"]
username_state = st.session_state["logged_in_user"]

col_left, col_right = st.columns(2)

with col_left:
    # Data about the user / lesion
    st.subheader("Datos de la Lesión")
    st.write(f"Usuario actual: `{username_state}` (solo puedes subir para tu cuenta).")
    age = st.number_input("Edad (opcional)", min_value=0, max_value=120, value=30, step=1)

    body_part_options = [
        "Brazo izquierdo",
        "Brazo derecho",
        "Tórax",
        "Espalda",
        "Pierna izquierda",
        "Pierna derecha",
        "Cuello",
        "Cabeza/Cara",
        "Otra",
        "No especificar"
    ]
    selected_body_part = st.selectbox("Parte del cuerpo", options=body_part_options, index=len(body_part_options)-1)
    if selected_body_part == "Otra":
        body_part_custom = st.text_input("Describe la parte del cuerpo")
        body_part = body_part_custom if body_part_custom else "Otra"
    elif selected_body_part == "No especificar":
        body_part = ""
    else:
        body_part = selected_body_part

    diameter_larger_than_pencil = st.checkbox(
        "¿Diámetro supera ~6 mm (grosor de un lápiz)?",
        help="Puede usar un lápiz o un objeto similar para estimar el diámetro."
    )

with col_right:
    st.subheader("Ubicación y Comentarios")
    location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition", key="get_location")

    geolocation_city = st.text_input("Ciudad (opcional)")
    geolocation_region = st.text_input("Región (opcional)")
    additional_comment = st.text_area("Comentario adicional (opcional)", help="¿Sientes picazón, cambio de color, etc.?")

    # Timestamp if you want
    selected_date = st.date_input("Fecha de subida (opcional)", value=datetime.now().date())
    selected_time = st.time_input("Hora de subida (opcional)", value=datetime.now().time())
    timestamp = datetime.combine(selected_date, selected_time) if selected_date and selected_time else None

    geolocation_lat = None
    geolocation_lon = None
    if location:
        geolocation_lat = location.coords.latitude
        geolocation_lon = location.coords.longitude

# File upload
uploaded_file = st.file_uploader("Selecciona una imagen (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="🖼️ Imagen original subida", use_container_width=True, clamp=True)

def delete_image(image_id: str, headers: dict) -> bool:
    try:
        resp = requests.delete(
            f"{BASE_URL}/delete_image/{image_id}",
            headers=headers,
            timeout=30
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False

if st.button("🚀 Enviar para segmentación y clasificación"):
    if not username_state:
        st.warning("⚠️ Usuario no definido.")
    elif not uploaded_file:
        st.warning("⚠️ Por favor, sube una imagen.")
    else:
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }
        data = {
            "username": username_state,
            "age": str(age) if age else "",
            "body_part": body_part,
            "diameter_larger_than_pencil": str(diameter_larger_than_pencil),
            "geolocation_city": geolocation_city,
            "geolocation_region": geolocation_region,
            "geolocation_lat": geolocation_lat,
            "geolocation_lon": geolocation_lon,
            "additional_comment": additional_comment
        }
        if timestamp:
            data["timestamp"] = timestamp.isoformat()

        headers = {"Authorization": f"Bearer {token}"}

        with st.spinner("Procesando..."):
            try:
                resp = requests.post(f"{BASE_URL}/upload_image", files=files, data=data, headers=headers, timeout=60)
                if resp.status_code == 200:
                    result_json = resp.json()
                    st.success("✅ ¡Imagen procesada exitosamente!")
                    
                    image_id = result_json.get("id")
                    col1, col2 = st.columns([0.9, 0.1])
                    
                    with col1:
                        first_class = result_json.get("first_classification", "N/A")
                        st.markdown(f"**Primera clasificación**: `{first_class}`")
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_new_img_{image_id}", help="Delete this image"):
                            if st.warning("⚠️ Are you sure you want to delete this image?"):
                                if delete_image(image_id, headers):
                                    st.success("Image deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete image")
                    
                    seg_result = result_json.get("segmentation_result", {})
                    seg_b64 = result_json.get("segmented_image_b64", None)

                    # with st.expander("🔍 Ver segmentación JSON", expanded=False):
                    #     st.json(seg_result)

                    if seg_b64:
                        overlay_bytes = base64.b64decode(seg_b64)
                        overlay_img = Image.open(BytesIO(overlay_bytes))
                        st.image(
                            overlay_img,
                            caption="🖌️ Imagen segmentada",
                            use_container_width=True,
                            clamp=True
                        )
                elif resp.status_code == 400:
                    # Possibly daily limit or other validation
                    detail = resp.json().get("detail", "Error desconocido.")
                    st.error(f"❌ {detail}")
                else:
                    st.error(f"❌ Error {resp.status_code}: {resp.text}")
            except requests.RequestException as e:
                st.error(f"❌ Error al conectar con el servidor: {e}")
