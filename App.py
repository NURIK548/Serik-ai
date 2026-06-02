import streamlit as st
import wikipedia
import requests
import re
import base64
from gtts import gTTS
import io
import random
import os
import json
import difflib
from requests.utils import quote

# ======================
# БАПТАУЛАР ЖӘНЕ ПАРОЛЬ
# ======================
st.set_page_config(page_title="Serik-Ai PRO Max Ultra", layout="wide")
wikipedia.set_lang("ru")
DEV_PASSWORD = "nurik777" 

# ======================
# АҚЫЛДЫ СҰРАҚ-ЖАУАП БАЗАСЫ (JSON)
# ======================
MEMORY_FILE = "memory_base.json"

def load_memory_base():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_to_memory_base(question, answer):
    base = load_memory_base()
    base[question.lower().strip()] = answer.strip()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=4)

def delete_from_memory(question):
    base = load_memory_base()
    if question in base:
        del base[question]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False, indent=4)
        return True
    return False

def find_closest_answer(user_query, memory_base):
    user_query = user_query.lower().strip()
    saved_questions = list(memory_base.keys())
    if not saved_questions:
        return None
    closest_matches = difflib.get_close_matches(user_query, saved_questions, n=1, cutoff=0.6)
    if closest_matches:
        matched_question = closest_matches[0]
        similarity = difflib.SequenceMatcher(None, user_query, matched_question).ratio()
        if similarity >= 0.65:
            return memory_base[matched_question]
    return None

# ======================
# SIDEBAR МӘЗІРІ ЖӘНЕ ФУНКЦИЯЛАР
# ======================
st.sidebar.title("🎨 Темы оформления")
bg_option = st.sidebar.selectbox(
    "Выберите фон для Serik-Ai:",
    ["Тёмный космос (По умолчанию)", "Киберпанк neon", "Матрица green", "Мягкий серый", "Светлая тема"]
)

# ФАЙЛДАРДЫ ТАЛДАУ
st.sidebar.markdown("---")
st.sidebar.title("📁 Анализ документов (.txt)")
uploaded_file = st.sidebar.file_uploader("Загрузите текстовый файл:", type=["txt"])
file_context = ""
if uploaded_file is not None:
    try:
        file_context = uploaded_file.read().decode("utf-8")
        st.sidebar.success("Файл успешно загружен! 📄")
    except:
        st.sidebar.error("Не удалось прочитать файл.")

# РАЗРАБОТЧИК ПАНЕЛІ
st.sidebar.markdown("---")
st.sidebar.title("🛠️ Панель Разработчика")
user_password = st.sidebar.text_input("Введите пароль разработчика:", type="password")
is_developer = (user_password == DEV_PASSWORD)

if is_developer:
    st.sidebar.success("Доступ разрешен! ✅")
    st.sidebar.subheader("🗄️ Управление базой памяти:")
    current_base = load_memory_base()
    if current_base:
        for q_key in list(current_base.keys()):
            col1, col2 = st.sidebar.columns([3, 1])
            col1.write(f"**Q:** {q_key}\n**A:** {current_base[q_key]}")
            if col2.button("❌", key=f"del_{q_key}"):
                delete_from_memory(q_key)
                st.rerun()
    else:
        st.sidebar.info("База данных пока пуста.")
else:
    if user_password:
        st.sidebar.error("Неверный пароль! ❌")

# Дизайн
bg_styles = {
    "Тёмный космос (По умолчанию)": "background-color: #0e1117; color: white;",
    "Киберпанк neon": "background: linear-gradient(135deg, #120c1f 0%, #05020a 100%); background-attachment: fixed; color: #00ffcc;",
    "Матрица green": "background-color: #000000; color: #00ff00; font-family: 'Courier New', monospace;",
    "Мягкий серый": "background-color: #2b2d42; color: #edf2f4;",
    "Светлая тема": "background-color: #f8f9fa; color: #212529;"
}
selected_bg = bg_styles[bg_option]
text_color = "white" if bg_option != "Светлая тема" else "#212529"

st.markdown(f"<style>.stApp {{{selected_bg}}} .stMarkdown, p, h1, h2, h3, span, label {{color: {text_color} !important;}}</style>", unsafe_allow_html=True)

# ======================
# ДАУЫС (TTS)
# ======================
def get_audio(text):
    try:
        clean_txt = text[:200]
        clean_txt = re.sub(r'[\U00010000-\U0010ffff]|\u263a|\u263b', '', clean_txt)
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
# ЖАНДЫ ИНТЕРНЕТ
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
# ЧАТ МОДЕЛІ
# ======================
def chat_with_ai(user_prompt, doc_context=""):
    try:
        context_instruction = f" Текст загруженного документа: '{doc_context}'." if doc_context else ""
        api_url = f"https://text.pollinations.ai/{quote(user_prompt)}?system=Ты+интеллектуальный+ассистент+Serik-AI+созданный+Нурханом.+Отвечай+всегда+СТРОГО+на+русском+языке+живо.+{quote(context_instruction)}"
        res = requests.get(api_url, timeout=15)
        if res.status_code == 200:
            return res.text.strip()
    except:
        pass
    return "Я тут, давай поболтаем! 😊"

# ======================
# SMART CONTENT МЕНЕДЖЕР
# ======================
def get_smart_content(q, doc_context=""):
    q_low = q.lower().strip()

    if q_low.startswith("запомни"):
        if not is_developer:
            return "❌ У вас нет прав разработчика для обучения ИИ! Введите верный пароль слева."
        core_text = q[7:].strip()
        if " это " in core_text.lower():
            parts = re.split(r'\s+это\s+', core_text, flags=re.IGNORECASE, maxsplit=1)
            question_part = parts[0].strip()
            answer_part = parts[1].strip()
            if question_part and answer_part:
                save_to_memory_base(question_part, answer_part)
                return f"🧠 **[Режим Разработчика]** Я успешно запомнил!\n\n**Вопрос:** {question_part}\n**Ответ:** {answer_part}"
        return "Пожалуйста, используй формат: **Запомни [вопрос] это [ответ]**"

    memory_base = load_memory_base()
    smart_answer = find_closest_answer(q, memory_base)
    if smart_answer:
        return smart_answer

    if "реферат" in q_low or "эссе" in q_low:
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
        main = wiki_summary if wiki_summary else google_data
        if "реферат" in q_low and main:
            return f"РЕФЕРАТ: {topic}\n\nВведение:\n{main}\n\nОсновная часть:\n{wiki_content[:1500] if wiki_content else google_data}\n\nЗаключение:\nАнализ показывает важность темы."
        elif "эссе" in q_low and main:
            return f"ЭССЕ: {topic}\n\nАнализ:\n{main}\n\nВывод: тема актуальна и интересна."

    return chat_with_ai(q, doc_context)

# ======================
# CHAT INTERFACE
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Привет! Я Serik-AI PRO Max Ultra. Я готов слушать и отвечать."})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ТҮЗЕТІЛДІ: ТЕЛЕФОНДА ДА, КОМПЬЮТЕРДЕ ДЕ НАҚТЫ ЕСТИТІН КІРІСТІРІЛГЕН БРАУЗЕРЛІК ДАУЫС ЖҮЙЕСІ
st.write("---")
st.write("🎙️ **Голосовой ввод для телефона и ПК:**")

# Телефон клавиатурасындағы дауыспен жазу жүйесін қолдану нұсқауымен бірге таза чат-енгізу
prompt = st.chat_input("Напишите или продиктуйте запрос (используйте микрофон на клавиатуре телефона)...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            text = get_smart_content(prompt, file_context)
        st.markdown(text)
        
        audio = get_audio(text)
        if audio:
            st.audio(audio, format="audio/mp3")
            
        st.session_state.messages.append({"role": "assistant", "content": text})
