import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Estilos minimalistas
st.markdown("""
<style>
  body { background-color: #ffffff; color: #000000; }
  .block-container { background: #ffffff; border-radius: 8px; padding: 2rem; max-width: 600px; margin: auto; }
  /* Botones en negro con texto blanco */
  .stButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-size: 1rem;
  }
  .stButton > button:hover {
    background-color: #333333 !important;
  }
  h1, h2, h3, label, .stMarkdown { color: #000000 !important; }
  .stSelectbox > div > div > div { color: #000000; }
  @keyframes floatEmoji { 0% { transform: translateY(0); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0); } }
  .emoji-flag { display: inline-block; animation: floatEmoji 3s ease-in-out infinite; font-size: 2rem; margin: 0 0.25rem; }
</style>
""", unsafe_allow_html=True)

# Título
st.title("🎙️ Traductor de Voz")
st.subheader("Habla y convierte a audio traducido")

# Cliente de traducción
translator = Translator()

# Botón de grabación
st.write("**Pulsa el botón y habla**")
rec_btn = Button(label="🔈 Grabar", width=200, height=50)
rec_btn.js_on_event(
    "button_click",
    CustomJS(code="""
        const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
        const rec = new Rec();
        rec.continuous = false;
        rec.interimResults = false;
        rec.onresult = e => {
            const txt = e.results[0][0].transcript;
            document.dispatchEvent(new CustomEvent('GET_TEXT', { detail: txt }));
        };
        rec.start();
    """),
)

# Capturar resultado de voz
result = streamlit_bokeh_events(
    rec_btn,
    events="GET_TEXT",
    key="voice",
    override_height=75,
    debounce_time=0
)

if result and 'GET_TEXT' in result:
    text = result['GET_TEXT']
    st.write(f"**Texto reconocido:** {text}")

    # Selección de idiomas con emojis animadas
    LANGS = {
        '🇪🇸 Español':'es',
        '🇬🇧 English':'en',
        '🇨🇳 中文':'zh-cn',
        '🇰🇷 한국어':'ko',
        '🇯🇵 日本語':'ja',
        '🇧🇩 বাংলা':'bn'
    }
    col1, col2 = st.columns(2, gap='large')
    with col1:
        origin_sel = st.selectbox('🔄 Origen', list(LANGS.keys()), index=0)
        st.markdown(f"<span class='emoji-flag'>{origin_sel.split()[0]}</span>", unsafe_allow_html=True)
    with col2:
        dest_sel = st.selectbox('🔁 Destino', list(LANGS.keys()), index=1)
        st.markdown(f"<span class='emoji-flag'>{dest_sel.split()[0]}</span>", unsafe_allow_html=True)

    # Mapear a códigos de idioma
    in_lang = LANGS[origin_sel]
    out_lang = LANGS[dest_sel]

    # Conversión a audio
    if st.button('🔄 Convertir y descargar'):
        translated_text = translator.translate(text, src=in_lang, dest=out_lang).text
        tts = gTTS(translated_text, lang=out_lang)
        os.makedirs('temp', exist_ok=True)
        fname = f"out_{int(time.time())}.mp3"
        path = os.path.join('temp', fname)
        tts.save(path)
        with open(path, 'rb') as f:
            st.download_button(label='⬇️ Descargar Audio', data=f, file_name=fname, mime='audio/mp3')

# Limpieza de archivos antiguos
def cleanup(days=7):
    cutoff = time.time() - days*86400
    for f in glob.glob('temp/*.mp3'):
        if os.stat(f).st_mtime < cutoff:
            os.remove(f)

cleanup()
