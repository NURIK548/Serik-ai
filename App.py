import streamlit as st
import requests
import urllib.parse

def generate_image(user_prompt):
    """Генерация бесконечных и высококачественных изображений"""
    # Улучшаем качество картинки до максимума
    enhanced_prompt = (
        f"{user_prompt}, 8k resolution, ultra-detailed, masterpiece, "
        f"high quality, photorealistic, cinematic lighting"
    )
    
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    
    # Бесконечный и бесплатный API для HD картинок
    API_URL = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        response = requests.get(API_URL, timeout=20)
        if response.status_code == 200:
            return response.content
        return None
    except Exception:
        return None

# --- ИНТЕРФЕЙС STREAMLIT ---
st.set_page_config(page_title="Serik-Ai PRO Max", page_icon="🤖", layout="centered")
st.title("🤖 Serik-Ai PRO Max")
st.caption("Умный бот: Пишет тексты, рисует HD-картинки и не лагает!")

# Инициализация памяти чата (чтобы рефераты и картинки не пропадали)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отрисовка всей истории чата (сохраняется при любых действиях)
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"])
            # Кнопка для скачивания картинки прямо из истории
            st.download_button(
                label="📥 Скачать в HD",
                data=message["content"],
                file_name=f"SerikAI_image_{index}.jpg",
                mime="image/jpeg",
                key=f"download_btn_{index}"
            )

# Ввод пользователя
if user_input := st.chat_input("Напиши реферат или попроси нарисовать картинку..."):
    
    # 1. Показываем запрос пользователя
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "type": "text", "content": user_input})
    
    # 2. Логика ответа бота
    with st.chat_message("assistant"):
        user_text = user_input.lower()
        
        # Умный поиск: бот сам понимает, если просят картинку, даже с ошибками
        image_keywords = ["картинка", "фото", "нарисуй", "сурет", "сделай фото", "изображение"]
        is_image_request = any(keyword in user_text for keyword in image_keywords)
        
        if is_image_request:
            with st.spinner("Создаю шедевр в HD качестве..."):
                image_bytes = generate_image(user_input)
            
            if image_bytes:
                st.image(image_bytes, caption="Готово! Вы можете скачать изображение ниже.")
                
                # Кнопка скачивания для новой картинки (чтобы скачать сразу)
                st.download_button(
                    label="📥 Скачать в HD",
                    data=image_bytes,
                    file_name="SerikAI_new_image.jpg",
                    mime="image/jpeg",
                    key=f"dl_new_{len(st.session_state.messages)}"
                )
                
                # Сохраняем картинку в историю
                st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_bytes})
            else:
                error_msg = "Ой, что-то пошло не так с сервером. Попробуй еще раз!"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": error_msg})
        
        # ЕСЛИ ЭТО ТЕКСТ (Рефераты, вопросы и т.д.)
        else:
            # Здесь в будущем будет подключена твоя текстовая нейросеть
            # Пока что он просто подтверждает, что сохранил текст
            ai_response = f"Я сохранил твой текст: '{user_input}'. Если это был реферат, он останется в истории навсегда!"
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "type": "text", "content": ai_response})
