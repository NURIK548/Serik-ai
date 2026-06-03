import streamlit as st
import json
import difflib
import os
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS

# =========================
# ПАРОЛЬ
# =========================
ADMIN_PASSWORD = "1234"

# =========================
# MEMORY
# =========================
def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

memory = load_memory()

def save_memory():
    with open("memory_base.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

# =========================
# ЗАПОМНИ КОМАНДА
# =========================
def handle_memory_command(user_input):
    if user_input.startswith("запомни "):
        try:
            parts = user_input.replace("запомни ", "").split("|")

            if len(parts) != 3:
                return "Формат: запомни пароль|сұрақ|жауап"

            password, question, answer = parts

            if password != ADMIN_PASSWORD:
                return "Қате пароль ❌"

            memory[question.lower()] = answer
            save_memory()

            return "Есте сақтадым ✅"

        except:
            return "Қате формат"

    return None

# =========================
# VOICE
# =========================
def speak_text(text):
    try:
        short_text = text[:300]

        tts = gTTS(text=short_text, lang="ru")
        filename = "voice.mp3"
        tts.save(filename)

        with open(filename, "rb") as f:
            audio = f.read()

        st.audio(audio, format="audio/mp3", autoplay=True)

        os.remove(filename)

    except:
        pass

# =========================
# INTERNET SEARCH
# =========================
def search_no_api(query):
    clean_query = query.lower().strip()

    try:
        wikipedia.set_lang("ru")
        return wikipedia.summary(clean_query, sentences=5)
    except:
        pass

    try:
        ddgs = DDGS()
        results = list(ddgs.text(clean_query, max_results=5))

        if results:
            text = "Нашёл в интернете:\n\n"
            for r in results:
                text += f"• {r.get('body','')}\n\n"
            return text

    except:
        pass

    return "Не смог найти информацию."

# =========================
# BRAIN LOGIC
# =========================
def get_bot_response(user_input, memory_base):

    user_input = user_input.lower().strip()

    # memory command
    mem = handle_memory_command(user_input)
    if mem:
        return mem

    # exact memory
    if user_input in memory_base:
        return memory_base[user_input]

    # fuzzy memory
    matches = difflib.get_close_matches(user_input, memory_base.keys(), n=1, cutoff=0.6)
    if matches:
        return memory_base[matches[0]]

    # internet
    answer = search_no_api(user_input)

    if "Не смог" not in answer:
        memory[user_input] = answer
        save_memory()

    return answer

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Serik-Ai PRO", layout="wide")

st.title("🤖 Serik-Ai PRO")
st.write("Разработчик: Нурик")

if "messages" not in st.session_state:
    st.session_state.messages = []

# chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input
if prompt := st.chat_input("Напишите сообщение..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Думаю..."):
        response = get_bot_response(prompt, memory)

    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    speak_text(response)
