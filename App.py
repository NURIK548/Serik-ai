import streamlit as st
import json
import difflib
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS
from deep_translator import GoogleTranslator
import os
import re
import base64

st.set_page_config(page_title="Serik AI", layout="wide")

ADMIN_PASSWORD = "nurik777"

# =========================
# STATE
# =========================
if "admin" not in st.session_state:
    st.session_state.admin = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "learning_mode" not in st.session_state:
    st.session_state.learning_mode = False

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
# LANGUAGE DETECTION
# =========================
def detect_lang(text):
    try:
        if re.search(r"[а-яА-ЯёЁ]", text):
            if any(x in text.lower() for x in "әіңғүұқөһ"):
                return "kk"
            return "ru"
        elif re.search(r"[a-zA-Z]", text):
            return "en"
        return "ru"
    except:
        return "ru"

# =========================
# TRANSLATOR
# =========================
def translate(text, src="auto", dest="ru"):
    try:
        return GoogleTranslator(source=src, target=dest).translate(text)
    except:
        return text

# =========================
# MEMORY COMMAND
# =========================
def handle_memory_command(text):
    if text.startswith("запомни "):
        if not st.session_state.admin:
            return "❌ Только админ"

        text = text.replace("запомни ", "", 1)

        if " это " not in text:
            return "Формат: запомни вопрос это ответ"

        q, a = text.split(" это ", 1)
        memory[q.strip().lower()] = a.strip()
        save_memory()

        return "✅ Запомнил"

    return None

# =========================
# SEARCH
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

    user_lang = detect_lang(text)

    text_ru = translate(text, "auto", "ru")
    text = text_ru.lower().strip()

    mem = handle_memory_command(text)
    if mem:
        return translate(mem, "ru", user_lang)

    if text in memory:
        return translate(memory[text], "ru", user_lang)

    match = difflib.get_close_matches(text, memory.keys(), n=1, cutoff=0.75)
    if match:
        return translate(memory[match[0]], "ru", user_lang)

    answer = internet_search(text)

    if "❌ Ничего не найдено" in answer:
        msg = "Я не знаю 😕 Научи меня: запомни вопрос это ответ"
        return translate(msg, "ru", user_lang)

    return translate(answer, "ru", user_lang)

# =========================
# VOICE FIX (Kazakh safer)
# =========================
def kazakh_fix(text):
    text = text.replace("ә", "a")
    text = text.replace("і", "i")
    text = text.replace("ң", "n")
    text = text.replace("ғ", "g")
    text = text.replace("қ", "k")
    text = text.replace("ұ", "u")
    text = text.replace("ү", "u")
    text = text.replace("ө", "o")
    return text

def speak(text):
    try:
        text = re.sub(r"[^\w\sа-яА-ЯёЁ]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return

        lang = detect_lang(text)

        # 🔥 fix kazakh pronunciation
        if lang == "kk":
            text = kazakh_fix(text)
            lang = "ru"

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
# UI
# =========================
st.title("🤖 Serik AI PRO")

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
