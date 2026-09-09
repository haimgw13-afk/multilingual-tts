# Multilingual AI Text-to-Speech Assistant

BIT 4543 Artificial Intelligence â€” Group Project 3 (Speech AI)

A web application that automatically detects the language of user-submitted
text and converts it into natural-sounding speech, with downloadable audio
output. Built as a course prototype.

## Features

- **Automatic language detection** across 6 languages (English, Spanish,
  German, Mandarin Chinese, Japanese, Korean), using statistical detection
  (`langdetect`) with a Unicode-script fallback for short text.
- **Speech synthesis** via gTTS, with the engine layer abstracted so
  alternative engines (Coqui TTS, cloud APIs) can be swapped in.
- **Translation between any two supported languages** (`src/translator.py`,
  via `deep-translator`/Google Translate) â€” pick a "translate to" language
  in the sidebar and the detected/selected text is translated before being
  spoken, e.g. Spanish text spoken aloud in Japanese, or Korean text spoken
  aloud in German.
- **Manual language override** for cases where auto-detection is uncertain.
- **Downloadable MP3 output** plus duration/character-count metadata.

## Project Structure

```
project-name/
â”œâ”€â”€ data/           # sample multilingual text & test sentences
â”œâ”€â”€ notebooks/      # experimentation (TTS engine comparison, language-ID tests)
â”œâ”€â”€ src/            # core modules: language_detect.py, tts_engine.py, audio_utils.py
â”œâ”€â”€ app/            # Streamlit application (app.py)
â”œâ”€â”€ models/         # cached/downloaded model artifacts (if applicable)
â”œâ”€â”€ docs/           # proposal, progress report, final report
â”œâ”€â”€ results/        # evaluation outputs, MOS scores, latency logs
â”œâ”€â”€ tests/          # unit tests for detection & synthesis modules
â”œâ”€â”€ README.md
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ LICENSE
â””â”€â”€ .gitignore
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`pydub` (used for duration estimation / WAV export) requires `ffmpeg` to be
installed and on your PATH.

## Run the app

```bash
streamlit run app/app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Run the tests

```bash
pytest tests/
```

## How it works

1. **Input** â€” user types or pastes text into the app.
2. **Language detection** (`src/language_detect.py`) â€” identifies the
   language automatically, or the user can select one manually.
3. **Translation** (`src/translator.py`, optional) â€” if enabled, the text is
   translated from the detected/selected language into whichever supported
   language the user picks as the "translate to" target.
4. **Speech synthesis** (`src/tts_engine.py`) â€” the resulting text and
   language (translated, or original if translation is off) are sent to the
   TTS engine (gTTS), which returns audio.
5. **Output** (`src/audio_utils.py` + `app/app.py`) â€” the audio is played
   back in-browser and offered as a downloadable MP3.

## Supported languages (current scope)

| Code  | Language          |
|-------|-------------------|
| en    | English           |
| es    | Spanish           |
| de    | German            |
| zh-cn | Mandarin Chinese  |
| ja    | Japanese          |
| ko    | Korean            |

## Roadmap (see Project Proposal for full timeline)

- Week 2: benchmark gTTS vs. Coqui TTS vs. a cloud API for voice quality.
- Week 3: polish UI, add voice-speed/pitch controls, error handling.
- Week 4: user testing, latency/quality evaluation, final report + slides.

## Team

BIT 4543 Artificial Intelligence â€” Group Project, Project 3.
