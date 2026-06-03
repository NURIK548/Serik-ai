import streamlit as st
import json
import os
import difflib
import wikipedia
from gtts import gTTS
from duckduckgo_search import DDGS
import io
import re

# =========================
# SETTINGS
# =========================
MEMORY_FILE = "memory_base.json"
wikipedia.set_lang("ru")

# =========================
# CLEAN TEXT (.,;: - бәрін өшіру)
# =========================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[.,;:!?\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================
# MEMORY
# =========================
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

memory = load_memory()

# =========================
# FREQUENT QUESTIONS TRACK
# =========================
if "freq" not in st.session_state:
    st.session_state.freq = {}

if "last_chat" not in st.session_state:
    st.session_state.last_chat = []

# =========================
# MATCH FUNCTION
# =========================
def find_best_match(question, memory):
    questions = list(memory.keys())
    match = difflib.get_close_matches(question, questions, n=1, cutoff=0.6)
    return match[0] if match else None

# =========================
# WEB SEARCH
# =========================
def search_web(query):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            results.append(r["body"])
    return results

# =========================
# WIKI
# =========================
def wiki_search(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except:
        return "Wikipedia-дан ештеңе табылмады."

# =========================
# TTS
# =========================
def speak(text):
    tts = gTTS(text=text, lang="ru")
    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio

# =========================
# UI
# =========================
st.title("🤖 Serik-AI PRO Clean")

user_input = st.text_input("Сұрақ жаз:")

if st.button("Жіберу") and user_input:

    clean_q = clean_text(user_input)

    # frequency count
    st.session_state.freq[clean_q] = st.session_state.freq.get(clean_q, 0) + 1

    # last chat save
    st.session_state.last_chat.append(clean_q)
    if len(st.session_state.last_chat) > 10:
        st.session_state.last_chat.pop(0)

    # memory match
    match = find_best_match(clean_q, memory)

    if match:
        answer = memory[match]
        st.success("🧠 Жадтан")
    else:
        wiki = wiki_search(clean_q)
        web = search_web(clean_q)

        answer = wiki + "\n\n🌐 Internet:\n" + "\n".join(web[:3])

        memory[clean_q] = answer
        save_memory(memory)

        st.info("💾 Сақталды")

    st.write(answer)

    audio = speak(answer)
    st.audio(audio, format="audio/mp3")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🧠 Memory")

if st.sidebar.button("Бар memory"):
    st.sidebar.write(memory)

if st.sidebar.button("Last chat"):
    st.sidebar.write(st.session_state.last_chat)

if st.sidebar.button("🔥 Частые сұрақтар"):
    sorted_freq = dict(sorted(st.session_state.freq.items(), key=lambda x: x[1], reverse=True))
    st.sidebar.write(sorted_freq)

if st.sidebar.button("Clear memory"):
    memory = {}
    save_memory(memory)
    st.sidebar.success("Өшірілді")
