import os
import time
import glob
import base64

import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import Button, CustomJS
from PIL import Image
from googletrans import Translator
from gtts import gTTS

# Configurar página y tema
st.set_page_config(page_title="🎤 Traductor Creativo", page_icon="🌐", layout="wide")

# Estilos personalizados
st.markdown("""
<style>
  /* Fondo animado con efecto pulse */
  @keyframes pulse {
    0% { background-color: #1a1a2e; }
    50% { background-color: #16213e; }
    100% { background-color: #1a1a2e; }
  }
  .css-18e3th9 { animation: pulse 8s ease infinite; }
  .block-container {
    padding: 2rem;
    border-radius: 1rem;
    background: rgba(255,255,255,0.05);
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }
  h1 { text-align: center; }
  .stButton > button {
    background: linear-gradient(90deg, #ff8c00, #e52e71);
    color: white;
    border: none;
    border-radius: 0.75rem;
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    transition: transform 0.2s;
  }
  .stButton > button:hover { transform: scale(1.05); box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
  .streamlit-expanderHeader { font-weight: bold; font-size: 1.1rem; color: #ff8c00; }
</style>
""", unsafe_allow_html=True)

# Título y portada
st.title("🌐 Traductor Interactivo y Divertido")
st.image(Image.open('OIG7.jpg'), width=250)

# Sidebar con instrucciones
with st.sidebar:
    st.header("Cómo usar")
    st.write(
        "1️⃣ Pulsa **Iniciar** para grabar tu voz.\n"
        "2️⃣ Habla la frase a traducir.\n"
        "3️⃣ Pulsa **Detener** para enviar el texto.\n"
        "4️⃣ Elige idiomas y descarga el audio." 
    )

# Área de grabación con dos botones
st.markdown("**Habla aquí 🎤:**")
col1, col2 = st.columns(2, gap="large")
with col1:
    start_btn = Button(label="Iniciar", width=200, height=50)
    start_btn.js_on_event('button_click', CustomJS(code="""
        window.recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'es-ES';
        recognition.onresult = e => {
            const text = e.results[0][0].transcript;
            document.dispatchEvent(new CustomEvent('GET_TEXT', {detail: text}));
        };
        recognition.start();
    """))
with col2:
    stop_btn = Button(label="Detener", width=200, height=50)
    stop_btn.js_on_event('button_click', CustomJS(code="""
        if(window.recognition) recognition.stop();
    """))

# Esperar evento GET_TEXT desde iniciar
event = streamlit_bokeh_events(
    start_btn,
    events='GET_TEXT',
    key='voice',
    override_height=60,
    debounce_time=0
)

# Procesar resultado y traducción
def process_translation(text):
    st.success(f"📝 Has dicho: {text}")
    LANGS = {
        '🇪🇸 Español':'es', '🇬🇧 Inglés':'en', '🇨🇳 Mandarín':'zh-cn',
        '🇰🇷 Coreano':'ko', '🇯🇵 Japonés':'ja', '🇧🇩 Bengalí':'bn'
    }
    in_lang = st.selectbox('🔄 Origen', list(LANGS.keys()), index=0)
    out_lang = st.selectbox('🔁 Destino', list(LANGS.keys()), index=1)
    if st.button('🔄 Traducir y Generar Audio'):
        with st.spinner('Traduciendo...'):
            translated = Translator().translate(text, src=LANGS[in_lang], dest=LANGS[out_lang]).text
        with st.spinner('Creando Audio...'):
            tts = gTTS(translated, lang=LANGS[out_lang], slow=False)
            os.makedirs('temp', exist_ok=True)
            fname = f"trans_{int(time.time())}.mp3"
            path = os.path.join('temp', fname)
            tts.save(path)
        st.balloons()
        with st.expander('Texto Traducido'):
            st.write(translated)
        b64 = base64.b64encode(open(path,'rb').read()).decode()
        dl = f"<a href='data:audio/mp3;base64,{b64}' download='{fname}' style='color:#e52e71; font-weight:bold; font-size:1.1rem;'>🎧 Descargar Audio</a>"
        st.markdown(dl, unsafe_allow_html=True)

if event and 'GET_TEXT' in event:
    process_translation(event['GET_TEXT'])

# Limpieza de archivos antiguos
def cleanup(days=7):
    now = time.time()
    for f in glob.glob('temp/*.mp3'):
        if os.stat(f).st_mtime < now - days*86400:
            os.remove(f)
cleanup()
