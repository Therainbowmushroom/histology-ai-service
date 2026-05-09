"""
Streamlit-фронтенд для гистологического анализа.
Обеспечивает регистрацию, логин, просмотр баланса, активацию промокодов,
загрузку SVS-файлов и отображение результатов предсказания.
"""

import requests
import streamlit as st
import time

API_URL = "http://backend:8000"

st.title("Histology AI")

# =====================================
# REGISTER
# =====================================

"""
Блок регистрации нового пользователя.
- Принимает username и password.
- Отправляет POST-запрос на /auth/register.
- Выводит ответ сервера.
"""

st.header("Register")

register_username = st.text_input("Register username")

register_password = st.text_input("Register password", type="password")

if st.button("Register"):
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "username": register_username,
            "password": register_password
        }
    )

    st.write(response.json())


# =====================================
# LOGIN
# =====================================

"""
Блок аутентификации.
- Принимает username и password.
- POST-запрос на /auth/login.
- При успехе сохраняет JWT-токен в st.session_state.
- При ошибке выводит сообщение.
"""

st.header("Login")

login_username = st.text_input("Login username")

login_password = st.text_input("Login password", type="password")

if st.button("Login"):
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "username": login_username,
            "password": login_password
        }
    )

    data = response.json()

    if "access_token" in data:
        st.session_state["token"] = data["access_token"]
        st.success("Logged in")

    else:
        st.error(data)

# =====================================
# USER PANEL
# =====================================

"""
Блок, отображаемый только после успешного логина.
Содержит: просмотр баланса, активацию промокода, загрузку SVS-файла.
"""

if "token" in st.session_state:

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    st.success("Authenticated")

    # =====================================
    # BALANCE
    # =====================================

    """
    Кнопка для получения текущего баланса пользователя.
    GET-запрос на /balance/me.
    """

    if st.button("Show balance"):

        response = requests.get(f"{API_URL}/balance/me", headers=headers)
        st.write(response.json())

    # =====================================
    # PROMOCODE
    # =====================================

    """
    Блок активации промокода.
    - Поле ввода кода.
    - POST-запрос на /promocode/activate с параметром code.
    - Вывод ответа (начисление бонуса или ошибка).
    """

    st.header("Promocode")

    promocode = st.text_input("Enter promocode")

    if st.button("Activate promocode"):
        response = requests.post(

            f"{API_URL}/promocode/activate",
            params={
                "code": promocode
            },

            headers=headers
        )

        st.write(response.json())

    # =====================================
    # UPLOAD
    # =====================================

    """
    Загрузка SVS-файла, запуск предсказания и опрос статуса.
    """

    st.header("Upload SVS")

    uploaded_file = st.file_uploader("Choose .svs file", type=["svs"])

    if uploaded_file is not None:

        if st.button("Run prediction"):

            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue())
            }

            response = requests.post(

                f"{API_URL}/prediction/upload",
                headers=headers,
                files=files
            )

            data = response.json()
            st.write(data)
            prediction_id = data["prediction_id"]

            # =====================================
            # POLLING
            # =====================================

            """
            Циклически проверяет статус предсказания, пока оно не завершится.
            Возможные статусы: PENDING, PROCESSING, INFERENCE, SUCCESS, FAILED.
            """
            status = "PENDING"
            status_data = {}
            while status in ["PENDING", "PROCESSING", "INFERENCE"]:
                time.sleep(2)
                status_response = requests.get(f"{API_URL}/prediction/{prediction_id}")
                status_data = status_response.json()
                status = status_data.get("status", "")
                st.write(f"Status: {status}")

            # =====================================
            # RESULT
            # =====================================

            if status == "SUCCESS":
                st.success("Prediction completed")
                st.write(f"Prediction: {status_data.get('result')}")
                st.write(f"Confidence: {status_data.get('confidence')}")
            else:
                st.error(f"Prediction failed: {status_data}")
