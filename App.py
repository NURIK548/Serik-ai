import streamlit as st
import requests
import json
import os
from urllib.parse import quote

# Конфигурация
MEMORY_FILE = "memory_base.json"

# 1. БАЗАНЫ ОҚУ ЖӘНЕ ИКЕМДІ ІЗДЕУ ФУНКЦИЯСЫ
def get_answer_from_memory(user_input):
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                clean_input = user_input.strip().lower()
                # Икемді іздеу: сұрақтың ішіндегі кілт сөздерді табады
                for key in data.keys():
                    if key in clean_input or clean_input in key:
                        return data[key]
        except:
            return None
    return None

# 2. ИНТЕРНЕТ АРҚЫЛЫ ЖАУАП ҚҰРАСТЫРУ
def chat_with_ai(user_input):
    try:
        system_instructions = (
            "Ты — Serik-Ai, интеллектуальный и харизматичный ИИ-ассистент, созданный Нурханом. "
            "Твой стиль общения: живой, дружелюбный, как у реального человека. "
            "Всегда общайся только на русском языке. "
            "Если не знаешь ответа, используй свою логику, чтобы дать полезный и интересный ответ."
        )
        api_url = f"https://text.pollinations.ai/{quote(user_input)}?system={quote(system_instructions)}"
        res = requests.get(api_url, timeout=15)
        if res.status_code == 200:
            return res.text.strip()
    except:
        pass
    return "Я тут, давай поболтаем! 😊"

# 3. ИНТЕРФЕЙС ЖӘНЕ НЕГІЗГІ ЛОГИКА
st.title("Serik-Ai PRO Max")
st.write("Спроси меня о чем угодно!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Чат тарихын көрсету
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Қолданушы сұрауы
if user_input := st.chat_input("Твое сообщение..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # Ақылды логика: алдымен база, жоқ болса интернет
        answer = get_answer_from_memory(user_input)
        
        if not answer:
            answer = chat_with_ai(user_input)
            
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
