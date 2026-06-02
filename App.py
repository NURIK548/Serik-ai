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
st.sidebar.title("🎨 Темы оформления")
bg_option = st.sidebar.selectbox(
    "Выберите фон для Serik-Ai:",
    ["Тёмный космос (По умолчанию)", "Киберпанк neon", "Матрица green", "Мягкий серый", "Светлая тема"]
)

bg_styles = {
    "Тёмный космос (По умолчанию)": "background-color: #0e1117; color: white;",
    "Киберпанк neon": "background: linear-gradient(135deg, #120c1f 0%, #05020a 100%); background-attachment: fixed; color: #00ffcc;",
    "Матрица green": "background-color: #000000; color: #00ff00; font-family: 'Courier New', monospace;",
    "Мягкий серый": "background-color: #2b2d42; color: #edf2f4;",
    "Светлая тема": "background-color: #f8f9fa; color: #212529;"
}

selected_bg = bg_styles[bg_option]

text_color = "white"
if bg_option == "Светлая тема":
    text_color = "#212529"
elif bg_option == "Матрица green":
    text_color = "#00ff00"
elif bg_option == "Киберпанк neon":
    text_color = "#00ffcc"

# ======================
# ДИЗАЙН
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
</style>
""", unsafe_allow_html=True)

# ======================
# ДАУЫС (TTS) - СМАЙЛИК ПЕН НҮКТЕЛЕР ОҚЫЛМАЙДЫ
# ======================
def get_audio(text):
    try:
        clean_txt = text[:200]
        
        # ТҮЗЕТІЛДІ: Смайликтерді (Emoji) мәтіннен толық өшіру
        clean_txt = re.sub(r'[\U00010000-\U0010ffff]|\u263a|\u263b', '', clean_txt)
        
        # ТҮЗЕТІЛДІ: Нүкте, үтір және басқа тыныс белгілерін дыбыстамау үшін бос орынға ауыстыру
        clean_txt = re.sub(r'[.,\/#!$%\^&\*;:{}=\-_`~()?"\n]', ' ', clean_txt)
        
        clean_txt = re.sub(r'\s+', ' ', clean_txt).strip()

        if clean_txt:
            tts = gTTS(text=clean_txt, lang='ru')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp
    except:
        return None
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
# ЧАТ МОДЕЛІ (ChatGPT / Gemini СИЯҚТЫ)
# ======================
def chat_with_ai(user_prompt):
    try:
        # ТҮЗЕТІЛДІ: Тек қана орыс тілінде еркін әңгімелесу нұсқауы берілді
        api_url = f"https://text.pollinations.ai/{quote(user_prompt)}?system=Ты+интеллектуальный+ассистент+Serik-AI+созданный+Нурханом.+Ты+умеешь+поддерживать+любую+беседу+как+ChatGPT+и+Gemini.+Отвечай+всегда+СТРОГО+на+русском+языке+живо+и+интересно."
        res = requests.get(api_url, timeout=15)
        if res.status_code == 200:
            return res.text.strip()
    except:
        pass
    return "Я тут, давай поболтаем! О чём думаешь? 😊"

# ======================
# SMART CONTENT (ЕСКІ НҰСҚА ҚАЛПЫНА КЕЛТІРІЛДІ)
# ======================
def get_smart_content(q):
    q_low = q.lower().strip()

    fast_answers = {
        "привет": "Привет! Я Serik-AI PRO Max готов к работе.",
        "как дела": "Отлично! Всё работает стабильно.",
        "кто тебя создал": "Меня создал Нурхан"
    }

    if q_low in fast_answers:
        return fast_answers[q_low]

    # ТҮЗЕТІЛДІ: Егер қолданушы жай ғана сөйлесіп жатса (реферат/эссе демесе), бірден ЧАТ режим қосылады
    if "реферат" not in q_low and "эссе" not in q_low:
        return chat_with_ai(q)

    # НАҚТЫ ЕСКІ ОРИГИНАЛ КОД (ЕШҚАНДАЙ ӨЗГЕРІССІЗ РЕФЕРАТ ПЕН ЭССЕ БӨЛІМІ)
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
        return chat_with_ai(q)

    main = wiki_summary if wiki_summary else google_data

    if "реферат" in q_low:
        text = f"""РЕФЕРАТ: {topic}

Введение:
{main}

Основная часть:
{wiki_content[:1500] if wiki_content else google_data}

Заключение:
Анализ показывает важность темы."""
        return text

    if "эссе" in q_low:
        text = f"""ЭССЕ: {topic}

Анализ:
{main}

Вывод: тема актуальна и интересна."""
        return text

    return main

# ======================
# CHAT INIT
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Привет! Я Serik-AI PRO Max. Как дела? О чём поговорим сегодня?"
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
        with st.spinner("Думаю..."):
            text = get_smart_content(prompt)

        st.markdown(text)

        audio = get_audio(text)
        if audio:
            st.audio(audio, format="audio/mp3")

        st.session_state.messages.append({"role": "assistant", "content": text})
