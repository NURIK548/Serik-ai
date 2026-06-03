import streamlit as st
import requests
import json
import os
from urllib.parse import quote

# 1. СТРАНИЦА КОНФИГУРАЦИЯСЫ ЖӘНЕ ДИЗАЙН (ОБОЙ)
st.set_page_config(page_title="Serik-Ai PRO Max", page_icon="🤖", layout="wide")

# Күңгірт фон (Dark Mode) және стильдер
st.markdown("""
    <style>
    .stApp {
        background: #0e1117 !important;
        color: #ffffff !important;
    }
    div[data-testid="stChatMessage"] {
        background-color: #1e222b !important;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .dev-tag {
        text-align: center;
        color: #00ff00;
        font-family: monospace;
        font-size: 14px;
        margin-bottom: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

MEMORY_FILE = "memory_base.json"

# 2. БАЗАНЫ ҚАТЕСІЗ ҚАУІПСІЗ ОҚУ (АҚЫЛДЫ ФУНКЦИЯ)
def load_memory_safe():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f), None
        except json.JSONDecodeError as e:
            # Егер JSON-да қате болса, қай жолда екенін анықтайды
            return None, f"Строка {e.lineno}, колонка {e.colno}: {e.msg}"
        except Exception as e:
            return None, str(e)
    return {}, None

# Сұрақты базадан іздеу алгоритмі
def get_answer_from_memory(user_input, data):
    if not data:
        return None
    
    clean_input = user_input.strip().lower()
    
    # 1-ші деңгей: Дәлме-дәл сәйкестік (Ең дәл жауап)
    if clean_input in data:
        return data[clean_input]
        
    # 2-ші деңгей: Икемді іздеу (Сөз ішінде болса)
    for key, value in data.items():
        k = key.strip().lower()
        if len(k) > 3 and (k in clean_input or clean_input in k):
            return value
            
    return None

# 3. ИНТЕРНЕТТЕН ЖАУАП АЛУ (POLLINATIONS API)
def chat_with_ai(user_input):
    try:
        system_instructions = (
            "Ты — Serik-Ai, интеллектуальный и харизматичный ИИ-ассистент, созданный Нурханом. "
            "Твой стиль общения: живой, дружелюбный, как у реального человека. "
            "Всегда общайся только на русском языке. "
            "Отвечай развернуто и интересно, никогда не используй сухие шаблонные фразы."
        )
        api_url = f"https://text.pollinations.ai/{quote(user_input)}?system={quote(system_instructions)}"
        res = requests.get(api_url, timeout=15)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except:
        pass
    return "Я тут, братишка, на связи! О чем поболтаем? 😊"

# 4. ИНТЕРФЕЙС КӨРІНІСІ
st.title("🤖 Serik-Ai PRO Max")
st.markdown("<div class='dev-tag'>Разработчик: Нурхан | Version 3.0 (Стабильная)</div>", unsafe_allow_html=True)

# Базаны жүктеп, қатесін тексеру
memory_data, json_error = load_memory_safe()

# БҮЙІРЛІК ПАНЕЛЬ (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Панель управления")
    
    # JSON файлда қате болса, экранға шығарып ескертеді
    if json_error:
        st.error(f"⚠️ Ошибка в memory_base.json!\n{json_error}")
        st.info("💡 Проверь пропущенные запятые или кавычки в указанной строке.")
    else:
        st.success("✅ База данных успешно подключена и работает!")
        
    uploaded_file = st.file_uploader("Обновить базу знаний (JSON)", type=['json'])

# ЧАТ ТАРИХЫ
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ПАЙДАЛАНУШЫ СҰРАҒЫ
if user_input := st.chat_input("Привет брат, как дела?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # "Думает" анимациялық индикаторы
        with st.spinner("Serik-Ai думает..."):
            # Алдымен қатесіз оқылған базадан іздейді
            answer = get_answer_from_memory(user_input, memory_data)
            
            # Базада жоқ болса, интернетке (AI) жібереді
            if not answer:
                answer = chat_with_ai(user_input)
                
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
