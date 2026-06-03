import streamlit as st
import json
import difflib
import os
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS

# =========================
# ЖАДТЫ ЖҮКТЕУ
# =========================

def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

memory = load_memory()

# =========================
# ЖАДҚА САҚТАУ
# =========================

def save_to_memory(question, answer):
    try:
        memory[question.lower()] = answer

        with open("memory_base.json", "w", encoding="utf-8") as f:
            json.dump(
                memory,
                f,
                ensure_ascii=False,
                indent=4
            )
    except Exception:
        pass

# =========================
# ДАУЫСПЕН ОҚУ
# =========================

def speak_text(text):
    try:
        short_text = text[:300] + "..." if len(text) > 300 else text

        tts = gTTS(
            text=short_text,
            lang="ru",
            slow=False
        )

        filename = "voice.mp3"
        tts.save(filename)

        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()

        st.audio(
            audio_bytes,
            format="audio/mp3",
            autoplay=True
        )

        os.remove(filename)

    except Exception:
        pass

# =========================
# ИНТЕРНЕТТЕН ІЗДЕУ
# =========================

def search_no_api(query):

    clean_query = (
        query.lower()
        .replace("напиши", "")
        .replace("эссе", "")
        .replace("реферат", "")
        .replace("про", "")
        .strip()
    )

    try:
        wikipedia.set_lang("ru")

        wiki_summary = wikipedia.summary(
            clean_query,
            sentences=7
        )

        return (
            "Вот подробная информация из Википедии:\n\n"
            + wiki_summary
        )

    except:
        pass

    try:
        ddgs = DDGS()

        results = list(
            ddgs.text(
                clean_query,
                region="ru-ru",
                max_results=5
            )
        )

        if results:

            text = "Вот что я нашёл в интернете:\n\n"

            for r in results:
                body = r.get("body", "")
                text += f"• {body}\n\n"

            return text

    except:
        pass

    return "Извини, я не смог найти информацию."

# =========================
# БОТ ЛОГИКАСЫ
# =========================

def get_bot_response(user_input, memory_base):

    user_input = user_input.lower().strip()

    if not memory_base:

        answer = search_no_api(user_input)

        if "Извини" not in answer:
            save_to_memory(user_input, answer)

        return answer

    matches = difflib.get_close_matches(
        user_input,
        memory_base.keys(),
        n=1,
        cutoff=0.6
    )

    if matches:
        return memory_base[matches[0]]

    answer = search_no_api(user_input)

    if answer and "Извини" not in answer:
        save_to_memory(user_input, answer)

    return answer

# =========================
# STREAMLIT ИНТЕРФЕЙСІ
# =========================

st.set_page_config(
    page_title="Serik-Ai PRO",
    layout="wide"
)

st.title("🤖 Serik-Ai PRO")
st.write("Разработчик: Нурик")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Чат тарихы

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Хабарлама енгізу

if prompt := st.chat_input("Напишите сообщение..."):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner(
        "Serik-Ai думает и ищет информацию..."
    ):
        response = get_bot_response(
            prompt,
            memory
        )

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    speak_text(response)
