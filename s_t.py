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

# Estilos para texto en negro en toda la app
st.markdown("""
<style>
  /* Aplicar color negro a la mayor parte de texto */
  * {
    color: #000000 !important;
  }
  /* Cuerpo y contenedor */
  .block-container {
    padding: 2rem 3rem;
    border-radius: 12px;
    background-color: #f0f8ff;
  }
  /* Botones y enlaces */
  .stButton > button {
    font-size: 1rem;
    padding: 0.6rem 1.2rem;
    color: #000000 !important;
    border: 1px solid #000000;
  }
  a {
    color: #000000 !important;
  }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🎤 Traductor de Voz y Texto")

# Banner superior con imagen nueva
if os.path.exists('translator_banner.png'):
    st.image(Image.open('translator_banner.png'), use_column_width=True)

# Selección de idiomas antes de grabar
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
    rec_btn.js_on_event('button_click', CustomJS(code=f"""
        window.recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = '{LANG_OPTIONS[in_lang_key]}';
        recognition.onresult = e => {{
            const txt = e.results[0][0].transcript;
            document.dispatchEvent(new CustomEvent('GET_TEXT', {{detail: txt}}));
        }};
        recognition.start();
    """))
with col2:
    stop_btn = Button(label="Detener 🛑", width=200, height=50)
    stop_btn.js_on_event('button_click', CustomJS(code="""
        if (window.recognition) recognition.stop();
    """))

# Capturar evento de voz
voice_event = streamlit_bokeh_events(
    rec_btn,
    events='GET_TEXT',
    key='voice_event',
    override_height=75,
    debounce_time=0
)

# Manejar texto reconocido y traducir
if voice_event and 'GET_TEXT' in voice_event:
    text = voice_event['GET_TEXT']
    st.success(f"📝 Reconocido: {text}")
    if st.button('🔄 Traducir y Descargar Audio'):
        # Traducir texto
        translator = Translator()
        translated = translator.translate(
            text,
            src=LANG_OPTIONS[in_lang_key],
            dest=LANG_OPTIONS[out_lang_key]
        ).text
        # Generar audio
        tts = gTTS(translated, lang=LANG_OPTIONS[out_lang_key], slow=False)
        os.makedirs('temp', exist_ok=True)
        filename = f"tts_{int(time.time())}.mp3"
        filepath = os.path.join('temp', filename)
        tts.save(filepath)
        # Enlace de descarga
        audio_bytes = open(filepath, 'rb').read()
        b64 = base64.b64encode(audio_bytes).decode()
        download_link = (
            f"<a href='data:audio/mp3;base64,{b64}' download='{filename}'"
            " style='font-size:1.1rem;'>🎧 Descargar Audio</a>"
        )
        st.markdown(download_link, unsafe_allow_html=True)
        # Mostrar traducción
        with st.expander('🔍 Ver Traducción'):
            st.write(translated)

# Limpieza de archivos antiguos
def cleanup(days=7):
    cutoff = time.time() - days * 86400
    for f in glob.glob('temp/*.mp3'):
        if os.stat(f).st_mtime < cutoff:
            os.remove(f)

cleanup()
