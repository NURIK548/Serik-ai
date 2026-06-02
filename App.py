import streamlit as st
import requests
import json
import os
from urllib.parse import quote

# 1. ЕҢ БІРІНШІ ЖОЛ: КОНФИГУРАЦИЯ (Мұны өзгертуге болмайды)
st.set_page_config(page_title="Serik-Ai PRO Max", page_icon="🤖", layout="wide")

# 2. ДИЗАЙН ЖӘНЕ ОБОЙ (CSS)
st.markdown("""
    <style>
    /* Фонды өзгерту */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1e1e1e 100%);
        color: white;
    }
    /* Чат бағанасының дизайны */
    .stChatInput {
        background-color: #262730;
    }
    /* Разработчик жазуы */
    .dev-tag {
        text-align: center;
        color: #00ff00;
        font-family: monospace;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

MEMORY_FILE = "memory_base.json"

# 3. ФУНКЦИЯЛАР
def get_answer_from_memory(user_input):
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            clean_input = user_input.strip().lower()
            for key in data.keys():
                if key in clean_input or clean_input in key:
                    return data[key]
    return None

def chat_with_ai(user_input):
    system_instructions = "Ты — Serik-Ai, интеллектуальный и харизматичный ИИ. Общайся на русском языке."
    api_url = f"https://text.pollinations.ai/{quote(user_input)}?system={quote(system_instructions)}"
    try:
        res = requests.get(api_url, timeout=10)
        return res.text if res.status_code == 200 else "Я тут, давай поболтаем!"
    except: return "Я тут, давай поболтаем!"

# 4. ИНТЕРФЕЙС (Барлық компоненттер)
st.title("🤖 Serik-Ai PRO Max")
st.markdown("<div class='dev-tag'>Разработчик: Нурхан | Version 2.0</div>", unsafe_allow_html=True)

# Бүйірлік панель
with st.sidebar:
    st.header("Управление")
    uploaded_file = st.file_uploader("Базаны жүктеу (JSON)", type=['json'])

# Чат тарихы
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Негізгі чат
if user_input := st.chat_input("Жазып көр..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        # "Думает" анимациясы
        with st.spinner("Serik-Ai думает..."):
            answer = get_answer_from_memory(user_input)
            if not answer: answer = chat_with_ai(user_input)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
