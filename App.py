import streamlit as st
import json
import os
import difflib
import re

# =========================
# SETTINGS
# =========================
MEMORY_FILE = "memory.json"
ADMIN_PASSWORD = "1234"

# =========================
# CLEAN TEXT
# =========================
def clean(text):
    text = text.lower()
    text = re.sub(r"[.,;:!?\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================
# MEMORY LOAD/SAVE
# =========================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

memory = load_memory()

# =========================
# SESSION STATE
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================
# SAFE MEMORY SEARCH
# =========================
def get_answer(q):
    q = clean(q)

    if q in memory:
        return memory[q]

    match = difflib.get_close_matches(q, list(memory.keys()), n=1, cutoff=0.6)
    if match:
        return memory[match[0]]

    return None

# =========================
# UI (IMPORTANT FIX HERE)
# =========================
st.set_page_config(page_title="AI Bot", layout="centered")

st.title("🤖 Simple AI Bot")

# =========================
# CHAT INPUT (BOTTOM FIXED STYLE)
# =========================
user_input = st.text_input("Сұрақ жаз:")

if st.button("Жіберу") and user_input:

    st.session_state.chat.append(("Сен", user_input))

    answer = get_answer(user_input)

    if answer:
        bot = "🧠 Memory: " + answer
    else:
        bot = "❌ Мен білмеймін (admin үйрету керек)"

    st.session_state.chat.append(("Бот", bot))

# =========================
# CHAT DISPLAY (NORMAL POSITION FIX)
# =========================
st.divider()

for role, msg in st.session_state.chat:
    if role == "Сен":
        st.markdown(f"🧑 **Сен:** {msg}")
    else:
        st.markdown(f"🤖 **Бот:** {msg}")

# =========================
# SIDEBAR ADMIN
# =========================
st.sidebar.title("🔐 Admin")

pw = st.sidebar.text_input("Пароль", type="password")

if st.sidebar.button("Login"):
    if pw == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.sidebar.success("Admin ON 🔥")

if st.session_state.is_admin:
    st.sidebar.markdown("### 🧠 Үйрету")

    q = st.sidebar.text_input("Сұрақ")
    a = st.sidebar.text_input("Жауап")

    if st.sidebar.button("Сақтау"):
        if q and a:
            memory[clean(q)] = a
            save_memory(memory)
            st.sidebar.success("Сақталды ✔")

# =========================
# EXTRA
# =========================
if st.sidebar.button("Memory көру"):
    st.sidebar.write(memory)

if st.sidebar.button("Чатты тазалау"):
    st.session_state.chat = []
