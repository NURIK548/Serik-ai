import streamlit as st
import json
import difflib
import os
from gtts import gTTS
import wikipedia

# 1. Базаны жүктеу
def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

memory = load_memory()

# 2. Аудио (Сөйлеу)
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='ru', slow=False)
        filename = "voice.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        os.remove(filename)
    except Exception:
        pass

# 3. Интернеттен іздеу
def search_internet(query):
    try:
        wikipedia.set_lang("ru")
        return wikipedia.summary(query, sentences=2)
    except Exception:
        return "Ответа нет ни в базе, ни в интернете."

# 4. Жауапты табу (қателерді кешірумен)
def get_bot_response(user_input, memory_base):
    user_input = user_input.lower().strip()
    
    if not memory_base:
        return "База данных пуста."

    matches = difflib.get_close_matches(user_input, memory_base.keys(), n=1, cutoff=0.6)
    
    if matches:
        return memory_base[matches[0]]
    else:
        return search_internet(user_input)

# --- CHATGPT СИЯҚТЫ ИНТЕРФЕЙС ---
st.title("Serik-Ai")

# Чат тарихын сақтау үшін
if "messages" not in st.session_state:
    st.session_state.messages = []

# Бұрынғы жазылған хаттарды экранға шығару
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Төмендегі чатқа жазу жолағы
if prompt := st.chat_input("Напишите сообщение..."):
    
    # Пайдаланушының жазғанын экранға шығару
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Боттың жауабын дайындау
    response = get_bot_response(prompt, memory)

    # Боттың жауабын экранға шығару
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Боттың жауабын тарихқа қосу
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Дауыстап оқу
    speak_text(response)
