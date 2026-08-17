# Image-to-Nepali-Story Generator

Upload an image → get an English caption → a short genre story → Nepali translation → Nepali audio narration.

## Pipeline

1. **Caption** (`caption.py`) — BLIP (`Salesforce/blip-image-captioning-large`) generates an English caption from the image.
2. **Story** (`story.py`) — Qwen2.5-1.5B-Instruct expands the caption into a short story (4–5 sentences) in a chosen genre.
3. **Translate** (`translate_tts.py`) — Google Translate (via `deep_translator`) converts the story to Nepali.
4. **Narrate** (`translate_tts.py`) — Nepali text is converted to speech using either `edge-tts` (neural voices) or `gTTS`.
5. **App** (`app.py`) — Streamlit UI that wires all four stages together.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit app (main entry point) |
| `caption.py` | Image → English caption (BLIP) |
| `story.py` | Caption → English story (Qwen2.5-1.5B-Instruct, 8 genres) |
| `translate_tts.py` | Story → Nepali text → Nepali audio (gTTS / edge-tts) |

## Requirements

- Python 3.10–3.12 (avoid 3.13 — `audioop` removal breaks `pydub`/edge-tts deps)
- GPU recommended (CUDA) for BLIP + Qwen, but falls back to CPU

```bash
pip install streamlit torch torchvision transformers pillow deep-translator gtts edge-tts
```

## Usage

Run the app:

```bash
streamlit run app.py
```

Then in the browser:
1. Upload an image or take a photo.
2. Pick a genre (Fantasy, Children's, Mystery, Emotional, Adventure, Cinematic, Comedy, Horror).
3. Click "Regenerate story" to reroll with the same genre/caption if needed.
4. Choose a TTS engine (Edge TTS or gTTS) and voice.
5. Read/listen to the Nepali story.

### Standalone testing

Each stage can be run on its own from the command line:

```bash
python caption.py path/to/image.jpg
python story.py "a dog running on a beach"
python translate_tts.py "Once upon a time, a dog ran on the beach."
```
