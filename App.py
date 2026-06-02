import streamlit as st
import requests
import re
import random
import io
from gtts import gTTS  # Дауыс беру кітапханасы
from requests.utils import quote

# ======================
# НАСТРОЙКИ СЕССИИ
# ======================
st.set_page_config(page_title="Serik-Ai PRO Max", layout="wide")

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Сенің нұсқаң бойынша өзгертілген алғашқы сәлемдесу
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "👋 Ооо сәлем мен Серік-Аймын! Алдымен атыңды айтсаң, жаттап алайын? 😊"
    })

# ======================
# ДИЗАЙН (CSS)
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
    max-width: 700px;
    border-radius: 12px;
    border: 3px solid #4A90E2;
    overflow: hidden;
    margin: 15px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# ======================
# ТІЛДІ АНЫҚТАУ (Аудио үшін)
# ======================
def detect_text_language(text):
    kz_chars = re.compile(r'[ӘәҒғҚқҢңӨөҰұҮүҺһІі]')
    if kz_chars.search(text):
        return "kk"
    # Егер қазақша әріптер болмаса, бірақ қазақша сөздер болса
    kz_words = ["сәлем", "атым", "серік", "танысқанымызға", "қуаныштымын", "сурет", "сал"]
    if any(w in text.lower() for w in kz_words):
        return "kk"
    return "ru"

# ======================
# ДАУЫС ПЕН АУДИО ЖҮЙЕСІ (TTS)
# ======================
def get_audio(text, lang):
    try:
        # Аудио дұрыс шығуы үшін смайликтерді тазалаймыз
        clean_txt = re.sub(r'[^\w\s,.!?—\-]', '', text)
        clean_txt = clean_txt[:250] # Тым ұзақ мәтінді шектеу
        
        tts = gTTS(text=clean_txt, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# ======================
# СУРЕТ ГЕНЕРАТОРЫ (HD)
# ======================
def generate_hd_image(prompt_text):
    hd_enhancers = ", 8k resolution, highly detailed, masterpiece, cinematic lighting, photorealistic"
    full_prompt = prompt_text + hd_enhancers
    seed = random.randint(1, 999999)
    img_url = f"https://image.pollinations.ai/p/{quote(full_prompt)}?width=1024&height=1024&seed={seed}&nofeed=true"
    
    try:
        response = requests.get(img_url, timeout=15)
        if response.status_code == 200:
            return response.content, img_url
    except:
        pass
    return None, None

# ======================
# ЖАСАНДЫ ИНТЕЛЛЕКТ (AI Brain)
# ======================
def ask_ai_brain(user_prompt, name):
    try:
        system_instruction = (
            f"Ты — ИИ-ассистент по имени Серік-Ай PRO Max. Ты разговариваешь точно как живой человек, "
            f"как близкий друг пользователя. Пользователя зовут: {name if name else 'Друг'}. Обязательно часто обращайся к нему по имени! "
            f"Общайся свободно, используй смайлики (emoji), шути, спрашивай как дела. "
            f"Если пользователь пишет с ошибками (например, 'салем қалайсың нест', 'істецді', 'как сен сияқты'), ты должен "
            f"автоматически понимать суть и отвечать очень дружелюбно и естественно. "
            f"Отвечай строго на том языке, на котором к тебе обратились (казахский или русский). "
            f"Если просят реферат или эссе, то пиши развернуто и грамотно, но в самом чате веди себя как живой собеседник."
        )
        
        url = "https://ai.fakeopen.com/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8
        }
        
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
    except:
        pass
    
    if name:
        return f"Ой, {name}, интернет сәл нашарлап кетті. Қайтадан жазып жіберші? 😊"
    return "Интернет сәл қатып тұр, қайтадан жазып көрші?"

# ======================
# СМАРТ КОНТЕНТ МЕНЕДЖЕР
# ======================
def get_smart_content(q):
    q_low = q.lower().strip()

    if any(x in q_low for x in ["фото", "картинка", "рисунок", "нарисуй", "сурет", "істецді", "сал"]):
        topic = q_low
        for w in ["фото", "картинку", "рисунок", "нарисуй", "сделай", "сурет", "салып бер", "сал", "істецді"]:
            topic = topic.replace(w, "")
        topic = topic.strip() or "creative neon art"

        img_bytes, img_url = generate_hd_image(topic)
        if img_bytes:
            html = f'<div class="photo-box"><img src="{img_url}" style="width:100%; height:auto;"></div>'
            name_part = f", {st.session_state.user_name}" if st.session_state.user_name else ""
            msg_text = f"🎨 **Мінекей{name_part}, сұраған суретіңді өзім құрастырып шықтым:** *{topic}*"
            return msg_text, html, img_bytes
        else:
            return "Қап, сурет салатын серверім сәл шаршап қалыпты. Қайтадан басып көрші?", None, None

    ai_response = ask_ai_brain(q, st.session_state.user_name)
    return ai_response, None, None

# ======================
# ЧАТ ТАРИХЫН КӨРСЕТУ
# ======================
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_html" in msg and msg["image_html"]:
            st.markdown(msg["image_html"], unsafe_allow_html=True)
        if "image_bytes" in msg and msg["image_bytes"]:
            st.download_button(
                label="📥 Жүктеп алу / Скачать фото",
                data=msg["image_bytes"],
                file_name=f"serik_ai_{i}.png",
                mime="image/png",
                key=f"dl_{i}"
            )

# ======================
# ЕНГІЗУ ӨРІСІ ЖӘНЕ ДАУЫСТЫ БІРДЕН ОЙНАТУ
# ======================
prompt = st.chat_input("Серікке жаз...")

if prompt:
    # 1. Пайдаланушының хабарламасын көрсету және сақтау
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Жауапты өңдеу
    with st.chat_message("assistant"):
        # ЕГЕР АТЫ ӘЛІ ЖАТТАЛМАҒАН БОЛСА
        if st.session_state.user_name is None:
            clean_name = prompt.replace("Менің атым", "").replace("меня зовут", "").replace("мен", "").replace("атым", "").strip()
            st.session_state.user_name = clean_name
            
            answer_text = f"🎉 Мәссаған, танысқанымызға өте қуаныштымын, **{clean_name}**! Атыңды миыма толық жазып алдым. Енді біз нағыз достармыз! Не істейміз? 😉"
            image_html, image_bytes = None, None
        
        # ЕГЕР АТЫ БҰРЫННАН БЕЛГІЛІ БОЛСА
        else:
            answer_text, image_html, image_bytes = get_smart_content(prompt)
        
        # Экранға мәтінді шығару
        st.markdown(answer_text)
        
        # Егер сурет болса шығару
        if image_html:
            st.markdown(image_html, unsafe_allow_html=True)
        if image_bytes:
            st.download_button(
                label="📥 Жүктеп алу / Скачать фото",
                data=image_bytes,
                file_name="serik_ai_photo.png",
                mime="image/png",
                key="dl_current"
            )
        
        # ДАУЫСТЫ ОЙНАТУ (Бет жаңармай тұрып бірден шығады)
        lang = detect_text_language(answer_text)
        audio_file = get_audio(answer_text, lang)
        if audio_file:
            st.audio(audio_file, format="audio/mp3", autoplay=True) # autoplay=True автоматты түрде сөйлейді
            
        # Жауапты сессияға сақтаймыз
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer_text, 
            "image_html": image_html,
            "image_bytes": image_bytes
        })
