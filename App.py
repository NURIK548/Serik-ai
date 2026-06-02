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

# Пайдаланушының қатесін кешіріп, түзетіп жазатын ЖИ Миы
def ask_ai(user_prompt, name, web_context=""):
    try:
        # МАНЫЗДЫ НҰСҚАУЛЫҚ (ЖИ-дің ережесі)
        system = (
            f"Ты ИИ-ассистент Серік-Ай PRO Max. Разговаривай абсолютно естественно, как живой человек и близкий друг. "
            f"Пользователя зовут {name if name else 'Друг'}. Обращайся к нему по имени! "
            # МІНЕ, ҚАТЕНІ ТҮЗЕТЕТІН БАСТЫ НҰСҚАУ:
            f"Ты должен автоматически понимать запросы, даже если в них куча грамматических и смысловых ошибок (например, 'нест', 'істецді', 'скачатт'). "
            f"Если передан контекст из интернета/Википедии, используй эти данные, чтобы написать огромный, мощный реферат, сочинение или эссе "
            f"с введением, основной частью и заключением. Пиши красиво, не используй сухие шаблоны. "
            f"Отвечай строго на языке пользователя (казахский или русский)."
        )
        
        full_prompt = user_prompt
        if web_context:
            full_prompt = f"Найденная информация из интернета:\n{web_context}\n\nЗапрос пользователя: {user_prompt}"

        # Сұранысты OpenAi моделіне жіберу (ол қате сөздерді автоматты түрде өңдейді)
        payload = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": full_prompt}
            ],
            "model": "openai" # Ең ақылды модель қателерді өзі түзеп оқиды
        }
        res = requests.post("https://text.pollinations.ai/", json=payload, timeout=15)
        if res.status_code == 200:
            return res.text
    except:
        pass
    return "Байланыс үзілді..."

import streamlit as st
import requests
import random
from requests.utils import quote

# Беттің баптаулары
st.set_page_config(page_title="Serik-Ai Фото Генератор", layout="wide")

# Қараңғы стиль (Дизайн)
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
.stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
.stChatInput textarea { background-color: #1a1f2c !important; color: white !important; }
.photo-box { width: 100%; max-width: 600px; border-radius: 12px; border: 3px solid #4A90E2; overflow: hidden; margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Serik-Ai Ваш Личный помощник")
st.write("что хотите спросите (он может ошибатся):")

# Сурет тарту функциясы
def draw_image(prompt_text):
    seed = random.randint(1, 999999)
    # HD сапа беретін баптаулар қосылды
    hd_prompt = prompt_text + ", 8k resolution, highly detailed, photorealistic"
    url = f"https://image.pollinations.ai/p/{quote(hd_prompt)}?width=1024&height=1024&seed={seed}&nofeed=true"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.content, url
    except:
        pass
    return None, None

# Сессияда суреттер тізімін сақтау (Бұрынғы салынған суреттер жоғалмауы үшін)
if "saved_images" not in st.session_state:
    st.session_state.saved_images = []

# Ескі салынған суреттерді экранға тізіп көрсету
for img in st.session_state.saved_images:
    st.markdown(f"🔹 **{img['title']}**")
    st.markdown(img['html'], unsafe_allow_html=True)
    st.download_button(
        "📥 Скачать фото", 
        data=img['bytes'], 
        file_name="photo.png", 
        mime="image/png", 
        key=f"dl_{random.randint(1, 999999)}"
    )
    st.markdown("---")

# Жаңа сұраныс енгізу өрісі (Ең астында тұрады)
user_input = st.chat_input("Қандай сурет саламыз? (Мысалы: Мерседес бандитский / БМВ в неоне)...")

if user_input:
    with st.spinner("Сурет салынып жатыр, күте тұр..."):
        bytes_data, img_url = draw_image(user_input)
        
        if bytes_data:
            img_html = f'<div class="photo-box"><img src="{img_url}" style="width:100%;"></div>'
            
            # Жаңа суретті тізімге қосып қоямыз
            st.session_state.saved_images.append({
                "title": user_input,
                "html": img_html,
                "bytes": bytes_data
            })
            
            # 🔥 МАНЫЗДЫ: Код кептеліп қалмай, келесі суретті де шексіз салу үшін бетті жаңартамыз!
            st.rerun()
        else:
            st.error("Сурет салу сервері жауап бермеді. Қайтадан байқап көрші.")
            
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
        "привет": "Привет! Я Serik-AI готов к работе.",
        "как дела": "Отлично! Всё работает стабильно.",
        "кто тебя создал": "Меня создал Нурхан"
    }

    if q_low in fast_answers:
        return fast_answers[q_low], None

    # ======================
    # PHOTO GENERATOR
    # ======================
    if any(x in q_low for x in ["фото", "картинка", "рисунок", "нарисуй"]):
        topic = q_low
        for w in ["фото", "картинку", "рисунок", "нарисуй", "сделай"]:
            topic = topic.replace(w, "")
        topic = topic.strip() or "scifi city"

        seed = random.randint(1, 999999)
        img_url = f"https://image.pollinations.ai/p/{quote(topic)}?width=800&height=600&seed={seed}&nofeed=true"

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
        text, image_html = get_smart_content(prompt)

        st.markdown(text)

        if image_html:
            st.markdown(image_html, unsafe_allow_html=True)

        audio = get_audio(text)
        if audio:
            st.audio(audio, format="audio/mp3")

        st.session_state.messages.append({"role": "assistant", "content": text})
