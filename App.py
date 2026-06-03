import streamlit as st
import json
import difflib
import os
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS  # Даг-Даг кітапханасы

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
        # Аудио тез жасалуы үшін тек алғашқы 300 әріпті оқиды
        short_text = text[:300] + "..." if len(text) > 300 else text
        tts = gTTS(text=short_text, lang='ru', slow=False)
        filename = "voice.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        os.remove(filename)
    except Exception:
        pass

# 3. Поиск без API (Wikipedia + DuckDuckGo)
def search_no_api(query):
    # Очищаем запрос от лишних слов, чтобы поиск работал точнее
    clean_query = query.lower().replace("напиши", "").replace("эссе", "").replace("реферат", "").replace("про", "").strip()
    
    result_text = ""
    
    # Сначала ищем в Википедии (идеально для рефератов и эссе)
    try:
        wikipedia.set_lang("ru")
        # Берем 7 предложений, чтобы текст был длинным как реферат
        wiki_summary = wikipedia.summary(clean_query, sentences=7)
        result_text += f"Вот подробная информация (из Википедии):\n\n{wiki_summary}"
        return result_text
    except Exception:
        pass # Если в Википедии нет, идем дальше
        
    # Если Википедия не нашла, ищем через DuckDuckGo (даг-даг)
    try:
        ddgs = DDGS()
        results = ddgs.text(clean_query, region='ru-ru', max_results=3)
        if results:
            result_text += "Вот что я нашел в интернете (DuckDuckGo):\n\n"
            for r in results:
                result_text += f"- {r['body']}\n\n"
            return result_text
    except Exception:
        pass
        
    return "Извини, я не смог найти информацию ни в своей базе, ни в интернете."

# 4. Логика поиска ответа
def get_bot_response(user_input, memory_base):
    user_input = user_input.lower().strip()
    
    if not memory_base:
        return "База данных пуста."

    # Проверка совпадений в JSON
    matches = difflib.get_close_matches(user_input, memory_base.keys(), n=1, cutoff=0.6)
    
    if matches:
        return memory_base[matches[0]]
    else:
        # Запуск поиска в интернете без API
        return search_no_api(user_input)

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
if prompt := st.chat_input("Напишите сообщение (вопрос, эссе, реферат)..."):
    
    # 1. Показываем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. АНИМАЦИЯ "ДУМАЕТ" (крутилка на экране)
    with st.spinner("Serik-Ai думает и ищет информацию... ⏳"):
        response = get_bot_response(prompt, memory)

    # 3. Вывод ответа
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 4. Автоматическая озвучка
    speak_text(response)
