import streamlit as st
import json
import difflib
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS
import os
import re
import base64
import random

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

if "offline" not in st.session_state:
    st.session_state.offline = False

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
# MEMORY COMMAND
# =========================
def handle_memory_command(text):

    if text.startswith("запомни "):

        if not st.session_state.admin:
            return "❌ Admin only"

        text = text.replace("запомни ", "", 1)

        if " это " not in text:
            return "⚠️ format: запомни question это answer"

        q, a = text.split(" это ", 1)

        memory[q.strip().lower()] = a.strip()
        save_memory()

        return "✅ Saved"

    return None

# =========================
# AUTO 1000+ GENERATOR
# =========================
def generate_base():

    base = {}
    templates = [
        ("привет", "ПРИВЕТ 👋"),
        ("как дела", "Нормально 😎"),
        ("спасибо", "Пожалуйста,чем могу помочь 😊"),
        ("нормально", "Круто 😎"),
        ("ты кто", "Я ИССКУСТВЕННЫЙ ИНТЕЛЕКТ(ИИ) 🤖"),
        ("помоги мне", "ДА ЧЕМ МОГУ ПОМОЧЬ 😊"),
        ("прикол", "😄 ну примерно как"),
    ]

    for i in range(1000):
        q, a = templates[i % len(templates)]
        base[f"{q} {i}"] = f"{a} #{i}"

    with open("memory_base.json", "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=4)

    return "✅"

# =========================
# INTERNET
# =========================
def internet_search(query):

    if st.session_state.offline:
        return None

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
# GPT-LIKE BRAIN
# =========================
def brain(text):

    text = text.lower().strip()

    mem_cmd = handle_memory_command(text)
    if mem_cmd:
        return mem_cmd

    if text in memory:
        return memory[text]

    match = difflib.get_close_matches(text, memory.keys(), n=1, cutoff=0.7)
    if match:
        return memory[match[0]]

    # thinking simulation 🤖
    st.toast(random.choice([
        "🧠 ДУМАЮ...",
        "🔎 ИЩУ ДЛЯ ВАС...",
        "🤖 Анализ делаб жди..."
    ]))

    answer = internet_search(text)
    if answer:
        return answer

    return f"🤖 Я этого не знаю,Но я могу этого учить: '{text}'"

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
st.sidebar.title("⚙️ Panel")

# admin
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if password == ADMIN_PASSWORD:
        st.session_state.admin = True
        st.sidebar.success("Admin ON 🔓")
    else:
        st.sidebar.error("Wrong ❌")

if st.sidebar.button("Generate 1000+"):
    st.sidebar.success(generate_base())

st.session_state.offline = st.sidebar.toggle("Offline mode")

# =========================
# UI
# =========================
st.title("🤖 Serik AI PRO")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("пишите сюда..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("thinking... 🤖"):
        response = brain(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    speak(response)
