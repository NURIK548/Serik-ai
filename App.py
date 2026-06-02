import streamlit as st
import wikipedia
import requests
import re
import base64
from gtts import gTTS
import io
import random
from requests.utils import quote

# ======================
# БАПТАУЛАР
# ======================
st.set_page_config(page_title="Serik-Ai PRO Max", layout="wide")
wikipedia.set_lang("ru")

# ======================
# ОБОЙ ТАҢДАУ (SIDEBAR)
# ======================
# Сол жақ мәзірде қолданушы өзіне ұнайтын обойды таңдайды
st.sidebar.title("🎨 Темы оформления")
bg_option = st.sidebar.selectbox(
    "Выберите фон для Serik-Ai:",
    ["Тёмный космос (По умолчанию)", "Киберпанк неоновый", "Матрица зелёный", "Мягкий серый", "Светлая тема"]
)

# Әр обойға сәйкес келетін CSS кодтар
bg_styles = {
    "Тёмный космос (По умолчанию)": """
        background-color: #0e1117;
        color: white;
    """,
    "Киберпанк неоновый": """
        background: linear-gradient(135deg, #120c1f 0%, #05020a 100%);
        background-attachment: fixed;
        color: #00ffcc;
    """,
    "Матрица зелёный": """
        background-color: #000000;
        color: #00ff00;
        font-family: 'Courier New', monospace;
    """,
    "Мягкий серый": """
        background-color: #2b2d42;
        color: #edf2f4;
    """,
    "Светлая тема": """
        background-color: #f8f9fa;
        color: #212529;
    """
}

selected_bg = bg_styles[bg_option]

# Кодтың ішіндегі мәтіндер таңдалған обойға қарай автоматты түрде түсін өзгертеді
text_color = "#212529" if bg_option == "Светлая тема" else "white"
if bg_option == "Матрица зелёный":
    text_color = "#00ff00"
elif bg_option == "Киберпанк неоновый":
    text_color = "#00ffcc"

# ======================
# ДИЗАЙН (ӨЗГЕРТІЛДІ)
# ======================
st.markdown(f"""
<style>
.stApp {{
    {selected_bg}
}}
.stMarkdown, p, h1, h2, h3, span, label {{
    color: {text_color} !important;
}}
.stChatInput textarea {{
    background-color: #1a1f2c !important;
    color: white !important;
    border: 1px solid #3a3f50 !important;
}}
.photo-box {{
    width: 100%;
    max-width: 750px;
    border-radius: 12px;
    border: 2px solid #3a3f50;
    overflow: hidden;
    margin: 15px 0;
}}
</style>
""", unsafe_allow_html=True)

# ======================
# ДАУЫС (TTS)
# ======================
def get_audio(text):
    try:
        clean_txt = text[:200]
        tts = gTTS(text=clean_txt, lang='ru')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# ======================
# GOOGLE / DUCKDUCKGO INFO
# ======================
def search_google_and_compose(topic):
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={quote(topic)}"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(search_url, headers=headers, timeout=6)

        if res.status_code == 200:
            snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', res.text, re.DOTALL)

            composed = ""
            for snip in snippets[:4]:
                clean = re.sub(r'<[^>]+>', '', snip).strip()
                composed += clean + " "

            return composed.strip()

    except:
        pass

    return ""

# ======================
# SMART CONTENT
# ======================
def get_smart_content(q):
    q_low = q.lower().strip()

    fast_answers = {
        "привет": "Привет! Я Serik-AI PRO Max готов к работе.",
        "как дела": "Отлично! Всё работает стабильно.",
        "кто тебя создал": "Меня создал Нурхан"
    }

    if q_low in fast_answers:
        return fast_answers[q_low], None

    # ======================
    # TEXT / WIKI
    # ======================
    topic = q.replace("напиши", "").replace("реферат", "").replace("эссе", "").replace("про", "").strip()

    wiki_summary = ""
    wiki_content = ""

    try:
        page = wikipedia.page(topic)
        wiki_summary = page.summary
        wiki_content = page.content
    except:
        pass

    google_data = search_google_and_compose(topic)

    if not wiki_summary and not google_data:
        return f"Я не нашел информацию про '{topic}'. Попробуй точнее.", None

    main = wiki_summary if wiki_summary else google_data

    # ======================
    # REF / ESSAY
    # ======================
    if "реферат" in q_low:
        text = f"""РЕФЕРАТ: {topic}

Введение:
{main}

Основная часть:
{wiki_content[:1500] if wiki_content else google_data}

Заключение:
Анализ показывает важность темы."""
        return text, None

    if "эссе" in q_low:
        text = f"""ЭССЕ: {topic}

Анализ:
{main}

Вывод: тема актуальна и интересна."""
        return text, None

    return main, None

# ======================
# CHAT INIT
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Привет! Я Serik-AI PRO Max."
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# ======================
# DISPLAY CHAT
# ======================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ======================
# INPUT
# ======================
prompt = st.chat_input("Напиши запрос...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        text, _ = get_smart_content(prompt)

        st.markdown(text)

        audio = get_audio(text)
        if audio:
            st.audio(audio, format="audio/mp3")

        st.session_state.messages.append({"role": "assistant", "content": text})
