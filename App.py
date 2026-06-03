import streamlit as st
import json
import difflib  # Түсініксіз немесе қате сөздерді түзетіп оқу үшін
import os
from gtts import gTTS  # Дауыспен сөйлету үшін
import wikipedia  # Интернеттен іздеу үшін

# 1. JSON базасын жүктеу
def load_memory():
    try:
        with open("memory_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Базаны жүктеу қатесі: {e}")
        return {}

memory = load_memory()

# 2. Мәтінді аудиоға айналдыру және сөйлету функциясы
def speak_text(text):
    try:
        # Орыс тілінде таза сөйлеуі үшін 'ru' тілін таңдаймыз
        tts = gTTS(text=text, lang='ru', slow=False)
        filename = "voice.mp3"
        tts.save(filename)
        
        # Стримлитте аудио ойнатқышты көрсету және автоматты ойнату
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        # Уақытша файлды тазалап отыру
        os.remove(filename)
    except Exception as e:
        st.error(f"Аудио шығаруда қате кетті: {e}")

# 3. Интернеттен (Wikipedia) іздеу функциясы
def search_internet(query):
    try:
        wikipedia.set_lang("ru")
        # Сұрақ бойынша ең қысқа 2 сөйлемді үзінді алып келеді
        summary = wikipedia.summary(query, sentences=2)
        return f"Мен бұл сұрақты базадан таппадым, бірақ интернетте былай деп жазылған: {summary}"
    except Exception:
        return "Кешір, бұл сұрақты өз базамнан да, интернеттен де таба алмадым, бро."

# 4. Жауап іздеу логикасы (Қателерді кешірумен)
def get_bot_response(user_input, memory_base):
    user_input = user_input.lower().strip()
    
    if not memory_base:
        return "Менің базамыз бос тұр..."

    # Базадан 60% ұқсастығы бар сұрақты іздеу (опечаткаларды кешіреді)
    matches = difflib.get_close_matches(user_input, memory_base.keys(), n=1, cutoff=0.6)
    
    if matches:
        correct_question = matches[0]
        return memory_base[correct_question]
    else:
        # Егер базада мүлдем ұқсамаса, интернеттен іздейді
        return search_internet(user_input)

# --- СТРИМЛИТ ИНТЕРФЕЙСІ ---
st.title("Serik-Ai v1.0 PRO 🚀")
st.write("Создатель бота: **Нурик**")

user_query = st.text_input("Маған сұрақ қой (қате жазсаң да түсінемін):")

if user_query:
    # Жауапты анықтау
    response = get_bot_response(user_query, memory)
    
    # Жауапты экранға шығару
    st.write(f"**Serik-Ai:** {response}")
    
    # ЖАУАПТЫ ДАУЫСТАП СӨЙЛЕТУ (Автоматты түрде оқиды)
    speak_text(response)
