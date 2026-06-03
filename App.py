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
# CLEAN TEXT
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
# SESSION STATE
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "freq" not in st.session_state:
    st.session_state.freq = {}

# =========================
# SEARCH
# =========================
def find_best_match(q, memory):
    keys = list(memory.keys())
    match = difflib.get_close_matches(q, keys, n=1, cutoff=0.6)
    return match[0] if match else None

def wiki_search(query):
    try:
        return wikipedia.summary(query, sentences=3)
    except:
        return "Wikipedia табылмады."

def web_search(query):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            results.append(r["body"])
    return results

def speak(text):
    tts = gTTS(text=text, lang="ru")
    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio

# =========================
# UI
# =========================
st.set_page_config(page_title="AI CHAT PRO", layout="wide")
st.title("🤖 Serik AI Chat PRO")

user_input = st.text_input("Сұрақ жаз:")

if st.button("Send") and user_input:

    q = clean_text(user_input)

    # freq update
    st.session_state.freq[q] = st.session_state.freq.get(q, 0) + 1

    # add chat
    st.session_state.chat.append(("user", user_input))

    # memory check
    match = find_best_match(q, memory)

    if match:
        answer = memory[match]
    else:
        wiki = wiki_search(q)
        web = web_search(q)

        answer = wiki + "\n\n🌐 Web:\n" + "\n".join(web)

        memory[q] = answer
        save_memory(memory)

    st.session_state.chat.append(("bot", answer))

    audio = speak(answer)
    st.audio(audio, format="audio/mp3")

# =========================
# CHAT DISPLAY
# =========================
for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"🧑 **Сен:** {msg}")
    else:
        st.markdown(f"🤖 **Bot:** {msg}")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🧠 Панель")

if st.sidebar.button("Memory"):
    st.sidebar.write(memory)

if st.sidebar.button("Last chat"):
    st.sidebar.write(st.session_state.chat[-10:])

if st.sidebar.button("🔥 Частые сұрақтар"):
    sorted_freq = dict(sorted(st.session_state.freq.items(), key=lambda x: x[1], reverse=True))
    st.sidebar.write(sorted_freq)

if st.sidebar.button("Clear memory"):
    memory = {}
    save_memory(memory)
    st.sidebar.success("Memory cleared")
