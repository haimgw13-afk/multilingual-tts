"""
test_pipeline.py
-----------------
Basic unit tests for the language detection, TTS synthesis, and translation
modules.

Run with:
    pytest tests/
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from language_detect import detect_language, SUPPORTED_LANGUAGES
from tts_engine import synthesize, UnsupportedLanguageError
from translator import translate_text, TranslationError


LANGUAGE_SAMPLES = {
    "en": "Hello, how are you doing today? I hope you are having a great day.",
    "es": "Hola, ¿cómo estás? Espero que tengas un buen día.",
    "de": "Guten Tag, wie geht es Ihnen heute?",
    "ja": "こんにちは、お元気ですか？今日はいい天気ですね。",
    "ko": "안녕하세요, 오늘 기분이 어떠세요?",
    "zh-cn": "你好，你今天好吗？希望你今天过得愉快。",
}


@pytest.mark.parametrize("expected_code,text", list(LANGUAGE_SAMPLES.items()))
def test_language_detection(expected_code, text):
    result = detect_language(text)
    assert result["language_code"] == expected_code, (
        f"Expected {expected_code}, got {result['language_code']} for: {text}"
    )
    assert result["supported"] is True


def test_empty_text_defaults_gracefully():
    result = detect_language("")
    assert result["language_code"] == "en"
    assert result["confidence"] == 0.0


def test_synthesis_produces_audio_bytes():
    result = synthesize("Hello world, this is a unit test.", "en")
    assert result.audio_bytes is not None
    assert len(result.audio_bytes) > 1000  # a real MP3, not an empty stub
    assert result.engine == "gTTS"


def test_synthesis_rejects_unsupported_language():
    with pytest.raises(UnsupportedLanguageError):
        synthesize("Bonjour", "fr")  # French not in current supported set


def test_synthesis_rejects_empty_text():
    with pytest.raises(ValueError):
        synthesize("   ", "en")


# --- Translation tests (require internet, same as the synthesis tests above) ---

# One sample pair per supported language, translated into a different
# supported language, to confirm translation works across the whole set -
# not just a single hardcoded language pair.
TRANSLATION_PAIRS = [
    ("Hola, ¿cómo estás?", "es", "en"),
    ("Good morning", "en", "es"),
    ("Guten Tag, wie geht es Ihnen?", "de", "en"),
    ("你好，你今天好吗？", "zh-cn", "ja"),
    ("こんにちは、お元気ですか？", "ja", "ko"),
    ("안녕하세요, 어떻게 지내세요?", "ko", "de"),
]


@pytest.mark.parametrize("text,source_lang,target_lang", TRANSLATION_PAIRS)
def test_translate_text_across_supported_languages(text, source_lang, target_lang):
    result = translate_text(text, source_lang, target_lang)
    assert result.source_lang == source_lang
    assert result.target_lang == target_lang
    assert len(result.translated_text.strip()) > 0
    # Translated text shouldn't just be the original text unchanged.
    assert result.translated_text != result.original_text


def test_translate_text_rejects_empty_text():
    with pytest.raises(TranslationError):
        translate_text("   ", "es", "en")


def test_translate_text_rejects_same_source_and_target():
    with pytest.raises(TranslationError):
        translate_text("Hello", "en", "en")
