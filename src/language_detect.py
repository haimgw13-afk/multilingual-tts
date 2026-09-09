"""
language_detect.py
-------------------
Automatic language detection for the Multilingual AI Text-to-Speech Assistant.

Uses `langdetect` (a Python port of Google's language-detection library) as the
primary detector, with a lightweight Unicode-script heuristic as a fallback for
very short strings where statistical detection is unreliable.
"""

from langdetect import detect_langs, DetectorFactory, LangDetectException

# Make detection deterministic across runs (langdetect is otherwise randomized).
DetectorFactory.seed = 0

# Languages supported by this prototype, mapped to human-readable names and
# to the language codes expected by the TTS engine layer.
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "de": "German",
    "zh-cn": "Mandarin Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}

# Unicode-range fallback heuristics for short text where statistical
# detection is unreliable (e.g. single words, greetings).
def _script_heuristic(text: str) -> str | None:
    for ch in text:
        code = ord(ch)
        if 0x3040 <= code <= 0x30FF:  # Hiragana / Katakana
            return "ja"
        if 0xAC00 <= code <= 0xD7A3:  # Hangul syllables
            return "ko"
        if 0x4E00 <= code <= 0x9FFF:  # CJK unified ideographs (Chinese, or Kanji)
            return "zh-cn"
    return None


def detect_language(text: str, min_confidence: float = 0.5) -> dict:
    """
    Detect the language of `text`.

    Returns a dict:
        {
          "language_code": str,   # e.g. "en", "es", "zh-cn"
          "language_name": str,   # e.g. "English"
          "confidence": float,    # 0-1
          "supported": bool,      # whether it's one of SUPPORTED_LANGUAGES
          "method": str,          # "statistical" or "heuristic" or "fallback"
        }
    """
    text = (text or "").strip()
    if not text:
        return {
            "language_code": "en", "language_name": "English",
            "confidence": 0.0, "supported": True, "method": "fallback",
        }

    # Very short input: prefer script heuristic, which is more reliable than
    # statistical n-gram detection on a handful of characters.
    if len(text) < 8:
        heuristic = _script_heuristic(text)
        if heuristic:
            return {
                "language_code": heuristic,
                "language_name": SUPPORTED_LANGUAGES.get(heuristic, heuristic),
                "confidence": 0.75,
                "supported": heuristic in SUPPORTED_LANGUAGES,
                "method": "heuristic",
            }

    try:
        candidates = detect_langs(text)
        top = candidates[0]
        code = top.lang
        # langdetect returns "zh-cn"/"zh-tw" for Chinese already.
        return {
            "language_code": code,
            "language_name": SUPPORTED_LANGUAGES.get(code, code),
            "confidence": round(top.prob, 3),
            "supported": code in SUPPORTED_LANGUAGES,
            "method": "statistical",
        }
    except LangDetectException:
        heuristic = _script_heuristic(text)
        code = heuristic or "en"
        return {
            "language_code": code,
            "language_name": SUPPORTED_LANGUAGES.get(code, code),
            "confidence": 0.3,
            "supported": code in SUPPORTED_LANGUAGES,
            "method": "fallback",
        }


if __name__ == "__main__":
    samples = [
        "Hello, how are you today?",
        "Hola, ¿cómo estás?",
        "Guten Tag, wie geht es Ihnen?",
        "こんにちは、お元気ですか？",
        "안녕하세요, 어떻게 지내세요?",
        "你好，你今天好吗？",
    ]
    for s in samples:
        print(s, "->", detect_language(s))
