import streamlit as st
import json
import difflib
import os
from gtts import gTTS
import wikipedia

# 1. Загрузка базы
def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Ошибка загрузки базы: {e}")
        return {}

memory = load_memory()

# 2. Озвучка текста
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='ru', slow=False)
        filename = "voice.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        os.remove(filename)
    except Exception as e:
        st.error(f"Ошибка аудио: {e}")

# 3. Поиск в интернете
def search_internet(query):
    try:
        wikipedia.set_lang("ru")
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except Exception:
        return "Ответа нет ни в базе, ни в интернете."

# 4. Логика ответов
def get_bot_response(user_input, memory_base):
    user_input = user_input.lower().strip()
    
    if not memory_base:
        return "База данных пуста."

    matches = difflib.get_close_matches(user_input, memory_base.keys(), n=1, cutoff=0.6)
    
    if matches:
        correct_question = matches[0]
        return memory_base[correct_question]
    else:
        return search_internet(user_input)

# --- ИНТЕРФЕЙС ---
st.title("Serik-Ai v1.0 PRO")
st.write("Создатель: **Нурик**")

user_query = st.text_input("Задай вопрос:")

if user_query:
    response = get_bot_response(user_query, memory)
    st.write(f"**Serik-Ai:** {response}")
    speak_text(response)
