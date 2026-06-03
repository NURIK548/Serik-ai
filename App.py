import streamlit as st
import json
import os
import difflib
import re

# =========================
# SETTINGS
# =========================
MEMORY_FILE = "memory.json"
ADMIN_PASSWORD = "1234"  # өзгерт

# =========================
# CLEAN TEXT
# =========================
def clean(text):
    text = text.lower()
    text = re.sub(r"[.,;:!?\"'()\[\]{}]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================
# LOAD / SAVE MEMORY
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
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "chat" not in st.session_state:
    st.session_state.chat = []

if "freq" not in st.session_state:
    st.session_state.freq = {}

# =========================
# LOGIN
# =========================
st.sidebar.title("🔐 Admin Panel")

password = st.sidebar.text_input("Admin password", type="password")

if st.sidebar.button("Login"):
    if password == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.sidebar.success("Admin mode ON 🔥")
    else:
        st.sidebar.error("Wrong password")

# =========================
# TEACH MODE (ADMIN ONLY)
# =========================
if st.session_state.is_admin:
    st.sidebar.markdown("### 🧠 Teach Bot")

    new_q = st.sidebar.text_input("Question")
    new_a = st.sidebar.text_input("Answer")

    if st.sidebar.button("Save"):
        if new_q and new_a:
            q = clean(new_q)
            memory[q] = {
                "answer": new_a,
                "times_used": 0
            }
            save_memory(memory)
            st.sidebar.success("Saved ✔")

# =========================
# SMART SEARCH
# =========================
def get_answer(question):
    q = clean(question)

    # exact match
    if q in memory:
        memory[q]["times_used"] += 1
        save_memory(memory)
        return memory[q]["answer"]

    # fuzzy match
    keys = list(memory.keys())
    match = difflib.get_close_matches(q, keys, n=1, cutoff=0.6)

    if match:
        key = match[0]
        memory[key]["times_used"] += 1
        save_memory(memory)
        return memory[key]["answer"]

    return None

# =========================
# UI
# =========================
st.title("🤖 Admin AI Bot (Serik Edition)")

user_input = st.text_input("Сұрақ жаз:")

if st.button("Send") and user_input:

    q = clean(user_input)

    # frequency
    st.session_state.freq[q] = st.session_state.freq.get(q, 0) + 1

    st.session_state.chat.append(("Сен", user_input))

    answer = get_answer(user_input)

    if answer:
        bot_reply = "🧠 Memory: " + answer
    else:
        bot_reply = "❌ Мен білмеймін. Admin үйретуі керек."

    st.session_state.chat.append(("Бот", bot_reply))

# =========================
# CHAT DISPLAY
# =========================
for role, msg in st.session_state.chat:
    if role == "Сен":
        st.markdown(f"🧑 **Сен:** {msg}")
    else:
        st.markdown(f"🤖 **Bot:** {msg}")

# =========================
# SIDEBAR STATS
# =========================
st.sidebar.title("📊 Stats")

if st.sidebar.button("Show memory"):
    st.sidebar.write(memory)

if st.sidebar.button("Frequent questions"):
    st.sidebar.write(
        dict(sorted(st.session_state.freq.items(), key=lambda x: x[1], reverse=True))
    )

if st.sidebar.button("Clear chat"):
    st.session_state.chat = []

if st.sidebar.button("Reset memory"):
    memory = {}
    save_memory(memory)
    st.sidebar.success("Memory cleared")
