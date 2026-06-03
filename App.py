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

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Serik AI NO API", layout="wide")

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
# LANGUAGE DETECT (FIXED)
# =========================
def detect_lang(text):
    text = text.lower()

    kz = "әіңғүұқөһ"
    kz_score = sum(1 for c in text if c in kz)
    en_score = len(re.findall(r"[a-z]", text))
    ru_score = len(re.findall(r"[а-яё]", text))

    if kz_score > 0:
        return "kk"
    elif en_score > ru_score:
        return "en"
    else:
        return "ru"

# =========================
# TRANSLATE (NO API)
# =========================
def translate(text, src="auto", dest="ru"):
    try:
        return GoogleTranslator(source=src, target=dest).translate(text)
    except:
        return text

# =========================
# MEMORY LEARN
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
# CORE BRAIN (NO GPT)
# =========================
def brain(text):

    user_lang = detect_lang(text)

    ru_text = translate(text, "auto", "ru")
    ru_text = ru_text.lower().strip()

    # memory command
    mem = handle_memory_command(ru_text)
    if mem:
        return translate(mem, "ru", user_lang)

    # exact memory
    if ru_text in memory:
        return translate(memory[ru_text], "ru", user_lang)

    # fuzzy fix
    match = difflib.get_close_matches(ru_text, memory.keys(), n=1, cutoff=0.75)
    if match:
        return translate(memory[match[0]], "ru", user_lang)

    # internet
    answer = internet_search(ru_text)
    if answer and "❌" not in answer:
        return translate(answer, "ru", user_lang)

    return translate("Я не знаю 😕 Но можешь научить меня: запомни вопрос это ответ", "ru", user_lang)

# =========================
# VOICE FIX (KAZAKH SAFE)
# =========================
def speak(text):
    try:
        text = re.sub(r"[^\w\sа-яА-ЯёЁ]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return

        # gTTS only RU fallback
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
st.title("🤖 Serik AI NO API VERSION")

st.write("🔥 Memory + multilingual + internet + learning (NO GPT)")

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
