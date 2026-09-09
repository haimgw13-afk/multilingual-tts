"""
translator.py
-------------
Text translation layer for the Multilingual AI Text-to-Speech Assistant.

Uses `deep-translator`'s GoogleTranslator backend - free, no API key required
(it talks to the public Google Translate web frontend, the same approach gTTS
uses for synthesis). Kept behind a small interface (`translate_text`) so a
different backend (e.g. a paid cloud translation API) can be swapped in later
without changing the application layer.

Translation is supported between any two of this app's six supported
languages (English, Spanish, German, Mandarin Chinese, Japanese, Korean) -
not just a single fixed pair. The caller picks a source and a target
language (e.g. from the detected language and a "translate to" dropdown).
"""

from dataclasses import dataclass
from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, RequestError


# Language codes deep-translator expects match our SUPPORTED_LANGUAGES codes,
# except Mandarin: deep-translator wants "zh-CN" (capitalised), not "zh-cn".
DEEP_TRANSLATOR_LANG_MAP = {
    "en": "en",
    "es": "es",
    "de": "de",
    "zh-cn": "zh-CN",
    "ja": "ja",
    "ko": "ko",
}


@dataclass
class TranslationResult:
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    engine: str


class TranslationError(Exception):
    pass


def translate_text(text: str, source_lang: str, target_lang: str) -> TranslationResult:
    """
    Translate `text` from `source_lang` to `target_lang` (both using this
    project's language codes, e.g. "en", "es", "de", "zh-cn", "ja", "ko").

    Works between any two of the app's supported languages - not limited to
    a single fixed pair.

    Raises TranslationError if the text is empty, a language code isn't
    supported by the translator backend, source and target are the same
    language, or the translation request fails (e.g. no internet connection).
    """
    text = (text or "").strip()
    if not text:
        raise TranslationError("No text provided for translation.")

    if source_lang == target_lang:
        raise TranslationError(
            f"Source and target language are both {source_lang!r} - nothing to translate."
        )

    src = DEEP_TRANSLATOR_LANG_MAP.get(source_lang)
    tgt = DEEP_TRANSLATOR_LANG_MAP.get(target_lang)
    if not src or not tgt:
        raise TranslationError(
            f"Unsupported language pair for translation: "
            f"{source_lang!r} -> {target_lang!r}."
        )

    try:
        translated = GoogleTranslator(source=src, target=tgt).translate(text)
    except (NotValidPayload, RequestError) as e:
        raise TranslationError(f"Translation failed: {e}") from e

    if not translated:
        raise TranslationError("Translation returned no text.")

    return TranslationResult(
        original_text=text,
        translated_text=translated,
        source_lang=source_lang,
        target_lang=target_lang,
        engine="GoogleTranslator (deep-translator)",
    )


if __name__ == "__main__":
    samples = [
        ("Hello, how are you today?", "en", "es"),
        ("Hola, ¿cómo estás?", "es", "ja"),
        ("Guten Tag, wie geht es Ihnen?", "de", "zh-cn"),
        ("你好，你今天好吗？", "zh-cn", "ko"),
        ("こんにちは、お元気ですか？", "ja", "en"),
        ("안녕하세요, 어떻게 지내세요?", "ko", "de"),
    ]
    for text, src, tgt in samples:
        result = translate_text(text, src, tgt)
        print(f"[{result.source_lang} -> {result.target_lang}] "
              f"{result.original_text!r} -> {result.translated_text!r}")
