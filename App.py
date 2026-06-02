import streamlit as st
import wikipedia
import requests
import re
import base64
from gtts import gTTS
import io
import random
from requests.utils import quote

# ==========================================
# ⚙️ БАПТАУЛАР (PAGE CONFIG)
# ==========================================
st.set_page_config(page_title="Serik-Ai PRO Max", layout="wide")
wikipedia.set_lang("ru")

# ==========================================
# 🧠 ЖАДЫНЫ ІСКЕ ҚОСУ (SESSION STATE)
# ==========================================
# Егер жады бос болса, баптаймыз
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Привет! Я Serik-Ai PRO Max. Твой личный ассистент. Прежде чем мы начнем, скажи, пожалуйста, как тебя зовут? 😊"}
    ]

# Суреттерді сақтау үшін жеке жады
if "saved_images" not in st.session_state:
    st.session_state.saved_images = []

# ==========================================
# ✨ ДИЗАЙН (CUSTOM CSS & HTML)
# ==========================================
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
.stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
.stChatInput textarea { background-color: #1a1f2c !important; color: white !important; border: 1px solid #3a3f50 !important; }
.photo-box { width: 100%; max-width: 750px; border-radius: 12px; border: 2px solid #3a3f50; overflow: hidden; margin: 15px 0; }
div.stButton > button { background-color: #4A90E2 !important; color: white !important; width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Serik-Ai Ваш Личный помощник")
st.write("что хотите спросите (он может ошибатся):")

# ==========================================
# 🌐 ФУНКЦИЯЛАР (СУРЕТ, ДАУЫС, ЖИ МИЫ)
# ==========================================

# 1. Тілді анықтау функциясы
def detect_lang(text):
    if re.search(r'[ӘәҒғҚқҢңӨөҰұҮүҺһІі]', text):
        return "kk"
    keywords = ["привет", "меня зовут", "как дела", "фото", "картинка", "нарисуй", "эссе", "реферат", "скачать"]
    if any(w in text.lower() for w in keywords):
        return "ru"
    return "kk" # Базалық тіл

# 2. Суретті HD сапада тарту функциясы
def draw_image(prompt_text):
    seed = random.randint(1, 999999)
    # Керемет сапа беретін баптаулар қосылды
    hd_prompt = prompt_text + ", 8k resolution, highly detailed, photorealistic, cinematic lighting"
    url = f"https://image.pollinations.ai/p/{quote(hd_prompt)}?width=1024&height=1024&seed={seed}&nofeed=true"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.content, url
    except:
        pass
    return None, None

# 3. Дауыс шығару (TTS) функциясы
def get_audio(text, lang='ru'):
    try:
        clean_txt = re.sub(r'<[^>]+>', '', text)[:200]
        tts = gTTS(text=clean_txt, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# 4. Пайдаланушының қатесін кешіріп, түзетіп жазатын ЖИ Миы
def ask_ai(user_prompt, name, web_context=""):
    try:
        system = (
            f"Ты ИИ-ассистент Серік-Ай PRO Max. Разговаривай абсолютно естественно, как живой человек и близкий друг. "
            f"Пользователя зовут {name if name else 'Друг'}. Обращайся к нему по имени! "
            f"Ты должен автоматически понимать запросы, даже если в них куча грамматических и смысловых ошибок (скачатт, нест, істецді). "
            f"Если передан контекст из интернета/Википедии, используй эти данные, чтобы написать огромный, мощный реферат, сочинение или эссе "
            f"с введением, основной частью и заключением. Пиши красиво, не используй сухие шаблоны. "
            f"Отвечай строго на языке пользователя (казахский или русский)."
        )
        payload = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": user_prompt}], "model": "openai"}
        res = requests.post("https://text.pollinations.ai/", json=payload, timeout=15)
        if res.status_code == 200:
            return res.text
    except:
        pass
    return "Байланыс үзілді..."

# ==========================================
# 🖼 БӨЛІМ 1: ЕСКІ СУРЕТТЕРДІ КӨРСЕТУ
# ==========================================
# Ескі салынған суреттерді жоғалтпай экранға тізіп тұру
for img in st.session_state.saved_images:
    st.markdown(f"🔹 **{img['title']}**")
    st.markdown(img['html'], unsafe_allow_html=True)
    import random
    st.download_button("📥 Скачать фото", data=img['bytes'], file_name="photo.png", mime="image/png", key=f"dl_{random.randint(1,99999)}")
    st.markdown("---")

# ==========================================
# 💬 БӨЛІМ 2: ЧАТ ТАРИХЫН КӨРСЕТУ
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 📥 ЧАТ ЕНГІЗУ ЖОЛЫ МЕН НЕГІЗГІ ЛОГИКА
# ==========================================
prompt = st.chat_input("Напиши запрос...")

if prompt:
    # 1. Пайдаланушының сөзін тарихқа сақтау
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Тілді анықтау
    lang = detect_lang(prompt)

    # 3. Жауап дайындау
    with st.chat_message("assistant"):
        with st.spinner("Задумываюсь..."):

            # 🚨 А) СУРЕТ САЛУ ШАРТЫ (ҚАТЕСІ ТҮЗЕТІЛГЕН ОРЫСШАЛАНҒАН НҰСҚА)
            if any(x in prompt.lower() for x in ["фото", "картинка", "рисунок", "нарисуй"]):
                topic = prompt.lower()
                for w in ["фото", "картинку", "рисунок", "нарисуй", "сделай", "сал", "сурет"]:
                    topic = topic.replace(w, "")
                topic = topic.strip() or "cyberpunk city landscape"
                
                # Суретті ең жоғары сапада (HD) генерациялау
                bytes_data, img_url = draw_image(topic)
                
                if bytes_data:
                    # Суретті көрсету үшін HTML
                    img_html = f'<div class="photo-box"><img src="{img_url}" style="width:100%;"></div>'
                    # Орысша жауап құрастыру
                    reply = f"🎨 **Вот, твой рисунок готов:** *{topic}*"
                    
                    # Суретті чат тарихына (сессияға) шегелеп сақтаймыз!
                    st.session_state.saved_images.append({
                        "title": topic,
                        "html": img_html,
                        "bytes": bytes_data
                    })
                    
                    # Экранға шығару
                    st.markdown(reply)
                    st.markdown(img_html, unsafe_allow_html=True)
                    
                    # Скачать батырмасы (Әр суретке бөлек ID береміз, сонда код қатып қалмайды)
                    import random
                    st.download_button(
                        "📥 Скачать фото", 
                        data=bytes_data, 
                        file_name="photo.png", 
                        mime="image/png", 
                        key=f"dl_{random.randint(1,999999)}"
                    )
                    
                    # 🔥 БОТ ЕКІНШІ РЕТТЕ КЕПТЕЛІП ҚАЛМАУЫ ҮШІН БЕТТІ ЖАҢАРТАМЫЗ!
                    st.rerun()
                else:
                    st.error("Ошибка сервера картинок. Попробуй еще раз через секунду.")
                    reply = "Ошибка при генерации изображения."

            # Б) ЕСІМДІ ЖАТТАП АЛУ ШАРТЫ
            elif st.session_state.user_name is None:
                # Пайдаланушы атын айтқанша, ЖИ жауап бермейді
                st.session_state.user_name = prompt
                reply = f"🎉 Танысқанымызға қуаныштымын, **{prompt}**! Өте әдемі есім. Енді мен сенің көмекшіңмін. Не істейміз? 😉"

            # В) ЖАЙ ЧАТ НЕМЕСЕ РЕФЕРАТ ІЗДЕУ ШАРТЫ
            else:
                combined_context = ""
                # Реферат сұраса, Википедия мен Интернеттен мәлімет жинаймыз
                if any(x in prompt.lower() for x in ["реферат", "эссе", "туралы", "мәлімет", "что такое", "кім"]):
                    search_query = prompt.lower()
                    for w in ["реферат", "эссе", "жазып бер", "туралы", "мәлімет", "что такое", "кім"]:
                        search_query = search_query.replace(w, "")
                    search_query = search_query.strip()
                    
                    try:
                        combined_context = wikipedia.summary(search_query, sentences=3)
                    except:
                        combined_context = "" # Мәлімет табылмаса, бос қалдырамыз

                # ЖИ Миымен сөйлем құрастыру
                reply = ask_ai(prompt, st.session_state.user_name, combined_context)

        # 4. Жауапты тарихқа сақтау және дауыстау
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.markdown(reply)
        
        # Дауысты шығару
        audio_data = get_audio(reply, lang=lang)
        if audio_data:
            st.audio(audio_data, format="audio/mp3", autoplay=True)
