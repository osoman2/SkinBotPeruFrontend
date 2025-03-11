# frontend/0_Login.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

st.set_page_config(page_title="Login / Register", layout="wide")

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = "user"  # default or "admin" if needed

st.title("🔑 Iniciar Sesión / Registro")

tab_login, tab_register = st.tabs(["Iniciar Sesión", "Registrarse"])

with tab_login:
    st.subheader("Iniciar Sesión")
    login_user = st.text_input("Usuario", key="login_user")
    login_pass = st.text_input("Contraseña", type="password", key="login_pass")

    if st.button("Acceder", key="login_btn"):
        if not login_user or not login_pass:
            st.warning("Por favor, ingresa usuario y contraseña")
        else:
            try:
                resp = requests.post(
                    f"{BASE_URL}/login",
                    json={"username": login_user, "password": login_pass},
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state["access_token"] = data["access_token"]
                    st.session_state["logged_in_user"] = login_user
                    # If the backend returns a role, you could store it
                    # st.session_state["role"] = data.get("role", "user")
                    st.success(f"Bienvenido/a, {login_user}")
                    st.rerun()  # refresh page
                else:
                    st.error(f"Error {resp.status_code}: {resp.json().get('detail', 'Credenciales inválidas')}")
            except requests.RequestException as e:
                st.error(f"No se pudo conectar con el servidor: {e}")

with tab_register:
    st.subheader("Crear Cuenta")
    reg_user = st.text_input("Elige un nombre de usuario", key="reg_username")
    reg_pass = st.text_input("Elige una contraseña", type="password", key="reg_password")

    if st.button("Registrarse", key="register_btn"):
        if not reg_user or not reg_pass:
            st.warning("Por favor, completa todos los campos")
        else:
            try:
                r = requests.post(
                    f"{BASE_URL}/register",
                    json={"username": reg_user, "password": reg_pass},
                    timeout=15
                )
                if r.status_code == 200:
                    st.success("Registro exitoso. Ahora puedes iniciar sesión.")
                else:
                    st.error(r.json().get("detail", "Error desconocido al registrarse."))
            except requests.RequestException as e:
                st.error(f"No se pudo conectar con el servidor: {e}")

st.markdown("---")
st.info("Si ya tienes una sesión iniciada, navega a otra página desde la barra lateral. O cierra sesión arriba.")

if st.session_state["access_token"]:
    if st.button("Cerrar Sesión"):
        st.session_state["access_token"] = None
        st.session_state["logged_in_user"] = None
        st.rerun()
