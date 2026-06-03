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
# LANGUAGE DETECT (RU / EN ONLY)
# =========================
def detect_lang(text):
    text = text.lower()

    en_score = len(re.findall(r"[a-z]", text))
    ru_score = len(re.findall(r"[а-яё]", text))

    if en_score > ru_score:
        return "en"
    return "ru"

# =========================
# MEMORY COMMAND
# =========================
def handle_memory_command(text):
    if text.startswith("запомни "):

        if not st.session_state.admin:
            return "❌ Только админ может обучать"

        text = text.replace("запомни ", "", 1)

        if " это " not in text:
            return "⚠️ Формат: запомни вопрос это ответ"

        q, a = text.split(" это ", 1)

        memory[q.strip()] = a.strip()
        save_memory()

        return "✅ Запомнил ✨"

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

    return None

# =========================
# BRAIN (MEMORY FIRST)
# =========================
def brain(text):

    user_lang = detect_lang(text)

    ru_text = text.lower().strip()

    mem_cmd = handle_memory_command(ru_text)
    if mem_cmd:
        return mem_cmd

    if ru_text in memory:
        return memory[ru_text]

    match = difflib.get_close_matches(ru_text, memory.keys(), n=1, cutoff=0.75)
    if match:
        return memory[match[0]]

    answer = internet_search(ru_text)
    if answer:
        return answer

    return "Я не знаю 😕 Но можешь научить меня ✨"

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
# SIDEBAR (ADMIN)
# =========================
st.sidebar.title("⚙️ Admin Panel")

password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if password == ADMIN_PASSWORD:
        st.session_state.admin = True
        st.sidebar.success("Admin ON 🔓")
    else:
        st.sidebar.error("Wrong password ❌")

if st.session_state.admin:
    st.sidebar.success("Admin mode 👑")

    if st.sidebar.button("Logout"):
        st.session_state.admin = False

# =========================
# UI
# =========================
st.title("🤖 Serik AI CLEAN VERSION")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Жазыңыз..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Ойлап жатыр... 🤖"):
        response = brain(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    speak(response)
