# frontend/pages/2_Advanced_Analysis_and_Listing.py
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(page_title="Análisis Avanzado", layout="wide")

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass

load_css("./assets/style.css")

if "access_token" not in st.session_state or not st.session_state["access_token"]:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    st.stop()

token = st.session_state["access_token"]
username_state = st.session_state["logged_in_user"]

st.title("🔍 Análisis Avanzado")

# Small ABCDE guidance
with st.expander("¿Qué es la regla ABCDE?", expanded=False):
    st.markdown("""
    **A - Asimetría**: Lesiones que no sean uniformes en forma.<br>
    **B - Borde**: Bordes irregulares, dentados o mal definidos.<br>
    **C - Color**: Varias tonalidades, incluyendo marrón, negro, rojo, azul o blanco.<br>
    **D - Diámetro**: Mayor de 6 mm.<br>
    **E - Evolución**: Cambios en el tiempo (tamaño, forma, color, elevación o síntomas).<br>
    """, unsafe_allow_html=True)

st.subheader("Iniciar Análisis Avanzado de Respaldo")

col1, col2 = st.columns(2)

with col1:
    adv_username = st.text_input(
        "Nombre de usuario para Análisis Avanzado",
        value=username_state,
        help="Por defecto tu propio usuario; si eres admin, podrías analizar otro usuario"
    )

with col2:
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
        "Parte del cuerpo (opcional)",
        options=body_part_options,
        index=len(body_part_options)-1
    )

    body_part_filter = ""
    if selected_body_part_filter == "Otra":
        custom_part = st.text_input("Describe la parte del cuerpo")
        body_part_filter = custom_part if custom_part else ""
    elif selected_body_part_filter != "No especificar":
        body_part_filter = selected_body_part_filter

if st.button("🛠️ Iniciar Análisis Avanzado"):
    if not adv_username:
        st.warning("⚠️ Se requiere el nombre de usuario para el análisis avanzado.")
    else:
        payload = {"username": adv_username}
        if body_part_filter:
            payload["body_part"] = body_part_filter

        with st.spinner("Realizando análisis avanzado..."):
            try:
                headers = {"Authorization": f"Bearer {token}"}
                adv_resp = requests.post(
                    f"{BASE_URL}/start_process", 
                    json=payload, 
                    headers=headers,
                    timeout=60
                )

                if adv_resp.status_code == 200:
                    adv_data = adv_resp.json()
                    st.success("✅ ¡Análisis avanzado completado!")

                    overall_recommendation = adv_data.get("overall_recommendation", "No hay recomendación disponible.")
                    st.markdown(f"**Recomendación General**: `{overall_recommendation}`")

                    st.markdown("### Análisis Detallado")
                    analysis_list = adv_data.get("analysis", [])

                    for analysis in analysis_list:
                        image_id = analysis.get("image_id", "N/A")
                        with st.expander(f"📄 Análisis para ID de Imagen: {image_id}", expanded=False):
                            st.markdown(f"**Asimetría**: {analysis.get('asymmetry', '')}")
                            st.markdown(f"**Irregularidad del Borde**: {analysis.get('border_irregularity', '')}")
                            st.markdown(f"**Variegación del Color**: {analysis.get('color_variegation', '')}")
                            st.markdown(f"**Evaluación del Diámetro**: {analysis.get('diameter_assessment', '')}")
                            st.markdown(f"**Evaluación de la Evolución**: {analysis.get('evolution_assessment', '')}")
                            st.markdown(f"**Análisis de segmentación**: {analysis.get('segmentation_analysis', '')}")
                            st.markdown(f"**Información Extra**: {analysis.get('extra_info_influence', '')}")
                            st.markdown(f"**Comentarios Técnicos**: {analysis.get('image_technical_commentaries', '')}")
                            st.markdown(f"**Otros Diagnósticos**: {analysis.get('other_diagnoses', '')}")
                            st.markdown(f"**Decisión Final**: `{analysis.get('final_decision', '')}`")
                            st.markdown(f"**Nivel de Confianza**: `{analysis.get('confidence_level', '')}`")

                            # Attempt to fetch segmented image
                            try:
                                r_img = requests.get(f"{BASE_URL}/get_segmented_image/{image_id}", headers=headers, timeout=30)
                                if r_img.status_code == 200:
                                    image_data = r_img.json()
                                    seg_b64 = image_data.get("segmented_image_b64")
                                    if seg_b64:
                                        seg_img = Image.open(BytesIO(base64.b64decode(seg_b64)))
                                        st.image(seg_img, caption=f"Imagen Segmentada {image_id}")
                                    else:
                                        st.info("No se encontró la imagen segmentada.")
                                else:
                                    st.error(f"Error {r_img.status_code} al obtener imagen segmentada")
                            except requests.RequestException as e:
                                st.error(f"Error al obtener la imagen segmentada: {e}")

                else:
                    st.error(f"❌ Error {adv_resp.status_code}: {adv_resp.text}")

            except requests.RequestException as e:
                st.error(f"❌ Error al conectar con el servidor: {e}")

st.markdown("---")

st.info("Si deseas ver todas tus imágenes y resultados, revisa la página de Historial.")
