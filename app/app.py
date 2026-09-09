"""
app.py
------
Streamlit front-end for the Multilingual AI Text-to-Speech Assistant.

Run with:
    streamlit run app/app.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
from language_detect import detect_language, SUPPORTED_LANGUAGES
from tts_engine import synthesize, UnsupportedLanguageError
from audio_utils import estimate_duration_seconds
from translator import translate_text, TranslationError

st.set_page_config(page_title="Multilingual AI TTS Assistant", page_icon="🔊", layout="centered")

st.title("🔊 Multilingual AI Text-to-Speech Assistant")
st.caption("Type or paste text in any supported language — the app detects the language "
           "automatically and reads it aloud.")

with st.sidebar:
    st.header("Settings")
    auto_detect = st.checkbox("Auto-detect language", value=True)
    manual_lang = st.selectbox(
        "Manual language (used if auto-detect is off, or as override)",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda code: f"{SUPPORTED_LANGUAGES[code]} ({code})",
    )
    slow_speech = st.checkbox("Slow speech", value=False)
    st.markdown("---")
    st.markdown("**Translation**")
    translate_enabled = st.checkbox(
        "Translate before speaking", value=False,
        help="Translates the detected/selected language into a language of "
             "your choice before generating speech. Works between any two "
             "of the supported languages.",
    )
    translate_target = None
    if translate_enabled:
        translate_target = st.selectbox(
            "Translate to",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda code: f"{SUPPORTED_LANGUAGES[code]} ({code})",
        )
    st.markdown("---")
    st.markdown("**Supported languages:**")
    for code, name in SUPPORTED_LANGUAGES.items():
        st.markdown(f"- {name} (`{code}`)")

text_input = st.text_area(
    "Enter text",
    height=160,
    placeholder="e.g. Hello, how are you today?  /  Hola, \u00bfc\u00f3mo est\u00e1s?  /  \u4f60\u597d\uff0c\u4f60\u4eca\u5929\u597d\u5417\uff1f",
)

col1, col2 = st.columns([1, 1])
generate_clicked = col1.button("\U0001f399\ufe0f Generate Speech", type="primary", use_container_width=True)
clear_clicked = col2.button("Clear", use_container_width=True)

if clear_clicked:
    st.rerun()

if generate_clicked:
    if not text_input.strip():
        st.warning("Please enter some text first.")
    else:
        # Step 1: language detection
        if auto_detect:
            detection = detect_language(text_input)
            lang_code = detection["language_code"]
            st.info(
                f"Detected language: **{detection['language_name']}** "
                f"({lang_code}) — confidence {detection['confidence']:.0%} "
                f"[{detection['method']}]"
            )
            if not detection["supported"]:
                st.warning(
                    f"Detected language '{lang_code}' isn't in the supported set. "
                    f"Falling back to your manual selection: {SUPPORTED_LANGUAGES[manual_lang]}."
                )
                lang_code = manual_lang
        else:
            lang_code = manual_lang
            st.info(f"Using manually selected language: **{SUPPORTED_LANGUAGES[lang_code]}**")

        # Step 2: optional translation (any supported language -> any supported language)
        text_to_speak = text_input
        speak_lang_code = lang_code

        if translate_enabled and translate_target:
            if translate_target == lang_code:
                st.info(
                    f"Source and target language are both "
                    f"{SUPPORTED_LANGUAGES[lang_code]} — speaking the original text."
                )
            else:
                try:
                    with st.spinner("Translating..."):
                        translation = translate_text(text_input, lang_code, translate_target)
                    text_to_speak = translation.translated_text
                    speak_lang_code = translation.target_lang
                    st.write(
                        f"**Original ({SUPPORTED_LANGUAGES[translation.source_lang]}):** "
                        f"{translation.original_text}"
                    )
                    st.write(
                        f"**Translated ({SUPPORTED_LANGUAGES[translation.target_lang]}):** "
                        f"{translation.translated_text}"
                    )
                except TranslationError as e:
                    st.error(f"Translation failed, speaking original text instead: {e}")

        # Step 3: synthesis
        try:
            with st.spinner("Synthesizing speech..."):
                result = synthesize(text_to_speak, speak_lang_code, slow=slow_speech)
            duration = estimate_duration_seconds(result.audio_bytes)

            st.success("Speech generated.")
            st.audio(result.audio_bytes, format="audio/mp3")

            meta_cols = st.columns(3)
            meta_cols[0].metric("Engine", result.engine)
            meta_cols[1].metric("Characters", result.char_count)
            meta_cols[2].metric("Duration (s)", duration if duration >= 0 else "n/a")

            st.download_button(
                "\u2b07\ufe0f Download MP3",
                data=result.audio_bytes,
                file_name=f"tts_{speak_lang_code}.mp3",
                mime="audio/mp3",
            )
        except UnsupportedLanguageError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Something went wrong during synthesis: {e}")

st.markdown("---")
st.caption("BIT 4543 Artificial Intelligence — Group Project 3: Multilingual AI Text-to-Speech Assistant")
