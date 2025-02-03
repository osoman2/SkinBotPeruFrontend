# pages/2_Advanced_Analysis_and_Listing.py
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Análisis Avanzado y Listado",
    layout="wide",
    initial_sidebar_state="auto"
)

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Archivo CSS no encontrado: {file_name}")

load_css("./assets/style.css")

def decode_base64_image(image_b64: str) -> Image.Image:
    try:
        image_bytes = base64.b64decode(image_b64)
        return Image.open(BytesIO(image_bytes))
    except Exception as e:
        st.error(f"❌ Error al decodificar la imagen: {e}")
        return None

def fetch_segmented_image(image_id):
    try:
        resp = requests.get(f"{BASE_URL}/get_segmented_image/{image_id}", timeout=30)
        if resp.status_code == 200:
            image_data = resp.json()
            seg_b64 = image_data.get("segmented_image_b64", None)
            if seg_b64:
                image = decode_base64_image(seg_b64)
                return image
            else:
                st.warning(f"No se encontró la imagen segmentada para el ID {image_id}.")
                return None
        else:
            st.error(f"❌ Falló al obtener la imagen segmentada. Status: {resp.status_code}")
            return None
    except requests.RequestException as e:
        st.error(f"❌ Error al obtener la imagen segmentada: {e}")
        return None

st.title("🔍 Análisis Avanzado y Listado")
st.markdown("### Realiza Análisis Avanzados y Visualiza Resultados Complejos")

# Sección de Análisis Avanzado
# pages/2_Advanced_Analysis_and_Listing.py

# pages/2_Advanced_Analysis_and_Listing.py

st.header("Análisis Avanzado de Respaldo")

adv_username = st.text_input("Nombre de usuario para Análisis Avanzado", placeholder="ej. juan_perez")

# Opciones limitadas para la parte del cuerpo
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
selected_body_part_filter = st.selectbox(
    "Parte del cuerpo (opcional para filtrar)",
    options=body_part_options,
    index=len(body_part_options)-1
)

body_part_filter = None
if selected_body_part_filter == "Otra":
    custom_part = st.text_input("Describe la parte del cuerpo")
    if custom_part:
        body_part_filter = custom_part
elif selected_body_part_filter == "No especificar":
    body_part_filter = None
else:
    body_part_filter = selected_body_part_filter


if st.button("🛠️ Iniciar Análisis Avanzado"):
    if not adv_username:
        st.warning("⚠️ Se requiere el nombre de usuario para el análisis avanzado.")
    else:
        # Construir el payload
        payload = {"username": adv_username}
        if body_part_filter:
            payload["body_part"] = body_part_filter

        with st.spinner("Realizando análisis avanzado..."):
            try:
                adv_resp = requests.post(
                    f"{BASE_URL}/start_process", 
                    json=payload, 
                    timeout=60
                )

                if adv_resp.status_code == 200:
                    adv_data = adv_resp.json()
                    st.success("✅ ¡Análisis avanzado completado!")

                    # Tomamos la recomendación general
                    overall_recommendation = adv_data.get("overall_recommendation", "No hay recomendación disponible.")
                    st.markdown(f"**Recomendación General**: `{overall_recommendation}`")

                    # Analizamos cada item en 'analysis'
                    st.markdown("### Análisis Detallado")
                    analysis_list = adv_data.get("analysis", [])

                    for analysis in analysis_list:
                        # Extrae cada campo
                        image_id = analysis.get("image_id", "N/A")
                        asymmetry = analysis.get("asymmetry", "N/A")
                        border_irregularity = analysis.get("border_irregularity", "N/A")
                        color_variegation = analysis.get("color_variegation", "N/A")
                        diameter_assessment = analysis.get("diameter_assessment", "N/A")
                        evolution_assessment = analysis.get("evolution_assessment", "N/A")
                        segmentation_analysis = analysis.get("segmentation_analysis", "N/A")
                        extra_info_influence = analysis.get("extra_info_influence", "N/A")
                        image_technical_commentaries = analysis.get("image_technical_commentaries", "N/A")
                        other_diagnoses = analysis.get("other_diagnoses", "N/A")
                        final_decision = analysis.get("final_decision", "N/A")
                        confidence_level = analysis.get("confidence_level", "N/A")

                        # Expander por cada imagen
                        with st.expander(f"📄 Análisis para ID de Imagen: {image_id}", expanded=False):
                            st.markdown(f"**Asimetría**: {asymmetry}")
                            st.markdown(f"**Irregularidad del Borde**: {border_irregularity}")
                            st.markdown(f"**Variegación del Color**: {color_variegation}")
                            st.markdown(f"**Evaluación del Diámetro**: {diameter_assessment}")
                            st.markdown(f"**Evaluación de la Evolución**: {evolution_assessment}")

                            # Mostrar los nuevos campos
                            st.markdown(f"**Análisis de segmentación**: {segmentation_analysis}")
                            st.markdown(f"**Comentarios Técnicos**: {image_technical_commentaries}")
                            st.markdown(f"**Información Extra de Influencia**: {extra_info_influence}")
                            st.markdown(f"**Otros Diagnósticos Posibles**: {other_diagnoses}")

                            st.markdown(f"**Decisión Final**: `{final_decision}`")
                            st.markdown(f"**Nivel de Confianza**: `{confidence_level}`")

                            # Cargar la imagen segmentada (si existe)
                            segmented_image = fetch_segmented_image(image_id)
                            if segmented_image:
                                st.markdown("**Imagen Segmentada**:")
                                st.image(segmented_image, caption=f"Imagen Segmentada {image_id}", use_container_width=True)
                            else:
                                st.warning("Imagen segmentada no disponible.")
                else:
                    st.error(f"❌ Error {adv_resp.status_code}: {adv_resp.text}")

            except requests.RequestException as e:
                st.error(f"❌ Error al conectar con el servidor: {e}")
st.markdown("---")

# Sección de Listado de Usuarios e Imágenes
st.header("📄 Listar Todos los Usuarios e Imágenes")

if st.button("📥 Obtener Todos los Usuarios e Imágenes"):
    with st.spinner("Obteniendo datos..."):
        response = requests.get(f"{BASE_URL}/list_users_with_images")
        if response.status_code == 200:
            data = response.json()
            
            for user_info in data:
                username = user_info.get("username", "N/A")
                body_parts = user_info.get("body_parts", [])

                # 1er nivel: Expander por usuario
                with st.expander(f"👤 Usuario: {username}", expanded=False):
                    if not body_parts:
                        st.info("No hay imágenes para este usuario.")
                    else:
                        # Sin segundo expander: en su lugar, directamente se muestra
                        for bp_data in body_parts:
                            bp_name = bp_data.get("body_part", "N/A")
                            st.subheader(f"Parte del cuerpo: {bp_name}")
                            
                            # Lista de imágenes
                            for img in bp_data.get("images", []):
                                image_id = img.get("image_id", "N/A")
                                st.markdown(f"**ID de Imagen**: `{image_id}`")
                                st.markdown(f"**Hora de Subida**: {img.get('upload_time', 'N/A')}")

                                # Mostrar la imagen original
                                image_b64 = img.get("image_b64", None)
                                if image_b64:
                                    st.image(base64.b64decode(image_b64), caption="Imagen Original")

                                # Mostrar la imagen segmentada
                                seg_b64 = img.get("segmented_image_b64", None)
                                if seg_b64:
                                    st.image(base64.b64decode(seg_b64), caption="Imagen Segmentada")

                                # Mostrar fallback_result (no lo metemos en otro expander)
                                fallback_result = img.get("fallback_result", {})
                                if fallback_result:
                                    st.markdown("**Análisis Detallado**:")
                                    st.json(fallback_result)
                                
                                st.markdown("---")  # Separador
        else:
            st.error(f"Error {response.status_code}: {response.text}")

st.markdown("---")


if st.button("Ver Análisis Guardados"):
    with st.spinner("Obteniendo lista de análisis..."):
        resp = requests.get(f"{BASE_URL}/list_analyses", timeout=60)
        if resp.status_code == 200:
            analyses = resp.json()
            if not analyses:
                st.info("No hay análisis guardados.")
            else:
                for idx, analysis_doc in enumerate(analyses, start=1):
                    st.subheader(f"Análisis #{idx}")
                    st.write(f"Usuario: {analysis_doc['username']}")
                    st.write(f"Parte del cuerpo: {analysis_doc.get('body_part', 'N/A')}")
                    st.write(f"Fecha del análisis: {analysis_doc['analysis_date']}")
                    st.write(f"Recomendación global: {analysis_doc['overall_recommendation']}")
                    
                    # Expandir para ver el array "analysis"
                    st.write("**Resultados detallados**:")
                    for item in analysis_doc["analysis"]:
                        st.json(item)
                    st.markdown("---")
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")
