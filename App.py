import streamlit as st
import json
import difflib
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS
import os
import re
import base64

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Serik AI", layout="wide")

ADMIN_PASSWORD = "nurik777"

# =========================
# STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "admin" not in st.session_state:
    st.session_state.admin = False

if "learn_mode" not in st.session_state:
    st.session_state.learn_mode = False

if "last_q" not in st.session_state:
    st.session_state.last_q = None

# =========================
# MEMORY
# =========================
def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

memory = load_memory()

def save_memory():
    with open("memory_base.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

# =========================
# ADMIN LEARNING
# =========================
def handle_memory_command(text):
    if text.startswith("запомни "):

        if not st.session_state.admin:
            return "❌ Только админ может обучать"

        text = text.replace("запомни ", "", 1)

        if " это " not in text:
            return "⚠️ формат: запомни вопрос это ответ"

        q, a = text.split(" это ", 1)

        memory[q.strip().lower()] = a.strip()
        save_memory()

        return "✅ Запомнил ✨"

    return None

# =========================
# INTERNET
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

    return None

# =========================
# BRAIN (SELF LEARNING AI)
# =========================
def brain(text):

    text = text.lower().strip()

    # memory command
    mem_cmd = handle_memory_command(text)
    if mem_cmd:
        return mem_cmd

    # memory exact
    if text in memory:
        return memory[text]

    # fuzzy memory
    match = difflib.get_close_matches(text, memory.keys(), n=1, cutoff=0.7)
    if match:
        return memory[match[0]]

    # internet
    answer = internet_search(text)
    if answer:
        return answer

    # SELF LEARNING MODE
    st.session_state.learn_mode = True
    st.session_state.last_q = text

    return "🤖 Я не знаю ответ. Хочешь научить меня? Напиши: запомни ... это ..."

# =========================
# VOICE
# =========================
def speak(text):
    try:
        text = re.sub(r"[^\w\sа-яА-ЯёЁ]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return

        tts = gTTS(text=text[:300], lang="ru")
        file = "voice.mp3"
        tts.save(file)

        audio_html = f"""
        <audio autoplay hidden>
            <source src="data:audio/mp3;base64,{base64.b64encode(open(file,'rb').read()).decode()}">
        </audio>
        """

        st.markdown(audio_html, unsafe_allow_html=True)
        os.remove(file)

    except:
        pass

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Admin")

password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if password == ADMIN_PASSWORD:
        st.session_state.admin = True
        st.sidebar.success("Admin ON 🔓")
    else:
        st.sidebar.error("Wrong ❌")

if st.session_state.admin:
    st.sidebar.success("Admin mode 👑")

    if st.sidebar.button("Logout"):
        st.session_state.admin = False

# =========================
# UI
# =========================
st.title("🤖 Serik AI (Self Learning)")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Введите сообщение..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("thinking... 🤖"):
        response = brain(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    # reset learning mode if teaching
    if st.session_state.learn_mode and prompt.startswith("запомни "):
        st.session_state.learn_mode = False
        st.session_state.last_q = None

    speak(response)
