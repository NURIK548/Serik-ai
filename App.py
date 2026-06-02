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
st.set_page_config(page_title="Serik-Ai", layout="wide")
wikipedia.set_lang("ru")

# ======================
# ДИЗАЙН
# ======================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
.stMarkdown, p, h1, h2, h3, span, label {
    color: white !important;
}
.stChatInput textarea {
    background-color: #1a1f2c !important;
    color: white !important;
    border: 1px solid #3a3f50 !important;
}
.photo-box {
    width: 100%;
    max-width: 750px;
    border-radius: 12px;
    border: 2px solid #3a3f50;
    overflow: hidden;
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

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
# SMART CONTENT (ҚАТЕСІ ТҮЗЕТІЛІП, СУРЕТІ КҮШЕЙТІЛДІ)
# ======================
def get_smart_content(q):
    q_low = q.lower().strip()

    fast_answers = {
        "привет": "Привет! Я Serik-AI готов к работе.",
        "как дела": "Отлично! Всё работает стабильно.",
        "кто тебя создал": "Меня создал Нұрик"
    }

    if q_low in fast_answers:
        return fast_answers[q_low], None

    # ======================
    # PHOTO GENERATOR (СУРЕТ САПАСЫ КҮШЕЙТІЛДІ)
    # ======================
    if any(x in q_low for x in ["фото", "картинка", "рисунок", "нарисуй"]):
        topic = q_low
        for w in ["фото", "картинку", "рисунок", "нарисуй", "сделай"]:
            topic = topic.replace(w, "")
        topic = topic.strip() or "scifi city"

        # 🔥 СУРЕТТІҢ КАЧЕСТВОСЫН КӨТЕРЕТІН СӨЗДЕР ҚОСЫЛДЫ
        hd_topic = topic + ", 8k resolution, highly detailed, masterpiece, photorealistic"
        seed = random.randint(1, 999999)
        img_url = f"https://image.pollinations.ai/p/{quote(hd_topic)}?width=1024&height=1024&seed={seed}&nofeed=true"

        html = f"""
        <div class="photo-box">
            <img src="{img_url}" style="width:100%; height:auto;">
        </div>
        """

        return f"Изображение: {topic}", html

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
    # 🛠 СУРЕТТІ ТАРИХҚА ЖАЗУ ҮШІН "image" КІЛТІН ҚОСТЫҚ
    st.session_state.messages.append({"role": "assistant", "content": welcome, "image": None})

# ======================
# DISPLAY CHAT (СУРЕТТІҢ ӨШІП ҚАЛМАУЫ ОСЫ ЖЕРДЕ ТҮЗЕТІЛДІ)
# ======================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Егер бұрын сурет салынған болса, оны экранға шығарып тұрады
        if msg.get("image"):
            st.markdown(msg["image"], unsafe_allow_html=True)

# ======================
# INPUT
# ======================
prompt = st.chat_input("Напиши запрос...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "image": None})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        text, image_html = get_smart_content(prompt)

        st.markdown(text)

        if image_html:
            st.markdown(image_html, unsafe_allow_html=True)

        audio = get_audio(text)
        if audio:
            st.audio(audio, format="audio/mp3")

        # 🛠 ЕҢ БАСТЫСЫ: Суретті тарихқа сақтап қоямыз, келесіде өшіп қалмайды!
        st.session_state.messages.append({"role": "assistant", "content": text, "image": image_html})
