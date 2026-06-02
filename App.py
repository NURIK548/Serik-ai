import streamlit as st
import requests
import json
import os
from urllib.parse import quote

# 1. СТИЛЬ ЖӘНЕ ОБОЙ (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stChatInput { border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

MEMORY_FILE = "memory_base.json"

# 2. ФУНКЦИЯЛАР
def get_answer_from_memory(user_input):
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                clean_input = user_input.strip().lower()
                for key in data.keys():
                    # Дәл түсіну үшін икемді логика
                    if key in clean_input or clean_input in key:
                        return data[key]
        except: return None
    return None

def chat_with_ai(user_input):
    system_instructions = "Ты — Serik-Ai, харизматичный ИИ. Общайся на русском. Помогай всегда."
    api_url = f"https://text.pollinations.ai/{quote(user_input)}?system={quote(system_instructions)}"
    try:
        res = requests.get(api_url, timeout=10)
        return res.text if res.status_code == 200 else "Я тут, давай поболтаем!"
    except: return "Я тут, давай поболтаем!"

# 3. ИНТЕРФЕЙС
st.title("🤖 Serik-Ai PRO Max")
st.sidebar.title("Настройки")
uploaded_file = st.sidebar.file_uploader("Загрузить файл для ИИ", type=['txt', 'json'])

if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if user_input := st.chat_input("Привет брат, как дела?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        # "Думает" анимациясы үшін
        with st.spinner("Serik-Ai думает..."):
            answer = get_answer_from_memory(user_input)
            if not answer: answer = chat_with_ai(user_input)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
