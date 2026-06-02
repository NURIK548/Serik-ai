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
            snippets = re.findall(r'<a class="result__snippet".=.*?>(.*?)</a>', res.text, re.DOTALL)
            composed = ""
            for snip in snippets[:4]:
                clean = re.sub(r'<[^>]+>', '', snip).strip()
                composed += clean + " "
            return composed.strip()
    except:
        pass
    return ""

# ======================
# СВОБОДНОЕ ОБЩЕНИЕ (ChatGPT / Gemini СИЯҚТЫ)
# ======================
def chat_with_ai(user_prompt):
    """Пайдаланушымен кез келген тақырыпта шексіз әрі еркін сөйлесетін ақылды AI"""
    try:
        # Тұрақты әрі ақылды мәтіндік модель (Llama-3/GPT деңгейінде)
        api_url = f"https://text.pollinations.ai/{quote(user_prompt)}?system=Ты+интеллектуальный+ассистент+Serik-AI+созданный+Нурханом.+Ты+умеешь+поддерживать+любую+беседу+как+ChatGPT+и+Gemini.+Отвечай+всегда+на+языке+пользователя+живо+и+интересно."
        res = requests.get(api_url, timeout=15)
        if res.status_code == 200:
            return res.text.strip()
    except:
        pass
    return "Я тут, давай поболтаем! О чём думаешь? 😊"

# ======================
# SMART CONTENT
# ======================
def get_smart_content(q):
    q_low = q.lower().strip()

    # ТҮЗЕТІЛДІ: Егер қолданушы нақты реферат немесе эссе сұраса ғана интернеттен іздейді
    if "реферат" in q_low or "эссе" in q_low or "напиши доклад" in q_low:
        topic = q.replace("напиши", "").replace("реферат", "").replace("эссе", "").replace("pro", "").replace("про", "").strip()
        
        wiki_summary = ""
        wiki_content = ""
        try:
            page = wikipedia.page(topic)
            wiki_summary = page.summary
            wiki_content = page.content
        except:
            pass

        google_data = search_google_and_compose(topic)
        main = wiki_summary if wiki_summary else google_data

        if "реферат" in q_low and main:
            return f"РЕФЕРАТ: {topic}\n\nВведение:\n{main}\n\nОсновная часть:\n{wiki_content[:1500] if wiki_content else google_data}\n\nЗаключение:\nАнализ показывает важность темы."
        elif "эссе" in q_low and main:
            return f"ЭССЕ: {topic}\n\nАнализ:\n{main}\n\nВывод: тема актуальна и интересна."

    # ТҮЗЕТІЛДІ: Қалған жағдайдың бәрінде (привет, как дела, не істеп жатырсың, т.б.) таза нейросеть ретінде еркін сөйлесе береді
    return chat_with_ai(q)

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
        with st.spinner("Ойланып жатырмын..."):
            text = get_smart_content(prompt)

        st.markdown(text)

        audio = get_audio(text)
        if audio:
            st.audio(audio, format="audio/mp3")

        st.session_state.messages.append({"role": "assistant", "content": text})
