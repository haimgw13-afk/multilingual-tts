"""
tts_engine.py
-------------
Text-to-speech synthesis layer for the Multilingual AI Text-to-Speech Assistant.

Primary engine: gTTS (Google Translate TTS interface) - free, requires internet,
covers all languages in this prototype's scope.

The engine is wrapped behind a small interface (`synthesize`) so that a second
engine (e.g. Coqui TTS for offline synthesis, or a commercial cloud API) can be
swapped in later without changing the application layer. This mirrors the
"evaluate 2-3 engines" step planned for Week 2 in the project proposal.
"""

import io
from dataclasses import dataclass
from gtts import gTTS

# gTTS language codes for our supported set. gTTS uses "zh-CN" (capitalised)
# for Mandarin, and does not need special handling for the others.
GTTS_LANG_MAP = {
    "en": "en",
    "es": "es",
    "de": "de",
    "zh-cn": "zh-CN",
    "ja": "ja",
    "ko": "ko",
}


@dataclass
class SynthesisResult:
    audio_bytes: bytes
    language_code: str
    engine: str
    char_count: int


class UnsupportedLanguageError(Exception):
    pass


def synthesize(text: str, language_code: str, slow: bool = False) -> SynthesisResult:
    """
    Convert `text` into speech audio (MP3 bytes) for the given language code.

    Raises UnsupportedLanguageError if the language isn't in GTTS_LANG_MAP.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("No text provided for synthesis.")

    gtts_code = GTTS_LANG_MAP.get(language_code)
    if not gtts_code:
        raise UnsupportedLanguageError(
            f"Language '{language_code}' is not supported by the TTS engine."
        )

    tts = gTTS(text=text, lang=gtts_code, slow=slow)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)

    return SynthesisResult(
        audio_bytes=buf.read(),
        language_code=language_code,
        engine="gTTS",
        char_count=len(text),
    )


if __name__ == "__main__":
    result = synthesize("Hello, this is a test of the text to speech engine.", "en")
    with open("/tmp/test_output.mp3", "wb") as f:
        f.write(result.audio_bytes)
    print(f"Synthesized {result.char_count} chars via {result.engine} -> /tmp/test_output.mp3")
