import streamlit as st
import json
import random

# =========================
# MEMORY LOAD / SAVE
# =========================
def load_memory():
    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_memory_file(data):
    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

memory_db = load_memory()

# =========================
# SMART NORMALIZER
# =========================
def normalize(text):
    text = text.lower()

    variants = {
        "как дела": ["как дела", "как ты", "как жизнь", "как оно", "че как", "как сам", "как поживаешь", "как у тебя"],
        "хорошо": ["хорошо", "норм", "ок", "все ок", "всё ок", "нормально", "отлично", "супер", "класс"]
    }

    for key, words in variants.items():
        if text in words:
            return key

    return text

# =========================
# MEMORY SAVE (context)
# =========================
context_memory = {}

def set_context(user_id, text):
    context_memory[user_id] = text

def get_context(user_id):
    return context_memory.get(user_id, "")

# =========================
# BOT LOGIC
# =========================
def bot_reply(user_id, text):

    text = normalize(text)

    # follow-up style
    followups = [
        "Что делаешь сейчас?",
        "Расскажи подробнее 😎",
        "Чем занимаешься?",
        "Интересно 🤔 продолжай"
    ]

    base = {
        "как дела": "Отлично 😎 А у тебя как?",
        "хорошо": "Круто 🔥 Рад за тебя!"
    }

    reply = base.get(text)

    # MEMORY learning (simple)
    if not reply:
        memory_db[text] = "Я запомнил это 👍"
        save_memory_file(memory_db)
        reply = "Я пока не знаю ответ, но я запомнил это 🤖"

    # context reaction
    last = get_context(user_id)
    set_context(user_id, text)

    if last:
        reply = reply + f" (Ты раньше говорил: '{last}')"

    return reply + " " + random.choice(followups)

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Serik-AI PRO", layout="wide")

st.title("🤖 Serik-AI PRO MAX")

user_id = st.text_input("User ID", "user1")
user_input = st.text_input("Сұрақ жаз:")

if st.button("Send"):
    if user_input:
        answer = bot_reply(user_id, user_input)
        st.success(answer)
