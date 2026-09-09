"""
audio_utils.py
--------------
Small helpers for saving and converting synthesized audio.
"""

import io
import os
from datetime import datetime


def save_audio(audio_bytes: bytes, out_dir: str, prefix: str = "tts", ext: str = "mp3") -> str:
    """Save audio bytes to disk with a timestamped filename. Returns the file path."""
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        f.write(audio_bytes)
    return path


def mp3_to_wav_bytes(mp3_bytes: bytes) -> bytes:
    """Convert MP3 bytes to WAV bytes using pydub (requires ffmpeg on PATH)."""
    from pydub import AudioSegment
    audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    out = io.BytesIO()
    audio.export(out, format="wav")
    return out.getvalue()


def estimate_duration_seconds(mp3_bytes: bytes) -> float:
    """Best-effort duration estimate (seconds) for an MP3 byte string."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        return round(len(audio) / 1000.0, 2)
    except Exception:
        return -1.0
