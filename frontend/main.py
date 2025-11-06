import streamlit as st
import requests
import base64

st.set_page_config(page_title="GolosAI-DE", layout="centered")
st.title("🎙️ GolosAI-DE Frontend")
st.write("Ведите диалог с AI на немецком языке.")

# --- Сценарии и голоса ---
scenarios = {
    "В ресторане": "restaurant",
    "Знакомство": "introduction",
    "В аэропорту": "airport"
}
selected_scenario = st.selectbox("Сценарий:", list(scenarios.keys()))

# Используем один голос по умолчанию
selected_voice = "de_DE-thorsten-high"

# --- Сессия ---
if "session_id" not in st.session_state:
    try:
        r = requests.post(
            "http://backend:8000/start_session",
            params={"scenario_id": scenarios[selected_scenario]},
            timeout=10
        )
        if r.ok:
            st.session_state["session_id"] = r.json()["session_id"]
            st.success("✅ Сессия создана")
        else:
            st.error(f"Не удалось создать сессию: {r.status_code}")
    except Exception as e:
        st.error(f"Ошибка подключения к backend: {e}")

if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Вкладки ---
tab1, tab2 = st.tabs(["📂 Загрузка файла", "🎤 Запись голосом"])

with tab1:
    st.info("Загрузите готовый WAV-файл")
    uploaded_file = st.file_uploader("Выберите WAV-файл", type=["wav"])

    if uploaded_file and st.button("Отправить файл", key="upload_btn"):
        with st.spinner("Обработка..."):
            try:
                files = {"audio": (uploaded_file.name, uploaded_file, "audio/wav")}
                data = {
                    "voice": selected_voice,
                    "scenario_id": scenarios[selected_scenario],
                    "session_id": st.session_state.get("session_id", "")
                }
                resp = requests.post(
                    "http://backend:8000/dialogue_file",
                    files=files,
                    data=data,
                    timeout=60
                )

                if resp.ok:
                    result = resp.json()
                    st.session_state["history"].append({
                        "user": result["recognized"],
                        "ai": result["answer"],
                        "audio": base64.b64decode(result["audio_b64"])
                    })
                    st.success("✅ Ответ получен!")
                    st.rerun()
                else:
                    st.error(f"Ошибка: {resp.status_code} - {resp.text}")
            except Exception as e:
                st.error(f"Ошибка: {e}")

with tab2:
    st.info("🎙️ Нажмите на кнопку записи ниже, говорите, затем остановите запись")

    # Встроенный аудио рекордер Streamlit
    audio_bytes = st.audio_input("Нажмите для записи", key="audio_recorder")

    if audio_bytes is not None:
        st.audio(audio_bytes, format="audio/wav")

        if st.button("📤 Отправить запись", key="send_btn", type="primary"):
            with st.spinner("Отправка и обработка..."):
                try:
                    # Отправляем на backend
                    files = {"audio": ("recording.wav", audio_bytes, "audio/wav")}
                    data = {
                        "voice": selected_voice,
                        "scenario_id": scenarios[selected_scenario],
                        "session_id": st.session_state.get("session_id", "")
                    }

                    resp = requests.post(
                        "http://backend:8000/dialogue_file",
                        files=files,
                        data=data,
                        timeout=60
                    )

                    if resp.ok:
                        result = resp.json()
                        recognized = result.get("recognized", "")
                        answer = result.get("answer", "")
                        audio_b64 = result.get("audio_b64", "")

                        if audio_b64:
                            st.session_state["history"].append({
                                "user": recognized,
                                "ai": answer,
                                "audio": base64.b64decode(audio_b64)
                            })
                            st.success("✅ Ответ получен!")
                            st.rerun()
                        else:
                            st.error("Пустой ответ от сервера")
                    else:
                        st.error(f"❌ Ошибка: {resp.status_code}")
                        st.code(resp.text)

                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")

# --- История диалога ---
if st.session_state["history"]:
    st.divider()
    st.subheader("💬 История диалога")

    for turn in st.session_state["history"]:
        with st.chat_message("user"):
            st.write(f"**Вы:** {turn['user']}")

        with st.chat_message("assistant"):
            st.write(f"**AI:** {turn['ai']}")
            if "audio" in turn and turn["audio"]:
                st.audio(turn["audio"], format="audio/wav")

# --- Завершение диалога ---
st.divider()
if st.button("🏁 Завершить диалог"):
    try:
        resp = requests.post(
            "http://backend:8000/end_session",
            data={"session_id": st.session_state.get("session_id", "")},
            timeout=10
        )
        if resp.ok:
            transcript = resp.json()["transcript"]
            st.download_button(
                label="📥 Скачать стенограмму",
                data=transcript,
                file_name="dialogue.txt",
                mime="text/plain"
            )
            st.success("✅ Сессия завершена")
        else:
            st.error(f"Ошибка: {resp.status_code}")
    except Exception as e:
        st.error(f"Ошибка: {e}")