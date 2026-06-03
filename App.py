import streamlit as st
import json
import difflib
import os
from gtts import gTTS
import google.generativeai as genai

# --- НАСТРОЙКА ИИ (GEMINI API) ---
# Нурик, вставь сюда свой API ключ от Google AI Studio
API_KEY = "ТВОЙ_GEMINI_API_KEY" 
genai.configure(api_key=API_KEY)

# 1. Загрузка базы данных
def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

memory = load_memory()

# 2. Озвучка текста (gTTS)
def speak_text(text):
    try:
        # Чтобы длинные эссе не озвучивались слишком долго, берем первые 200 символов
        short_text = text[:200] + "..." if len(text) > 200 else text
        tts = gTTS(text=short_text, lang='ru', slow=False)
        filename = "voice.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        os.remove(filename)
    except Exception:
        pass

# 3. Генерация текста через ИИ (Эссе, рефераты, составление предложений)
def generate_ai_response(query):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Инструкция для ИИ, чтобы он помнил свое имя и создателя
        prompt = f"Ты умный ИИ по имени Serik-Ai. Тебя создал Нурик. Ответь на запрос (можешь писать эссе, рефераты, генерировать тексты): {query}"
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "Ошибка: Не удалось подключиться к модулю ИИ. Проверь API ключ."

# 4. Логика поиска ответа
def get_bot_response(user_input, memory_base):
    user_input = user_input.lower().strip()
    
    if not memory_base:
        return "База данных пуста."

    # Проверка совпадений в JSON (с допущением опечаток)
    matches = difflib.get_close_matches(user_input, memory_base.keys(), n=1, cutoff=0.6)
    
    if matches:
        return memory_base[matches[0]]
    else:
        # Если в базе ответа нет, ИИ сам генерирует текст (эссе, реферат и т.д.)
        return generate_ai_response(user_input)

# --- ИНТЕРФЕЙС В СТИЛЕ CHATGPT ---
st.title("Serik-Ai v1.0 PRO")
st.write("Разработчик: **Нурик**")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение истории чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода сообщения
if prompt := st.chat_input("Напишите сообщение..."):
    
    # Отображение сообщения пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Получение ответа от бота
    response = get_bot_response(prompt, memory)

    # Отображение ответа бота
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Автоматическая озвучка ответа
    speak_text(response)
