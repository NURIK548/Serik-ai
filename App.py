import streamlit as st
import wikipedia
import requests
import re
import io
import random
from requests.utils import quote

# ======================
# НАСТРОЙКИ
# ======================
st.set_page_config(page_title="Serik-Ai PRO Max", layout="wide")
wikipedia.set_lang("ru")

# Инициализация истории чата в сессии (чтобы ничего не пропадало)
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Привет! Я Serik-AI PRO Max. Готов писать рефераты, эссе и создавать качественные фото!"
    st.session_state.messages.append({"role": "assistant", "content": welcome, "image_html": None, "image_bytes": None})

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
    max-width: 750px;
    border-radius: 12px;
    border: 3px solid #4A90E2; /* Красивая синяя рамка */
    overflow: hidden;
    margin: 15px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# ======================
# ПОИСК ИНФОРМАЦИИ (DUCKDUCKGO)
# ======================
def search_google_and_compose(topic):
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
# УЛУЧШЕННЫЙ ГЕНЕРАТОР ФОТО (HD качество + скачивание)
# ======================
def generate_hd_image(prompt_text):
    # Промпт-улучшайзеры для создания уникального арта нейросетью самостоятельно
    hd_enhancers = " 8k resolution, highly detailed digital art, masterpiece, cinematic lighting, photorealistic, trending on artstation"
    full_prompt = prompt_text + hd_enhancers
    
    seed = random.randint(1, 999999)
    # Высокое качество изображения (1024x1024)
    img_url = f"https://image.pollinations.ai/p/{quote(full_prompt)}?width=1024&height=1024&seed={seed}&nofeed=true"
    
    try:
        # Скачиваем изображение в байтах для функции скачивания пользователем
        response = requests.get(img_url, timeout=15)
        if response.status_code == 200:
            return response.content, img_url
    except:
        pass
    return None, None

# ======================
# СВЯЗЫВАНИЕ ТЕКСТА И СОСТАВЛЕНИЕ СТРУКТУРЫ
# ======================
def compose_smart_text(q, topic, main_info, full_wiki):
    q_low = q.lower()
    
    # Очистка текста от лишних пробелов
    clean_info = re.sub(r'\s+', ' ', main_info).strip()
    
    if "реферат" in q_low:
        return f"""**РЕФЕРАТ НА ТЕМУ: "{topic.upper()}"**

---
### 1. ВВЕДЕНИЕ
В современной науке и практике изучение темы "{topic}" занимает важное место. Актуальность данного исследования продиктована глубокими изменениями в структуре рассматриваемого вопроса. На основе собранных данных, можно утверждать следующее: {clean_info[:350]}...

### 2. ОСНОВНАЯ ЧАСТЬ
Рассматривая детально аспекты '{topic}', стоит обратить внимание на важные исторические, теоретические и практические факторы. 
{full_wiki[:1200] if full_wiki else clean_info}

### 3. ЗАКЛЮЧЕНИЕ И ВЫВОДЫ
Таким образом, проведенный анализ темы "{topic}" позволяет сделать вывод, что данное направление требует дальнейшего детального изучения. Рассмотренные положения открывают новые перспективы для понимания проблематики и решения сопутствующих задач."""

    elif "эссе" in q_low:
        return f"""**ЭССЕ НА ТЕМУ: "{topic.upper()}"**

---
### Мое размышление
Задумываясь над темой "{topic}", мы часто сталкиваемся с неоднозначными мнениями. Как показывает анализ актуальной информации: {clean_info[:400]}...

### Личный взгляд и анализ
Я считаю, что важно учитывать внутренние взаимосвязи этого процесса. Тема '{topic}' наглядно демонстрирует нам, как быстро меняются современные тренды и подходы к решению ключевых вопросов.

### Итог
В заключение хочется подчеркнуть, что "{topic}" — это не просто теоретический вопрос, а живой и динамичный процесс, во многом определяющий развитие данной сферы в будущем."""

    return main_info

# ======================
# СМАРТ КОНТЕНТ МЕНЕДЖЕР
# ======================
def get_smart_content(q):
    q_low = q.lower().strip()

    fast_answers = {
        "привет": "Привет! Я Serik-AI PRO Max, готов к работе.",
        "как дела": "Отлично! Все системы работают стабильно.",
        "кто тебя создал": "Меня создал Нурхан."
    }

    if q_low in fast_answers:
        return fast_answers[q_low], None, None

    # ПРОВЕРКА ЗАПРОСА НА ФОТО
    if any(x in q_low for x in ["фото", "картинка", "рисунок", "нарисуй", "сделай фото"]):
        topic = q_low
        for w in ["фото", "картинку", "рисунок", "нарисуй", "сделай"]:
            topic = topic.replace(w, "")
        topic = topic.strip() or "futuristic city"

        # Генерация фото
        img_bytes, img_url = generate_hd_image(topic)
        
        if img_bytes:
            html = f"""
            <div class="photo-box">
                <img src="{img_url}" style="width:100%; height:auto;">
            </div>
            """
            return f"🎨 **Создано уникальное HD изображение по вашему запросу:** *{topic}*", html, img_bytes
        else:
            return "Не удалось сгенерировать фото. Сервер перегружен, попробуйте еще раз.", None, None

    # ПОИСК ТЕКСТА / РЕФЕРАТ / ЭССЕ
    topic = q.replace("напиши", "").replace("реферат", "").replace("эссе", "").replace("про", "").strip()

    wiki_summary, wiki_content = "", ""
    try:
        page = wikipedia.page(topic)
        wiki_summary = page.summary
        wiki_content = page.content
    except:
        pass

    google_data = search_google_and_compose(topic)

    if not wiki_summary and not google_data:
        return f"Я не нашел информацию по запросу '{topic}'. Попробуйте сформулировать точнее.", None, None

    raw_main = wiki_summary if wiki_summary else google_data
    
    # Сборка красивого связного текста
    final_text = compose_smart_text(q, topic, raw_main, wiki_content)

    return final_text, None, None

# ======================
# ОТОБРАЖЕНИЕ СТРАНИЦЫ И ИСТОРИИ ЧАТА
# ======================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("image_html"):
            st.markdown(msg["image_html"], unsafe_allow_html=True)
        if msg.get("image_bytes"):
            st.download_button(
                label="📥 Скачать фото в HD",
                data=msg["image_bytes"],
                file_name="serik_ai_image.png",
                mime="image/png"
            )

# ======================
# ПОЛЕ ВВОДА ЗАПРОСА
# ======================
prompt = st.chat_input("Напишите запрос (например: 'нарисуй космос' или 'реферат про физику')...")

if prompt:
    # 1. Сохраняем запрос пользователя
    st.session_state.messages.append({"role": "user", "content": prompt, "image_html": None, "image_bytes": None})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Обрабатываем ответ ассистента
    with st.chat_message("assistant"):
        text, image_html, image_bytes = get_smart_content(prompt)

        st.markdown(text)
        
        if image_html:
            st.markdown(image_html, unsafe_allow_html=True)
        
        if image_bytes:
            st.download_button(
                label="📥 Скачать фото в HD",
                data=image_bytes,
                file_name="serik_ai_image.png",
                mime="image/png"
            )

        # Сохраняем ответ в сессию (чтобы данные не сбрасывались при скачивании)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": text, 
            "image_html": image_html,
            "image_bytes": image_bytes
        })
        
        # Перезагружаем интерфейс для моментального обновления
        st.rerun()
