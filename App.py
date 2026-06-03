import streamlit as st
import json
import difflib
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS
import os
import re
import base64
from deep_translator import GoogleTranslator

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

if "learning_mode" not in st.session_state:
    st.session_state.learning_mode = False

if "last_question" not in st.session_state:
    st.session_state.last_question = None

# 🔥 LANGUAGE MODE ADDED
if "lang_mode" not in st.session_state:
    st.session_state.lang_mode = "AUTO"  # RU / KZ / AUTO

# =========================
# MEMORY LOAD
# =========================
def load_memory():
    def detect_lang(text):
        try:
            if re.search(r"[а-яА-ЯёЁ]",
    text):
                if any(x in text.lower() for
    x in "әіңғүұқөһ"):
                    return "kk"
                return "ru"
        
            elif re.search(r"[a-zA-Z]",
    text):
                return "en"
        
            return "ru"
        except:
            return "ru"


def translate_text(text, source="auto", target="ru"):
    try:
        return GoogleTranslator(
            source=source,
            target=target
        ).translate(text)
    except:
        return text
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

memory = load_memory()

def save_memory():
    with open("memory_base.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

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
# MEMORY SYSTEM
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
# LANGUAGE RESPONSE
# =========================
def translate_response(text):

    mode = st.session_state.lang_mode

    if mode == "RU":
        return text

    if mode == "KZ":
        # өте қарапайым қазақша ауыстыру (basic)
        text = text.replace("Привет", "Сәлем")
        text = text.replace("Я не знаю", "Мен білмеймін")
        text = text.replace("Запомнил", "Есімде сақталды")
        return text

    # AUTO
    return text

# =========================
# BRAIN
# =========================
def brain(text):

    user_lang = detect_lang(text)

    ru_text = translate_text(text, "auto", "ru")
    text = ru_text.lower().strip()

    mem = handle_memory_command(text)
    if mem:
        return translate_text(mem, "ru", user_lang)

    if text in memory:
        return translate_text(memory[text], "ru", user_lang)

    match = difflib.get_close_matches(text, memory.keys(), n=1, cutoff=0.75)
    if match:
        return translate_text(memory[match[0]], "ru", user_lang)

    answer = internet_search(text)

    if "❌ Ничего не найдено" in answer:
        st.session_state.learning_mode = True
        st.session_state.last_question = text
        return translate_text("Я не знаю 😕 Научи меня: запомни вопрос это ответ", "ru", user_lang)

    return translate_text(answer, "ru", user_lang)

# =========================
# VOICE
# =========================
def speak(text):
    try:
        text = clean_text(text)
        text = re.sub(r"[^\w\sа-яА-ЯёЁ]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return

        # 🔥 language voice
        lang = "ru"
        if st.session_state.lang_mode == "KZ":
            lang = "ru"  # gTTS қазақша толық жоқ, RU fallback

        tts = gTTS(text=text[:300], lang=lang)
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
st.sidebar.title("⚙️ Menu")

# language switch
st.sidebar.subheader("🌐 Language Mode")
st.session_state.lang_mode = st.sidebar.selectbox(
    "Mode",
    ["AUTO", "RU", "KZ"]
)

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
st.write("💬 Multi-language AI (RU / KZ / AUTO)")

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

    if st.session_state.learning_mode and prompt.startswith("запомни "):
        st.session_state.learning_mode = False
        st.session_state.last_question = None

    speak(response)
