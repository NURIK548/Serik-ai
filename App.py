import streamlit as st
import wikipedia
import requests
import re
import random
from requests.utils import quote

# ======================
# НАСТРОЙКИ СЕССИИ
# ======================
st.set_page_config(page_title="Serik-Ai PRO Max", layout="wide")

# Сессиялық жадты ретке келтіру (Қатесіз жұмыс істеу үшін)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Алғашқы сәлемдесу
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "👋 Привет! Мен Серік-Ай PRO Max! Қазақша және орысша түсінемін. Реферат, эссе жазып, сапалы HD суреттер сала аламын!"
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
# ТІЛДІ АНЫҚТАУ ЖӘНЕ МӘТІН ТАЗАЛАУ
# ======================
def detect_language(text):
    # Қазақша әріптер кездессе, тілді қазақша деп ажыратамыз
    kz_chars = re.compile(r'[ӘәҒғҚқҢңӨөҰұҮүҺһІі]')
    if kz_chars.search(text):
        return "kk"
    # Егер қазақша әріптер болмаса, бірақ жиі кездесетін сөздер болса
    kz_words = ["істе", "жаз", "сурет", "қыл", "құра", "бала", "мен", "сен", "болды"]
    if any(word in text.lower() for word in kz_words):
        return "kk"
    return "ru"

def clean_and_translate_for_ai(prompt_text):
    """ Қате жазылған сөздерді тазалап, нейрожеліге ыңғайлау """
    clean_text = prompt_text.lower()
    replacements = {
        "істецді": "сделай", "түсінеьін": "понимай", "интенрнеттен": "интернет",
        "фотонвң": "фото", "качествасын": "качество", "скачатт": "скачать"
    }
    for bad, good in replacements.items():
        clean_text = clean_text.replace(bad, good)
    return clean_text

# ======================
# ИНТЕРНЕТТЕН ІЗДЕУ (DUCKDUCKGO)
# ======================
def search_internet(topic):
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={quote(topic)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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
# ТҰРАҚТЫ СУРЕТ ГЕНЕРАТОРЫ (Қатпайды, 1024x1024 HD)
# ======================
def generate_hd_image(prompt_text):
    # Суретті әдемі қылатын нейрожелілік кілт сөздер
    hd_enhancers = ", 8k resolution, highly detailed, masterpiece, cinematic lighting, photorealistic, trending on artstation"
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
# АҚЫЛДЫ МӘТІН ҚҰРАСТЫРУШЫ (ҚАЗАҚША / ОРЫСША)
# ======================
def compose_smart_text(q, topic, main_info, lang):
    q_low = q.lower()
    clean_info = re.sub(r'\s+', ' ', main_info).strip()
    if len(clean_info) < 50:
        clean_info = f"Информация по теме {topic} из открытых источников." if lang == "ru" else f"{topic} тақырыбы бойынша интернеттен алынған мәлімет."

    if "реферат" in q_low:
        if lang == "kk":
            return f"""**Тақырыбы: "{topic.upper()}" РЕФЕРАТЫ**

---
### 1. КІРІСПЕ
Қазіргі таңда "{topic}" мәселесін зерттеу өте өзекті болып табылады. Бұл бағыттағы жұмыстар қоғам мен ғылым үшін маңызды рөл атқарады. Интернет деректеріне сүйенсек: {clean_info[:400]}...

### 2. НЕГІЗГІ БӨЛІМ
"{topic}" тақырыбының ішкі құрылымы мен негізгі ерекшеліктеріне тоқталатын болсақ, бұл құбылыс көптеген факторлармен байланысты. Жиналған мәліметтер оның жан-жақты дамып жатқанын көрсетеді.

### 3. ҚОРЫТЫНДЫ
Жүргізілген талдау жұмыстары қорытындылай келе, "{topic}" тақырыбы болашақта әлі де тереңірек зерттеуді қажет ететінін дәлелдейді."""
        else:
            return f"""**Тема: РЕФЕРАТ НА ТЕМУ "{topic.upper()}"**

---
### 1. ВВЕДЕНИЕ
В современном мире изучение темы "{topic}" занимает важное место. Актуальность данного исследования продиктована изменениями в структуре рассматриваемого вопроса. На основе собранных данных: {clean_info[:400]}...

### 2. ОСНОВНАЯ ЧАСТЬ
Рассматривая детально аспекты '{topic}', стоит обратить внимание на важные теоретические и практические факторы, влияющие на развитие данной сферы.

### 3. ЗАКЛЮЧЕНИЕ
Таким образом, проведенный анализ темы "{topic}" позволяет сделать вывод, что данное направление открывает новые перспективы для понимания проблематики."""

    elif "эссе" in q_low:
        if lang == "kk":
            return f"""**Тақырыбы: "{topic.upper()}" ЕССЕ**

---
### Менің көзқарасым
"{topic}" туралы ойланғанда, біз жиі әртүрлі пікірлерді кездестіреміз. Менің ойымша, бұл мәселеге байыппен қарау керек. Мәліметтерге қарасақ: {clean_info[:400]}...

### Талдау мен дәлелдер
Бұл тақырып тек теориялық емес, өмірлік маңызы бар процесс. Біз оның даму бағытын дұрыс түсінуіміз керек.

### Түйін
Қорыта айтқанда, "{topic}" — бұл біздің бүгініміз бен болашағымызға тікелей әсер ететін маңызды құбылыс."""
        else:
            return f"""**Тема: ЭССЕ НА ТЕМУ "{topic.upper()}"**

---
### Личное размышление
Задумываясь над темой "{topic}", мы часто сталкиваемся с неоднозначными мнениями. Данные показывают следующее: {clean_info[:400]}...

### Анализ и выводы
Я считаю, что тема '{topic}' наглядно демонстрирует нам, как быстро меняются современные тренды и подходы к решению ключевых вопросов.

### Итог
В заключение хочется подчеркнуть, что это живой и динамичный процесс, определяющий развитие данной сферы."""

    return main_info

# ======================
# БАСҚАРУШЫ ЛОГИКА
# ======================
def get_smart_content(q):
    lang = detect_language(q)
    q_cleaned = clean_and_translate_for_ai(q)
    q_low = q_cleaned.lower().strip()

    # Жылдам жауаптар
    if "привет" in q_low or "салем" in q_low or "сәлем" in q_low:
        return ("Привет! Салем! Я Serik-AI PRO Max готов к работе.", None, None)
    if "как дела" in q_low or "қалай жағдай" in q_low:
        return ("Отлично! Барлығы тұрақты жұмыс істеп тұр.", None, None)

    # СУРЕТ ЖАСАУ СҰРАНЫСЫ
    if any(x in q_low for x in ["фото", "картинка", "рисунок", "нарисуй", "сурет"]):
        topic = q_low
        for w in ["фото", "картинку", "рисунок", "нарисуй", "сделай", "сурет", "салып бер", "сал"]:
            topic = topic.replace(w, "")
        topic = topic.strip() or "cyberpunk city"

        img_bytes, img_url = generate_hd_image(topic)
        
        if img_bytes:
            html = f'<div class="photo-box"><img src="{img_url}" style="width:100%; height:auto;"></div>'
            msg_text = f"🎨 **HD Сурет дайын / HD Изображение готово:** *{topic}*"
            return msg_text, html, img_bytes
        else:
            return ("Сурет салу мүмкін болмады. Сервер бос емес. / Не удалось создать фото.", None, None)

    # МӘТІН ОҚУ / РЕФЕРАТ / ЭССЕ
    topic = q.replace("напиши", "").replace("реферат", "").replace("эссе", "").replace("про", "")
    topic = topic.replace("жаз", " ").replace("туралы", " ").replace("маған", " ").strip()

    # Сұраныс тіліне қарай Wikipedia тілін баптау
    wikipedia.set_lang(lang)
    
    wiki_summary = ""
    try:
        wiki_summary = wikipedia.summary(topic, sentences=4)
    except:
        pass

    google_data = search_internet(topic)
    raw_main = wiki_summary if wiki_summary else google_data

    if not raw_main:
        if lang == "kk":
            return f"Кешіріңіз, '{topic}' туралы интернеттен ештеңе таппадым. Толығырақ жазып көріңіз.", None, None
        return f"Я не нашел информацию по запросу '{topic}'. Попробуйте точнее.", None, None

    final_text = compose_smart_text(q, topic, raw_main, lang)
    return final_text, None, None

# ======================
# ЧАТ ТАРИХЫН ЭКРАНҒА ШЫҒАРУ
# ======================
# Мұнда ешқандай батырма жоқ, тек тарихты таза көрсетеміз (Бұл қатып қалудан сақтайды)
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
# ПАЙДАЛАНУШЫ ЕНГІЗЕТІН ӨРІС
# ======================
prompt = st.chat_input("Сұранысты жазыңыз (Мысалы: 'роботтың суретін сал' немесе 'реферат про Абай')...")

if prompt:
    # 1. Қолданушы сұранысын жадқа қосу
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Жауап алу
    text, image_html, image_bytes = get_smart_content(prompt)

    # 3. Ассистент жауабын жадқа қосу
    st.session_state.messages.append({
        "role": "assistant", 
        "content": text, 
        "image_html": image_html,
        "image_bytes": image_bytes
    })
    
    # Бұрынғы қателік тудыратын батырмаларды болдырмау үшін бетті бір рет жаңартамыз
    st.rerun()
