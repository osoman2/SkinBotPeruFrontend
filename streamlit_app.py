import streamlit as st
import requests
import json
import base64
from io import BytesIO
from PIL import Image

# Replace with your FastAPI server base URL
BASE_URL = "http://127.0.0.1:800"

st.set_page_config(page_title="Melanoma Detection", layout="wide")

st.title("Melanoma Detection: Upload & Segmented Preview")

col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Upload Image")
    username = st.text_input("Username", "")
    timestamp = st.text_input("Timestamp (optional)", "")
    uploaded_file = st.file_uploader("Select an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Show the original image preview
        st.image(uploaded_file, caption="Original Image", use_container_width=True)

    if st.button("Submit for Segmentation"):
        if not username:
            st.warning("Username required.")
        elif not uploaded_file:
            st.warning("Please upload an image.")
        else:
            files = {
                "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
            }
            data = {"username": username}
            if timestamp:
                data["timestamp"] = timestamp

            try:
                resp = requests.post(f"{BASE_URL}/upload_image", files=files, data=data, timeout=60)
                if resp.status_code == 200:
                    result_json = resp.json()
                    st.success("Image processed successfully!")

                    first_class = result_json.get("first_classification", "N/A")
                    seg_data = result_json.get("segmentation_result", {})
                    overlay_b64 = result_json.get("segmented_image_b64", "")

                    st.markdown(f"**First Classification**: `{first_class}`")
                    st.json(seg_data)

                    # Display the overlay next to the original
                    if overlay_b64:
                        overlay_bytes = base64.b64decode(overlay_b64)
                        overlay_img = Image.open(BytesIO(overlay_bytes))
                        st.image(overlay_img, caption="Segmented Overlay", use_container_width=True)
                else:
                    st.error(f"Error {resp.status_code}: {resp.text}")

            except requests.RequestException as e:
                st.error(f"Error connecting to server: {e}")

with col2:
    st.subheader("2. Advanced Analysis (Optional)")
    adv_username = st.text_input("Username (Advanced)", key="adv_user")
    if st.button("Start Advanced Analysis"):
        if not adv_username:
            st.warning("Username required for analysis.")
        else:
            try:
                adv_resp = requests.post(f"{BASE_URL}/start_process", json={"username": adv_username}, timeout=60)
                if adv_resp.status_code == 200:
                    adv_data = adv_resp.json()
                    st.success("Advanced analysis completed.")
                    st.json(adv_data)
                else:
                    st.error(f"Error {adv_resp.status_code}: {adv_resp.text}")
            except requests.RequestException as e:
                st.error(f"Error connecting to server: {e}")

st.markdown("---")

st.subheader("List Users & Images")
if st.button("Fetch All"):
    try:
        list_resp = requests.get(f"{BASE_URL}/list_users_with_images", timeout=30)
        if list_resp.status_code == 200:
            users_data = list_resp.json()
            st.json(users_data)
        else:
            st.error(f"Error {list_resp.status_code}: {list_resp.text}")
    except requests.RequestException as e:
        st.error(f"Error connecting to server: {e}")