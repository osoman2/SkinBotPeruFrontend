# frontend/pages/3_History.py
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(page_title="Historial", layout="wide")

if "access_token" not in st.session_state or not st.session_state["access_token"]:
    st.warning("Necesitas iniciar sesión para ver tu historial.")
    st.stop()

token = st.session_state["access_token"]
username = st.session_state["logged_in_user"]

st.title("📄 Historial de Imágenes y Análisis")

# Date filters for optional timeline
st.write("Filtra por rango de fechas (opcional).")
col1, col2, col3 = st.columns([1,1,1])

with col1:
    start_date = st.date_input("Fecha Inicio", value=date(2025, 1, 1))
with col2:
    end_date = st.date_input("Fecha Fin", value=date.today())
with col3:
    st.write("")  # spacer
    if st.button("Filtrar"):
        st.session_state["history_start"] = start_date
        st.session_state["history_end"] = end_date
        st.rerun()

# We store the chosen range in session_state so a rerun keeps it
start_val = st.session_state.get("history_start", start_date)
end_val = st.session_state.get("history_end", end_date)

try:
    # List analyses in the chosen date range
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "username": username,
        "start": start_val.isoformat(),
        "end": end_val.isoformat()
    }
    st.write(f"Mostrando análisis para `{username}`, entre {start_val} y {end_val}.")
    with st.spinner("Cargando historial..."):
        resp = requests.get(f"{BASE_URL}/list_analyses", headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            analyses = resp.json()
            if not analyses:
                st.info("No se encontraron análisis en este rango de fechas.")
            else:
                for idx, analysis_doc in enumerate(analyses, start=1):
                    st.subheader(f"Análisis #{idx} - {analysis_doc['analysis_date']}")
                    st.write(f"**Parte del cuerpo**: {analysis_doc.get('body_part', 'N/A')}")
                    st.write(f"**Recomendación global**: {analysis_doc.get('overall_recommendation', '')}")

                    # Show each analysis item
                    for item in analysis_doc["analysis"]:
                        with st.expander(f"Image ID: {item['image_id']}"):
                            st.write(item)
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")

except requests.RequestException as e:
    st.error(f"Error al obtener la lista de análisis: {e}")


# Optionally, you can also show "raw" images from your /list_users_with_images endpoint
st.markdown("---")
if st.button("Ver Imágenes Originales & Segmentadas"):
    with st.spinner("Cargando imágenes..."):
        try:
            r = requests.get(f"{BASE_URL}/list_users_with_images", headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                user_data = next((u for u in data if u["username"] == username), None)
                if not user_data:
                    st.info("No hay imágenes para tu usuario.")
                else:
                    for bp_data in user_data["body_parts"]:
                        bp_name = bp_data.get("body_part", "N/A")
                        st.subheader(f"Parte del cuerpo: {bp_name}")
                        for img in bp_data.get("images", []):
                            image_id = img.get("image_id", "N/A")
                            st.write(f"**ID de Imagen**: {image_id}")
                            st.write(f"**Hora de Subida**: {img.get('upload_time', 'N/A')}")
                            
                            image_b64 = img.get("image_b64", None)
                            if image_b64:
                                st.image(base64.b64decode(image_b64), caption="Imagen Original", use_container_width=True)
                            
                            seg_b64 = img.get("segmented_image_b64", None)
                            if seg_b64:
                                st.image(base64.b64decode(seg_b64), caption="Imagen Segmentada", use_container_width=True)
                            
                            st.markdown("---")
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except requests.RequestException as e:
            st.error(f"Error: {e}")
