import streamlit as st
import json
import difflib
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS
import os

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
# ADMIN MEMORY SYSTEM (FIXED)
# =========================
def handle_memory_command(text):

    if text.startswith("запомни "):

        if not st.session_state.admin:
            return "❌ Только админ может обучать бота"

        try:
            text = text.replace("запомни ", "", 1)

            # FORMAT: вопрос это ответ
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

    # memory command
    mem = handle_memory_command(text)
    if mem:
        return mem

    # exact memory
    if text in memory:
        return memory[text]

    # fuzzy memory
    match = difflib.get_close_matches(text, memory.keys(), n=1, cutoff=0.75)
    if match:
        return memory[match[0]]

    # internet fallback
    return internet_search(text)

# =========================
# VOICE
# =========================
def speak(text):
    try:
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

# history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input
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
