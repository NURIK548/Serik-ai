import streamlit as st
import json
import difflib
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS
import os
import re

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Serik AI", layout="wide")

ADMIN_PASSWORD = "nurik777"

# =========================
# SESSION STATE
# =========================
if "admin" not in st.session_state:
    st.session_state.admin = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# MEMORY LOAD
# =========================
def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

memory = load_memory()

# =========================
# SAVE MEMORY
# =========================
def save_memory():
    with open("memory_base.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

# =========================
# EMOJI CLEANER (NEW)
# =========================
def clean_text(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text)

# =========================
# ADMIN MEMORY SYSTEM
# =========================
def handle_memory_command(text):

    if text.startswith("запомни "):

        if not st.session_state.admin:
            return "❌ Только админ может обучать бота"

        try:
            text = text.replace("запомни ", "", 1)

            if " это " not in text:
                return "Формат: запомни вопрос это ответ"

            question, answer = text.split(" это ", 1)

            question = question.strip().lower()
            answer = answer.strip()

            memory[question] = answer
            save_memory()

            return "✅ Запомнил"

        except:
            return "❌ Ошибка"

    return None

# =========================
# INTERNET SEARCH
# =========================
def internet_search(query):

    try:
        wikipedia.set_lang("ru")
        return wikipedia.summary(query, sentences=2)
    except:
        pass

    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=3))

        if results:
            return "\n\n".join([r.get("body") or r.get("title") or "" for r in results])

    except:
        pass

    return "❌ Ничего не найдено"

# =========================
# BRAIN
# =========================
def brain(text):

    text = text.lower().strip()

    mem = handle_memory_command(text)
    if mem:
        return mem

    if text in memory:
        return memory[text]

    match = difflib.get_close_matches(text, memory.keys(), n=1, cutoff=0.75)
    if match:
        return memory[match[0]]

    return internet_search(text)

# =========================
# VOICE
# =========================
def speak(text):
    try:
        text = clean_text(text)   # 👈 EMOJI REMOVED HERE

        tts = gTTS(text=text[:300], lang="ru")
        file = "voice.mp3"
        tts.save(file)

        with open(file, "rb") as f:
            st.audio(f.read(), format="audio/mp3")

        os.remove(file)
    except:
        pass

# =========================
# SIDEBAR (ADMIN)
# =========================
st.sidebar.title("⚙️ Menu")

if not st.session_state.admin:
    password = st.sidebar.text_input("Admin password", type="password")

    if st.sidebar.button("Login"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin = True
            st.sidebar.success("Admin ON 🔓")
        else:
            st.sidebar.error("Wrong password ❌")
else:
    st.sidebar.success("Admin MODE 🔐")

    if st.sidebar.button("Logout"):
        st.session_state.admin = False

# =========================
# UI
# =========================
st.title("🤖 Serik AI PRO")

st.write("💬 ChatGPT-style AI бот (admin protected)")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Напишите сообщение..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Думаю... 🤖"):
        response = brain(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    speak(response)
