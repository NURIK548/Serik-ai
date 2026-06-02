import streamlit as st
import requests
import re
import random
import io
from gtts import gTTS
from requests.utils import quote

st.set_page_config(page_title="Serik-Ai PRO Max", layout="wide")

# ЖАДЫНЫ ІСКЕ ҚОСУ
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Ооо сәлем мен Серік-Аймын! Алдымен атыңды айтсаң, жаттап алайын? 😊"}
    ]

# ДИЗАЙН (ҚАРАҢҒЫ СТИЛЬ)
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
.stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
.stChatInput textarea { background-color: #1a1f2c !important; color: white !important; }
.photo-box { width: 100%; max-width: 600px; border-radius: 12px; border: 3px solid #4A90E2; overflow: hidden; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ТІЛДІ ТАНУ ЖҮЙЕСІ
def detect_lang(text):
    if re.search(r'[ӘәҒғҚқҢңӨөҰұҮүҺһІі]', text) or any(w in text.lower() for w in ["сәлем", "атым", "серік", "нест", "қалай", "реферат", "мәлімет"]):
        return "kk"
    return "ru"

# АУТО-ДАУЫС ЖАСАУ (TTS)
def make_voice(text, lang):
    try:
        clean_txt = re.sub(r'[^\w\s,.!?—\-]', '', text)
        clean_txt = clean_txt[:200] # Аудио қатып қалмау үшін басын ғана оқиды
        tts = gTTS(text=clean_txt, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# СУРЕТ САЛУ ГЕНЕРАТОРЫ
def draw_image(prompt_text):
    seed = random.randint(1, 999999)
    url = f"https://image.pollinations.ai/p/{quote(prompt_text)}?width=1024&height=1024&seed={seed}&nofeed=true"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.content, url
    except:
        pass
    return None, None

# 🌐 1-КӨЗ: ВЕБ-БРАУЗЕРДЕН ІЗДЕУ (DUCKDUCKGO БАЗАСЫ)
def search_duckduckgo(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        # DuckDuckGo-ның жеңіл нұсқасынан ақпаратты html түрінде суырып алу
        res = requests.get(f"https://html.duckduckgo.com/html/?q={quote(query)}", headers=headers, timeout=8)
        if res.status_code == 200:
            # Сұранысқа сай сайттардың қысқаша үзінділерін (snippets) жинау
            snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', res.text, re.DOTALL)
            cleaned = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets]
            return "\n".join(cleaned[:3]) # Ең үздік 3 сайттың мәліметі
    except:
        pass
    return ""

# 🌐 2-КӨЗ: ВІКІPEDIA API
def fetch_wikipedia(topic, lang):
    try:
        wiki_lang = "kk" if lang == "kk" else "ru"
        url = f"https://{wiki_lang}.wikipedia.org/api/rest_v1/page/summary/{quote(topic)}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("extract", "")
    except:
        pass
    return ""

# ОРАСАН ЗОР ЖИ МИЫ (Контекст жинағыш)
def ask_ai(user_prompt, name, web_context=""):
    try:
        system = (
            f"Ты ИИ-ассистент Серік-Ай PRO Max. Разговаривай абсолютно естественно, как живой человек и близкий друг. "
            f"Пользователя зовут {name if name else 'Друг'}. Обращайся к нему по имени! "
            f"Ты должен автоматически понимать запросы, даже если в них куча грамматических и смысловых ошибок (например, 'нест', 'істецді', 'скачатт'). "
            f"Если передан контекст из интернета/Википедии, используй эти данные, чтобы написать огромный, мощный реферат, сочинение или эссе "
            f"с введением, основной частью и заключением. Пиши красиво, не используй сухие шаблоны. "
            f"Отвечай строго на языке пользователя (казахский или русский)."
        )
        
        full_prompt = user_prompt
        if web_context:
            full_prompt = f"Найденная информация из интернета и браузеров:\n{web_context}\n\nЗапрос пользователя: {user_prompt}"

        payload = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": full_prompt}
            ],
            "model": "openai"
        }
        res = requests.post("https://text.pollinations.ai/", json=payload, timeout=15)
        if res.status_code == 200:
            return res.text
    except:
        pass
    return f"Ой, {name if name else 'досым'}, интернеттен мәлімет іздеу кезінде байланыс үзілді. Қайтадан жазып жіберші? 😊"

# ЕСКІ ЧАТ ТАРИХЫН ШЫҒАРУ
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img_html" in msg and msg["img_html"]:
            st.markdown(msg["img_html"], unsafe_allow_html=True)
            st.download_button("📥 Скачать фото", data=msg["img_bytes"], file_name="photo.png", mime="image/png", key=random.randint(1,9999))

# ЖАҢА СҰРАНЫС ЕНГІЗУ ӨРІСІ
user_input = st.chat_input("Серікке жаз (мысалы: 'Кенесары хан туралы реферат')")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        img_html, img_bytes = None, None
        lang = detect_lang(user_input)
        
        # 1. АТЫ ӘЛІ ЖАТТАЛМАҒАН БОЛСА
        if st.session_state.user_name is None:
            name = user_input.replace("Менің атым", "").replace("меня зовут", "").replace("мен", "").replace("атым", "").strip()
            st.session_state.user_name = name
            reply = f"🎉 Мәссаған, танысқанымызға қуаныштымын, **{name}**! Атыңды миыма толық тоқып алдым. Енді біз нағыз достармыз! Маған реферат жазғызсаң да, 59 сайтты тінткізсең де бәрін тауып берем! Не істейміз? 😉"
        
        # 2. СУРЕТ САЛУ СҰРАЛСА
        elif any(x in user_input.lower() for x in ["фото", "картинка", "рисунок", "нарисуй", "сурет", "сал"]):
            topic = user_input.lower()
            for w in ["фото", "картинку", "рисунок", "нарисуй", "сурет", "сал"]:
                topic = topic.replace(w, "")
            topic = topic.strip() or "epic cyber landscape"
            
            bytes_data, img_url = draw_image(topic)
            if bytes_data:
                img_html = f'<div class="photo-box"><img src="{img_url}" style="width:100%;"></div>'
                img_bytes = bytes_data
                reply = f"🎨 **Міне, {st.session_state.user_name}, сұраған суретіңді ғаламтордан құрастырып шықтым:** *{topic}*"
            else:
                reply = "Сурет серверінде қате шықты, сәлден кейін қайта басып көрші?"
        
        # 3. ЕРКІН ӘҢГІМЕ НЕУ СЕРФИНГ (БРАУЗЕР + ВИКИПЕДИЯ ІСКЕ ҚОСЫЛАДЫ)
        else:
            combined_context = ""
            # Егер реферат, эссе немесе бір мәлімет сұралса, қос іздеу жүйесі қосылады
            if any(x in user_input.lower() for x in ["реферат", "эссе", "туралы", "мәлімет", "про", "что такое", "кім", "не"]):
                search_query = user_input.lower()
                for w in ["реферат", "эссе", "жазып бер", "туралы", "мәлімет", "скажи", "напиши", "про", "что такое"]:
                    search_query = search_query.replace(w, "")
                search_query = search_query.strip()
                
                # 1-көз: Википедия дерегі
                wiki_data = fetch_wikipedia(search_query, lang)
                # 2-көз: DuckDuckGo арқылы басқа браузер-сайттардың дерегі
                ddg_data = search_duckduckgo(search_query)
                
                # Екеуін бір контекстке біріктіру
                combined_context = f"Википедия: {wiki_data}\n\nБасқа веб-сайттар дерегі: {ddg_data}"
            
            # ЖИ үлкен мәтінді, рефератты өзі адамша өңдеп, қателерді түзеп жазады
            reply = ask_ai(user_input, st.session_state.user_name, combined_context)

        # Экранға шығару
        st.markdown(reply)
        if img_html:
            st.markdown(img_html, unsafe_allow_html=True)
            st.download_button("📥 Скачать фото", data=img_bytes, file_name="photo.png", mime="image/png", key="current_dl")
        
        # ДАУЫСТЫ АВТОМАТТЫ ТҮРДЕ ОЙНАТУ
        audio_data = make_voice(reply, lang)
        if audio_data:
            st.audio(audio_data, format="audio/mp3", autoplay=True)

        # Сессияға сақтау
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "img_html": img_html,
            "img_bytes": img_bytes
        })
