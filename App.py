import streamlit as st
import json
import os
import difflib
import re

# =========================
# SETTINGS
# =========================
MEMORY_FILE = "memory.json"
ADMIN_PASSWORD = "nurik777"

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
        return json.load(open(MEMORY_FILE, "r", encoding="utf-8"))
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

if "freq" not in st.session_state:
    st.session_state.freq = {}

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================
# LOGIN ADMIN
# =========================
st.sidebar.title("🔐 Панель администратора")

password = st.sidebar.text_input("Пароль", type="password")

if st.sidebar.button("Войти"):
    if password == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.sidebar.success("Режим администратора включён 🔥")
    else:
        st.sidebar.error("Неверный пароль")

# =========================
# ОБУЧЕНИЕ (ТОЛЬКО АДМИН)
# =========================
if st.session_state.is_admin:
    st.sidebar.markdown("### 🧠 Обучение бота")

    q = st.sidebar.text_input("Вопрос")
    a = st.sidebar.text_input("Ответ")

    if st.sidebar.button("Сохранить"):
        if q and a:
            memory[clean(q)] = {
                "answer": a,
                "count": 0
            }
            save_memory(memory)
            st.sidebar.success("Сохранено ✔")

# =========================
# AI ЛОГИКА
# =========================
def ai(question):
    q = clean(question)

    # точное совпадение
    if q in memory:
        memory[q]["count"] += 1
        save_memory(memory)
        return memory[q]["answer"]

    # похожие вопросы
    keys = list(memory.keys())
    match = difflib.get_close_matches(q, keys, n=1, cutoff=0.6)

    if match:
        k = match[0]
        memory[k]["count"] += 1
        save_memory(memory)
        return memory[k]["answer"]

    return None

# =========================
# UI
# =========================
st.title("🤖 Ultra AI Ассистент (ChatGPT стиль)")

user = st.text_input("Введите вопрос:")

if st.button("Отправить") and user:

    st.session_state.chat.append(("Вы", user))
    st.session_state.freq[clean(user)] = st.session_state.freq.get(clean(user), 0) + 1

    answer = ai(user)

    if answer:
        bot = f"🧠 По моей памяти:\n{answer}"
    else:
        bot = (
            "❌ Я не знаю ответа.\n"
            "🔐 Администратор должен обучить меня или добавить информацию."
        )

    st.session_state.chat.append(("Бот", bot))

# =========================
# CHAT DISPLAY
# =========================
for role, msg in st.session_state.chat:
    if role == "Вы":
        st.markdown(f"🧑 **Вы:** {msg}")
    else:
        st.markdown(f"🤖 **Бот:** {msg}")

# =========================
# SIDEBAR STATS
# =========================
st.sidebar.title("📊 Статистика")

if st.sidebar.button("Показать память"):
    st.sidebar.write(memory)

if st.sidebar.button("Частые вопросы"):
    st.sidebar.write(
        dict(sorted(st.session_state.freq.items(), key=lambda x: x[1], reverse=True))
    )

if st.sidebar.button("Очистить чат"):
    st.session_state.chat = []

if st.sidebar.button("Сброс памяти"):
    memory = {}
    save_memory(memory)
    st.sidebar.success("Очищено")
