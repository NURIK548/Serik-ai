import streamlit as st
import wikipedia
import requests
import re
import base64
from gtts import gTTS
import io
import random
from requests.utils import quote

Беттің баптаулары

st.set_page_config(page_title="Serik-Ai PRO Max", layout="wide")
wikipedia.set_lang("ru") # Орысша іздеу

Дизайн (қара фон, ақ жазу)

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
.stMarkdown, p, h1, h2, h3, span, label { color: white !important; }
.stChatInput textarea { background-color: #1a1f2c !important; color: white !important; border: 1px solid #3a3f50 !important; }
.photo-box {
width: 100%;
max-width: 750px;
border-radius: 12px;
border: 2px solid #3a3f50;
overflow: hidden;
margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

Дауыс шығару HTML-ы

def get_audio_html(text):
try:
clean_txt = re.sub(r'[^\w\sа-яА-ЯёЁ]', '', text)[:200]
tts = gTTS(text=clean_txt, lang='ru')
fp = io.BytesIO()
tts.write_to_fp(fp)
fp.seek(0)
audio_b64 = base64.b64encode(fp.read()).decode()
return f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_b64}">'
except: return ""

ГУГЛДАН ЖҮЗДЕГЕН САЙТТАРДЫ СҮЗІП, СӨЙЛЕМ ҚҰРАУ ФУНКЦИЯСЫ

def search_google_and_compose(topic):
try:
# Гуглдың ашық іздеу жүйесінен мәліметтер жинау
search_url = f"https://html.duckduckgo.com/html/?q={quote(topic)}"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
res = requests.get(search_url, headers=headers, timeout=5)

if res.status_code == 200:  
        # Сайттардың сипаттамаларын (snippet) тауып алу  
        snippets = re.findall(r'<td class="result-snippet">(.*?)</td>', res.text, re.DOTALL)  
        if snippets:  
            composed_text = ""  
            # Табылған мәліметтерді тазалап, біріктіріп сөйлем құрау  
            for snip in snippets[:4]:  # Ең негізгі 4 сайттың дерегін аламыз  
                clean_snip = re.sub(r'<[^>]+>', '', snip).strip() # HTML тегтерді өшіру  
                composed_text += clean_snip + " "  
            return composed_text  
except: pass  
return ""

Ботпен амандасу

if "messages" not in st.session_state:
st.session_state.messages = []
welcome = "Привет! Я Serik-Ai PRO Max. Текст, рефераты, поиск по сотням сайтов Гугла и генерация чистых фото — всё готово к работе!"
st.session_state.messages.append({"role": "assistant", "content": welcome})
st.markdown(get_audio_html(welcome), unsafe_allow_html=True)

for message in st.session_state.messages:
with st.chat_message(message["role"]):
st.markdown(message["content"])

НЕГІЗГІ АҚПАРАТ ПЕН ФОТО ДВИЖОГЫ

def get_smart_content(q):
q_low = q.lower().strip()

# 1. Тез жауаптар  
fast_answers = {  
    "привет": "Привет! Я готов к работе. О чем написать?",  
    "как дела": "Отлично! Мои сервера работают на полную мощь.",  
    "кто тебя создал": "Меня создал гениальный Нұрик!"  
}  
if q_low in fast_answers: return fast_answers[q_low]  

# 2. ТАЗА ФОТО ГЕНЕРАТОР (Егер промптта фото сөзі болса)  
if "фото" in q_low or "картинка" in q_low or "нарисуй" in q_low or "рисунок" in q_low:  
    photo_topic = q_low.replace("фото", "").replace("картинку", "").replace("нарисуй", "").replace("рисунок", "").replace("сделай", "").strip()  
    if not photo_topic: photo_topic = "scifi city"  
      
    seed = random.randint(1, 999999)  
    img_url = f"https://image.pollinations.ai/p/{quote(photo_topic)}?width=800&height=600&seed={seed}&nofeed=true"  
      
    # Фотоны экранға таза күйінде шығару  
    photo_html = f"""  
    <div class="photo-box">  
        <img src="{img_url}" style="width:100%; height:auto; display:block;">  
    </div>  
    """  
    st.markdown(photo_html, unsafe_allow_html=True)  
    return f"Изображение по вашему запросу '{photo_topic}' успешно сгенерировано!"  

# 3. МӘТІН ЖӘНЕ СӨЙЛЕМ ҚҰРАУ ОРНЫ  
topic = q.replace("напиши", "").replace("реферат", "").replace("эссе", "").replace("про", "").replace("на тему", "").strip()  
  
# Алдымен Википедияны тексереміз  
wiki_summary = ""  
wiki_content = ""  
try:  
    page = wikipedia.page(topic)  
    wiki_content = page.content  
    wiki_summary = page.summary  
except: pass  

# Гугл мен жүздеген сайттардан қосымша ақпарат жинап, сөйлем құрау  
google_composed_info = search_google_and_compose(topic)  

# Егер екі жақтан да түк табылмаса  
if not wiki_summary and not google_composed_info:  
    return f"Я искал на сотнях сайтов Гугла и в Википедии про '{topic}', но ничего не нашлось. Попробуй написать тему точнее."  

# Барлық жиналған деректерді біріктіріп, мәтін құрастыру  
main_intel_data = wiki_summary if wiki_summary else google_composed_info  
extended_data = wiki_content[:4000] if wiki_content else google_composed_info  

# Сұраныс форматы бойынша мәтінді дайындау  
if "реферат" in q_low:  
    full_ref = f"### РЕФЕРАТ: {topic.upper()}\n\n"  
    full_ref += f"**Введение:** {main_intel_data}\n\n"  
    full_ref += f"**Основная часть (Анализ интернет-ресурсов):**\n{extended_data}...\n\n"  
    full_ref += "**Заключение:** Проведенный анализ на основе сотен сетевых источников показывает высокую историческую и практическую важность данной темы."  
    return full_ref  
  
elif "эссе" in q_low:  
    return f"### ЭССЕ НА ТЕМУ: {topic.upper()}\n\n**Мое мнение и анализ источников:** Данная тематика вызывает много споров в сети. На основе изученных материалов сайтов, можно утверждать следующее: {main_intel_data} Это доказывает актуальность вопроса в наше время."  
      
else:  
    # Жай сұраныс болса, қысқаша талдауды береді  
    return f"### Результат анализа по запросу: {topic}\n\n{main_intel_data}"

Жазу жолағы

if prompt := st.chat_input("Напиши реферат про Александра Македонского или сделай фото робота..."):
st.session_state.messages.append({"role": "user", "content": prompt})
with st.chat_message("user"): st.markdown(prompt)

with st.chat_message("assistant"):  
    response = get_smart_content(prompt)  
    st.markdown(response)  
    # Жауаптың басын дауыстап оқу  
    st.markdown(get_audio_html(response), unsafe_allow_html=True)  
    st.session_state.messages.append({"role": "assistant", "content": response})

Мына кодты дұрыстап берші импорт Википедия қате кетті диді стреамлит гитхуб арқылы істедім
