# frontend/pages/2_Advanced_Analysis_and_Listing.py
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os
from datetime import datetime

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

# --- No changes needed in these functions ---
def delete_analysis(analysis_id: str, headers: dict) -> bool:
    # ... (keep existing implementation)
    try:
        resp = requests.delete(
            f"{BASE_URL}/delete_analysis/{analysis_id}",
            headers=headers,
            timeout=30
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False

def display_analysis_details(analysis):
    """Función para mostrar los detalles del análisis"""
    if not analysis or not isinstance(analysis, dict): # Added type check
        st.warning("No analysis details available or format is incorrect.")
        return

    # ABCDE criteria
    st.subheader("Criterios ABCDE")
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"**A - Asimetría**: {analysis.get('asymmetry', 'N/A')}") # Added default N/A
        st.markdown(f"**B - Irregularidad del Borde**: {analysis.get('border_irregularity', 'N/A')}")
    with cols[1]:
        st.markdown(f"**C - Variegación del Color**: {analysis.get('color_variegation', 'N/A')}")
        st.markdown(f"**D - Evaluación del Diámetro**: {analysis.get('diameter_assessment', 'N/A')}")
    with cols[2]:
        st.markdown(f"**E - Evaluación de la Evolución**: {analysis.get('evolution_assessment', 'N/A')}")

    # Technical Analysis
    st.subheader("Análisis Técnico")
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**Análisis de Segmentación**: {analysis.get('segmentation_analysis', 'N/A')}")
        st.markdown(f"**Comentarios Técnicos**: {analysis.get('image_technical_commentaries', 'N/A')}")
    with cols[1]:
        st.markdown(f"**Otros Diagnósticos Posibles**: {analysis.get('other_diagnoses', 'N/A')}")
        st.markdown(f"**Influencia de Info Adicional**: {analysis.get('extra_info_influence', 'N/A')}")

    # Final Assessment
    st.subheader("Evaluación Preventiva Preliminar")
    cols = st.columns(2)
    with cols[0]:
        classification = analysis.get('advance_classification', 'Unknown')
        color = "green" if classification.lower() == 'benign' else "red" if classification.lower() == 'malignant' else "orange"
        confidence = analysis.get('confidence_level', 0)
        try:
            confidence_val = float(confidence) * 100
        except (ValueError, TypeError):
            confidence_val = 0
        progress_val = min(max(confidence_val / 100, 0.0), 1.0)

        st.warning("⚠️ Esta es una evaluación preliminar asistida por IA que ayudará a los médicos y no constituye un diagnóstico médico conclusivo.")
        st.markdown(f"**Evaluación preventiva preliminar**: <span style='color:{color}; font-weight:bold;'>{classification}</span>", unsafe_allow_html=True)
        st.progress(progress_val, text=f"Nivel de Confianza del modelo: **{confidence_val:.1f}**%")
        st.info("👨‍⚕️ Recuerde: La mejor prevención es la revisión regular con un profesional de la salud.")

    with cols[1]:
        st.markdown(f"**Observaciones Generales**: {analysis.get('final_explanation', 'N/A')}")

def display_image(image_id):
    """Función para mostrar la imagen segmentada"""
    # ... (keep existing implementation)
    try:
        r_img = requests.get(
            f"{BASE_URL}/get_segmented_image/{image_id}",
            headers=headers,
            timeout=30
        )
        if r_img.status_code == 200:
            image_data = r_img.json()
            seg_b64 = image_data.get("segmented_image_b64")
            if seg_b64:
                try:
                    seg_img = Image.open(BytesIO(base64.b64decode(seg_b64)))
                    st.image(seg_img, caption="Imagen Segmentada", use_container_width=True)
                except Exception as e:
                    st.error(f"Error decoding or displaying segmented image: {e}")
            else:
                st.info("No se encontró la imagen segmentada.")
        elif r_img.status_code == 404:
             st.info(f"Imagen segmentada para ID {image_id} no encontrada.")
        else:
            st.error(f"Error {r_img.status_code} al obtener imagen segmentada: {r_img.text}")
    except requests.RequestException as e:
        st.error(f"Error de red al obtener la imagen segmentada: {e}")
# --- End of unchanged functions ---


if "access_token" not in st.session_state or not st.session_state["access_token"]:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    st.stop()

token = st.session_state["access_token"]
username_state = st.session_state.get("logged_in_user", "Unknown") # Use .get for safety
headers = {"Authorization": f"Bearer {token}"}

st.title("🔍 Análisis Avanzado")

# Small ABCDE guidance
with st.expander("¿Qué es la regla ABCDE?", expanded=False):
    st.markdown("""
    **A - Asimetría**: manchas que no sean uniformes en forma.<br>
    **B - Borde**: Bordes irregulares, dentados o mal definidos.<br>
    **C - Color**: Varias tonalidades, incluyendo marrón, negro, rojo, azul o blanco.<br>
    **D - Diámetro**: Mayor de 6 mm.<br>
    **E - Evolución**: Cambios en el tiempo (tamaño, forma, color, elevación o síntomas).<br>
    """, unsafe_allow_html=True)

# Crear tabs para organizar la interfaz
tab1, tab2 = st.tabs(["📥 Imágenes Pendientes", "🔍 Análisis Manual"])

with tab1:
    st.subheader("Imágenes Pendientes de Análisis")

    if st.button("🔄 Actualizar lista", key="refresh_pending"):
        st.rerun()

    try:
        pending_resp = requests.get(f"{BASE_URL}/pending_analysis", headers=headers, timeout=30)

        if pending_resp.status_code == 200:
            pending_images = pending_resp.json()

            if not pending_images:
                st.info("No hay imágenes pendientes de análisis avanzado.")
            else:
                st.write(f"Se encontraron {len(pending_images)} imágenes pendientes de análisis.")

                for img in pending_images:
                    img_id = img.get('id', 'N/A')
                    timestamp_str = img.get('timestamp', 'N/A')
                    try:
                        # Attempt to format timestamp nicely
                        timestamp_display = datetime.fromisoformat(timestamp_str).strftime('%d %b %Y, %H:%M')
                    except:
                        timestamp_display = timestamp_str # Fallback to raw string

                    body_part_display = img.get('body_part', 'Sin especificar')

                    with st.expander(f"Imagen del {timestamp_display} - {body_part_display} (ID: {img_id})"):
                        cols = st.columns([0.7, 0.3])

                        with cols[0]:
                            st.markdown(f"""
                            - **ID**: {img_id}
                            - **Fecha**: {timestamp_display}
                            - **Parte del cuerpo**: {body_part_display}
                            - **Primera clasificación**: {img.get('first_classification', 'No disponible')}
                            """)
                            if img_id != 'N/A':
                                display_image(img_id)
                            else:
                                st.warning("ID de imagen no disponible.")

                        with cols[1]:
                            if img_id != 'N/A': # Only show button if ID exists
                                if st.button("🔍 Analizar", key=f"analyze_{img_id}"):
                                    # ----- MODIFICATION START -----
                                    # We need to tell the backend WHICH image to process.
                                    # Assuming the backend /start_process can take an image_id
                                    # If not, the backend API needs modification.
                                    # Let's *assume* it can take `image_id` in the payload for now.
                                    payload = {
                                        "username": username_state, # Or maybe fetch from img['username'] if available?
                                        "image_id": img_id,
                                        "body_part": img.get('body_part') # Pass body_part if available
                                    }
                                    # Remove None values from payload if API doesn't like them
                                    payload = {k: v for k, v in payload.items() if v is not None}

                                    with st.spinner(f"Realizando análisis avanzado para imagen {img_id}..."):
                                        try:
                                            adv_resp = requests.post(
                                                f"{BASE_URL}/start_process",
                                                json=payload,
                                                headers=headers,
                                                timeout=120 # Increased timeout for potentially long analysis
                                            )

                                            if adv_resp.status_code == 200:
                                                analysis_doc = adv_resp.json() # This is the full document

                                                # Extract the nested analysis details
                                                analysis_details = None
                                                if 'analysis' in analysis_doc:
                                                    if isinstance(analysis_doc['analysis'], list) and analysis_doc['analysis']:
                                                        analysis_details = analysis_doc['analysis'][0]
                                                    elif isinstance(analysis_doc['analysis'], dict):
                                                         analysis_details = analysis_doc['analysis']

                                                # Display using the extracted details
                                                if analysis_details:
                                                     st.success("✅ Análisis completado")
                                                     display_analysis_details(analysis_details)
                                                     # Add a button to refresh the list *after* showing results
                                                     if st.button("Ocultar resultado y actualizar lista", key=f"refresh_after_{img_id}"):
                                                         st.rerun()
                                                else:
                                                     st.error("Análisis completado, pero la estructura de detalles ('analysis') no se encontró en la respuesta.")
                                                     st.json(analysis_doc) # Show raw response for debugging

                                            elif adv_resp.status_code == 404:
                                                st.error(f"Error 404: No se encontró el recurso para procesar (Imagen ID: {img_id}?). Verifique la API.")
                                            elif adv_resp.status_code == 422:
                                                st.error(f"Error 422: Datos inválidos enviados.")
                                                try:
                                                    st.json(adv_resp.json()) # Show validation errors if available
                                                except:
                                                    st.text(adv_resp.text)
                                            else:
                                                st.error(f"Error {adv_resp.status_code}: {adv_resp.text}")
                                        except requests.Timeout:
                                             st.error("Error: La solicitud de análisis tardó demasiado tiempo (timeout).")
                                        except requests.RequestException as e:
                                            st.error(f"Error de conexión durante el análisis: {e}")
                                    # ----- MODIFICATION END -----
                            else:
                                st.write("Análisis no disponible (ID inválido).")

        elif pending_resp.status_code == 401:
            st.error("Error 401: No autorizado. Verifique su inicio de sesión.")
        else:
            st.error(f"Error al obtener imágenes pendientes: {pending_resp.status_code} - {pending_resp.text}")

    except requests.Timeout:
        st.error("Error: La solicitud para obtener imágenes pendientes tardó demasiado (timeout).")
    except requests.RequestException as e:
        st.error(f"Error de conexión al obtener imágenes pendientes: {e}")


with tab2:
    st.subheader("Análisis Manual")
    st.markdown("Esta opción generalmente iniciará el análisis en la imagen *más reciente* subida por el usuario especificado (opcionalmente filtrada por parte del cuerpo).")

    col1, col2 = st.columns(2)

    with col1:
        adv_username = st.text_input(
            "Nombre de usuario para Análisis Avanzado",
            value=username_state, # Default to logged-in user
            key="manual_username",
            help="Analizará la imagen más reciente para este usuario."
        )

    with col2:
        body_part_options = [
            "No especificar", # Make this the default
            "Brazo izquierdo",
            "Brazo derecho",
            "Tórax",
            "Espalda",
            "Pierna izquierda",
            "Pierna derecha",
            "Cuello",
            "Cabeza/Cara",
            "Otra",
        ]
        selected_body_part_filter = st.selectbox(
            "Filtrar por parte del cuerpo (opcional)",
            options=body_part_options,
            index=0, # Default to "No especificar"
            key="manual_body_part"
        )

    if st.button("🛠️ Iniciar Análisis Manual", key="manual_analyze_button"):
        if not adv_username:
            st.warning("⚠️ Se requiere el nombre de usuario para el análisis avanzado.")
        else:
            payload = {"username": adv_username}
            if selected_body_part_filter != "No especificar":
                payload["body_part"] = selected_body_part_filter

            with st.spinner(f"Iniciando análisis manual para {adv_username}..."):
                try:
                    adv_resp = requests.post(
                        f"{BASE_URL}/start_process",
                        json=payload,
                        headers=headers,
                        timeout=120 # Increased timeout
                    )

                    # ----- MODIFICATION START -----
                    if adv_resp.status_code == 200:
                        analysis_doc = adv_resp.json() # Full document

                        # Extract nested details
                        analysis_details = None
                        if 'analysis' in analysis_doc:
                           if isinstance(analysis_doc['analysis'], list) and analysis_doc['analysis']:
                               analysis_details = analysis_doc['analysis'][0]
                           elif isinstance(analysis_doc['analysis'], dict):
                                analysis_details = analysis_doc['analysis']

                        # Display using extracted details
                        if analysis_details:
                            st.success("✅ ¡Análisis avanzado completado!")
                            display_analysis_details(analysis_details)
                        else:
                            st.error("Análisis completado, pero la estructura de detalles ('analysis') no se encontró en la respuesta.")
                            st.json(analysis_doc) # Show raw response for debugging

                    elif adv_resp.status_code == 404:
                         st.error(f"Error 404: No se encontró imagen reciente para {adv_username}" + (f" en {selected_body_part_filter}" if selected_body_part_filter != "No especificar" else "") + ". O el endpoint no existe.")
                    elif adv_resp.status_code == 422:
                         st.error(f"Error 422: Datos inválidos enviados.")
                         try:
                             st.json(adv_resp.json())
                         except:
                             st.text(adv_resp.text)
                    else:
                        st.error(f"Error {adv_resp.status_code}: {adv_resp.text}")
                    # ----- MODIFICATION END -----

                except requests.Timeout:
                    st.error("Error: La solicitud de análisis tardó demasiado tiempo (timeout).")
                except requests.RequestException as e:
                    st.error(f"Error de conexión durante el análisis manual: {e}")

st.markdown("---")
st.info("Si deseas ver todas tus imágenes y resultados, revisa la página de Historial.")
