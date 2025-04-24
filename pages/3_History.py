# frontend/pages/3_History.py
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

# Configure page
st.set_page_config(
    page_title="Historial de Evaluaciones",
    page_icon="📋",
    layout="wide"
)

def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return date_str

def create_metrics_card(analysis_doc):
    analysis_item = analysis_doc["analysis"][0] if analysis_doc.get("analysis") else {}
    
    cols = st.columns(3)
    with cols[0]:
        initial_evaluation = analysis_item.get('segmentation_analysis', '').split(':')[-1].strip()
        st.metric("Clasificación preliminar inicial", initial_evaluation)
    with cols[1]:
        # Clasificación final del análisis avanzado
        final_classification = analysis_doc.get('final_classification', 'N/A')
        st.metric("Classificación de diagnóstico final", final_classification)
    with cols[2]:
        confidence = analysis_item.get('confidence_level', 'N/A')
        if confidence != 'N/A':
            try:
                confidence = f"{float(confidence)*100:.1f}%"
            except (ValueError, TypeError):
                confidence = 'N/A'
        st.metric("Confidence Level", confidence)

def display_analysis_details(item, headers):
    # ABCDE criteria
    st.subheader("Criterios ABCDE")
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"**A - Asimetría**: {item.get('asymmetry', '')}")
        st.markdown(f"**B - Irregularidad del Borde**: {item.get('border_irregularity', '')}")
    with cols[1]:
        st.markdown(f"**C - Variegación del Color**: {item.get('color_variegation', '')}")
        st.markdown(f"**D - Evaluación del Diámetro**: {item.get('diameter_assessment', '')}")
    with cols[2]:
        st.markdown(f"**E - Evaluación de la Evolución**: {item.get('evolution_assessment', '')}")

    # Technical Analysis
    st.subheader("Análisis Técnico")
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**Análisis de Segmentación**: {item.get('segmentation_analysis', '')}")
        st.markdown(f"**Comentarios Técnicos**: {item.get('image_technical_commentaries', '')}")
    with cols[1]:
        st.markdown(f"**Otros Diagnósticos Posibles**: {item.get('other_diagnoses', '')}")
        st.markdown(f"**Influencia de información Adicional**: {item.get('extra_info_influence', '')}")

    # Final Assessment
    st.subheader("Evaluación preventiva final: ")
    cols = st.columns(2)
    with cols[0]:
        classification = item.get('advance_classification', '')
        color = "green" if classification.lower() == 'benign' else "red" if classification.lower() == 'malignant' else "yellow"
        confidence = item.get('confidence_level', 0) * 100
        st.markdown(f"**Clasificación pre-dignóstica**: <span style='color:{color}'>{classification}</span>", unsafe_allow_html=True)

        st.progress(confidence/100, f"Nivel de Confianza:  **{confidence:.1f}**%")
    with cols[1]:
        # Highlight final explanation
        st.markdown(f"**Explicación General**:  **{item.get('final_explanation', '')}**")

def display_image_with_controls(image_id: str
, original_b64: str, segmented_b64: str, headers: dict):
    """Display image with delete controls"""


    col1, col2, col3 = st.columns([0.3, 0.3, 0.4])
    
    with col1:
        if original_b64:
            try:
                st.image(
                    base64.b64decode(original_b64),
                    caption="Imagen Original",
                    use_container_width=True,
                    width=200
                )
            except Exception:
                st.error("Error displaying original image")
    
    with col2:
        if segmented_b64:
            try:
                st.image(
                    base64.b64decode(segmented_b64),
                    caption="Imagen Segmentada",
                    use_container_width=True,
                    width=200
                )
            except Exception:
                st.error("Error displaying segmented image")
    
    with col3:
        st.markdown("&nbsp;")
        if st.button("🗑️", key=f"delete_img_{image_id}", help="Delete this image"):
            if st.warning("⚠️ Warning: Deleting this image will also remove all related analyses. Are you sure?"):
                if delete_image(image_id, headers):
                    st.success("Image deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete image")

def delete_analysis(analysis_id: str, headers: dict) -> bool:
    try:
        resp = requests.delete(
            f"{BASE_URL}/delete_analysis/{analysis_id}",
            headers=headers,
            timeout=30
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False

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
        "No especificar",
        ""
    ]
def main():
    # Check authentication
    if "access_token" not in st.session_state or not st.session_state["access_token"]:
        st.warning("Please log in to access this page.")
        return

    st.title("📋 Historial de Evaluaciones Preventivas")
    st.markdown("""
    ⚠️ **Importante**: Este historial muestra evaluaciones preliminares asistidas por IA. 
    No constituyen diagnósticos médicos y no sustituyen la evaluación profesional regular. 
    Sin embargo, pueden ser útiles para el seguimiento preventivo de manchas cutáneas y su uso ayudarán a los médicos y usuarios.
    """)

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Fecha Inicio", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Fecha Fin", value=datetime.now())
    with col3:
        body_part = st.selectbox("Parte del Cuerpo", body_part_options)

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "body_part": body_part if body_part != "Todas" else None
    }

    try:
        with st.spinner("Cargando historial..."):
            resp = requests.get(f"{BASE_URL}/list_analyses", headers=headers, params=params, timeout=30)
            
            if resp.status_code == 200:
                analyses = resp.json()
                if not analyses:
                    st.info("No hay análisis disponibles para este período.")
                    return

                # Métricas de Resumen
                total_analyses = len(analyses)
                #Count 1 if his malignant and confidence > 0.75
                high_risk = sum(1 for r in analyses if 'malignant' in r.get('analysis', {}).get('advance_classification', '').lower() and r.get('analysis', {}).get('confidence_level', 0) > 0.75)

                # Mostrar métricas de resumen
                metrics_cols = st.columns(4)
                with metrics_cols[0]:
                    st.metric("Total Análisis", total_analyses)
                with metrics_cols[1]:
                    st.metric("Casos Alto Riesgo", high_risk)
                with metrics_cols[2]:
                    st.metric("Tasa de Riesgo", f"{(high_risk/total_analyses)*100:.1f}%")
                with metrics_cols[3]:
                    unique_parts = len(set(a.get('body_part', '') for a in analyses))
                    st.metric("Partes del Cuerpo", unique_parts)

                # Visualización de línea temporal
                timeline_data = pd.DataFrame([
                    {
                        'date': datetime.fromisoformat(a['analysis_date']),
                        'risk_level': a.get('analysis', {}).get('advance_classification', 'unknown'),
                        'confidence': a.get('analysis', {}).get('confidence_level', 0),
                        'body_part': a.get('body_part', 'desconocida')
                    } for a in analyses
                ])
                
                # Gráfico de evolución temporal
                fig = px.scatter(timeline_data, 
                               x='date', 
                               y='confidence',
                               color='risk_level',
                               symbol='body_part',
                               title="Evolución Temporal de Análisis",
                               labels={
                                   'date': 'Fecha de Análisis', 
                                   'confidence': 'Nivel de Confianza',
                                   'risk_level': 'Nivel de Riesgo',
                                   'body_part': 'Parte del Cuerpo'
                               })
                st.plotly_chart(fig, use_container_width=True)

                # Mostrar análisis individuales
                for analysis_doc in analyses:
                    with st.expander(f"Análisis del {analysis_doc['analysis_date'][:10]} - {analysis_doc['body_part']}", expanded=False):
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown(f"**Fecha**: {format_date(analysis_doc['analysis_date'])}")
                            st.markdown(f"**Parte del Cuerpo**: {analysis_doc['body_part']}")
                        with cols[1]:
                            # Green if benign, red if malignant, yellow if other
                            color = "green" if analysis_doc.get('analysis', {}).get('advance_classification', '').lower() == 'benign' else "red" if analysis_doc.get('analysis', {}).get('advance_classification', '').lower() == 'malignant' else "yellow"
                            st.markdown(f"**Recomendación General**:  <span style='color:{color}'>{analysis_doc.get('overall_recommendation', '')}</span>", unsafe_allow_html=True)

                        display_analysis_details(analysis_doc['analysis'], headers)
                        
                        # Add this section to display images
                        if 'image_id' in analysis_doc:
                            display_image_with_controls(
                                image_id=analysis_doc.get('image_id', ''),
                                original_b64=analysis_doc.get('image_b64', ''),
                                segmented_b64=analysis_doc.get('segmented_image_b64', ''),
                                headers=headers
                            )

            else:
                st.error(f"Error {resp.status_code}: {resp.text}")

    except requests.RequestException as e:
        st.error(f"Error fetching analysis list: {e}")

if __name__ == "__main__":
    main()
