import streamlit as st
import requests
import urllib.parse

def generate_image(user_prompt):
    """Суретті ChatGPT (DALL-E) сияқты сапалы әрі лагсыз, өте тез шығаратын функция"""
    # Суреттің сапасын арттыру үшін арнайы стиль сөздерін қосамыз
    enhanced_prompt = (
        f"{user_prompt}, cinematic lighting, photorealistic, hyper-detailed, "
        f"8k resolution, masterpiece, digital art"
    )
    
    # Мәтінді URL форматына қауіпсіз түрде түрлендіреміз (қате кетпеу үшін)
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    
    # Тегін, өте жылдам және сапалы Flux/StableDiffusion моделі (Токен керек емес!)
    API_URL = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&enhanced=true"
    
    try:
        response = requests.get(API_URL, timeout=15)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception:
        return None

# --- STREAMLIT ИНТЕРФЕЙСІ (БАРЛЫҒЫ БҰРЫНҒЫДАЙ ҚАЛДЫ) ---
st.set_page_config(page_title="Serik-Ai PRO Max", page_icon="🤖", layout="centered")
st.title("🤖 Serik-Ai PRO Max")
st.caption("Нұриктің ресми боты — Жылдам әрі сапалы!")

# Сессияны тексеру (Экран қатып қалмауы және хабарламалар жоғалмауы үшін)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ескі чат тарихын экранға қайта шығару
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"])

# Пайдаланушыдан сұраныс алу
if user_input := st.chat_input("Маған жаз немесе 'сурет: машина' деп тапсырыс бер"):
    
    # 1. Пайдаланушының жазғанын экранға шығару және жадқа сақтау
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "type": "text", "content": user_input})
    
    # 2. Боттың жауабы
    with st.chat_message("assistant"):
        # ЕГЕР ПАЙДАЛАНУШЫ СУРЕТ СҰРАСА
        if user_input.lower().startswith("сурет:") or user_input.lower().startswith("photo:"):
            # "сурет:" деген сөзді кесіп тастап, нақты промптты аламыз
            if ":" in user_input:
                prompt_to_send = user_input.split(":", 1)[1].strip()
            else:
                prompt_to_send = user_input.strip()
            
            if prompt_to_send:
                with st.spinner("Сурет салынуда, күте тұр..."):
                    image_bytes = generate_image(prompt_to_send)
                
                if image_bytes:
                    st.image(image_bytes, caption=f"Генерацияланған сурет: {prompt_to_send}")
                    # Суретті чат тарихына сақтаймыз
                    st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_bytes})
                else:
                    st.error("Қателік: Сервер жауап бермеді. Қайтадан байқап көр.")
            else:
                st.warning("Сурет салу үшін 'сурет: [не салу керек]' деп толық жаз.")
        
        # ЕГЕР ЖАЙ МӘТІН ЖАЗЫЛСА
        else:
            ai_response = f"Сәлем! Сенің сұранысыңды қабылдадым: '{user_input}'. Сурет салғың келсе, басына 'сурет:' деп жаз!"
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "type": "text", "content": ai_response})
