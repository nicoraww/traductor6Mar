import os
import time
import glob
import base64

import streamlit as st
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
from googletrans import Translator
from gtts import gTTS

# Configurar página y tema
st.set_page_config(
    page_title="🎤 Traductor Interactivo", 
    page_icon="🌍", 
    layout="wide"
)

# Estilos simples para contenedor e imagen
st.markdown("""
<style>
  .block-container { padding: 2rem 3rem; border-radius: 12px; background-color: #f0f8ff; }
  img { border-radius: 1rem; }
  .stButton > button { font-size: 1rem; padding: 0.6rem 1.2rem; }
  .language-selectbox label { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🎤 Traductor de Voz y Texto")

# Banner superior con imagen nueva
st.image(Image.open('translator_banner.png'), use_column_width=True)

# Selección de idiomas ANTES de grabar
st.markdown("### 🌐 Configuración de Idiomas")
LANG_OPTIONS = {
    '🇪🇸 Español': 'es',
    '🇬🇧 English': 'en',
    '🇨🇳 中文': 'zh-cn',
    '🇰🇷 한국어': 'ko',
    '🇯🇵 日本語': 'ja',
    '🇧🇩 বাংলা': 'bn'
}
col_in, col_out = st.columns(2)
with col_in:
    in_lang_key = st.selectbox("🔄 Idioma de Origen", list(LANG_OPTIONS.keys()), key="in_lang")
with col_out:
    out_lang_key = st.selectbox("🔁 Idioma de Destino", list(LANG_OPTIONS.keys()), key="out_lang")

# Área de grabación
st.markdown("### 🗣️ Graba tu voz")
col1, col2 = st.columns(2, gap="medium")
with col1:
    rec_btn = Button(label="Iniciar 🎙️", width=200, height=50)
    rec_btn.js_on_event('button_click', CustomJS(code="""
        window.recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = '%s';
        recognition.onresult = e => {
            const txt = e.results[0][0].transcript;
            document.dispatchEvent(new CustomEvent('GET_TEXT', {detail: txt}));
        };
        recognition.start();
    """ % LANG_OPTIONS[in_lang_key]))
with col2:
    stop_btn = Button(label="Detener 🛑", width=200, height=50)
    stop_btn.js_on_event('button_click', CustomJS(code="""
        if(window.recognition) recognition.stop();
    """))

# Capturar evento de voz
event = streamlit_bokeh_events(
    rec_btn,
    events='GET_TEXT',
    key='voice_event',
    override_height=75,
    debounce_time=0
)

# Cuando haya texto, mostrar y convertir
def handle_voice(text):
    st.success(f"📝 Reconocido: {text}")
    # Solo estética, no cambia lógica
    if st.button('🔄 Traducir y Descargar Audio'):
        # Traducir
        traslator = Translator()
        translated = traslator.translate(text,
                                         src=LANG_OPTIONS[in_lang_key],
                                         dest=LANG_OPTIONS[out_lang_key]).text
        # Generar audio
        tts = gTTS(translated, lang=LANG_OPTIONS[out_lang_key], slow=False)
        os.makedirs('temp', exist_ok=True)
        fname = f"tts_{int(time.time())}.mp3"
        fpath = os.path.join('temp', fname)
        tts.save(fpath)
        # Descarga creativa
        b64 = base64.b64encode(open(fpath,'rb').read()).decode()
        link = f"<a href='data:audio/mp3;base64,{b64}' download='{fname}' style='font-size:1.1rem; color:#0066cc;'>🎧 Descargar Audio</a>"
        st.markdown(link, unsafe_allow_html=True)
        # Mostrar traducción
        with st.expander('🔍 Ver Traducción'):
            st.write(translated)

if event and 'GET_TEXT' in event:
    handle_voice(event['GET_TEXT'])

# Limpieza de archivos antiguos
def cleanup(days=7):
    cutoff = time.time() - days * 86400
    for f in glob.glob('temp/*.mp3'):
        if os.stat(f).st_mtime < cuto
