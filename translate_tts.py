# Step 1: Import Required Libraries
import asyncio
from io import BytesIO
from deep_translator import GoogleTranslator
from gtts import gTTS
import edge_tts

# Nepali neural voices edge-tts:
edge_voice_female = "ne-NP-HemkalaNeural"
edge_voice_male = "ne-NP-SagarNeural"


# Translate English Text to Nepali
def translate_to_nepali(text):
    translator = GoogleTranslator(source='en', target='ne')
    nepali_text = translator.translate(text)
    return nepali_text


# Convert Nepali Text to Speech using gTTS
def narrate_nepali_gtts(nepali_text):
    tts = gTTS(text=nepali_text, lang='ne')
    mp3_bytes = BytesIO()
    tts.write_to_fp(mp3_bytes)
    mp3_bytes.seek(0)
    return mp3_bytes.read()


# Convert Nepali Text to Speech using edge-tts
async def generate_edge_speech(nepali_text, voice):
    communicate = edge_tts.Communicate(nepali_text, voice)
    audio_buffer = BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    audio_buffer.seek(0)
    return audio_buffer.read()


def narrate_nepali_edge(nepali_text, voice=edge_voice_female):
    audio_bytes = asyncio.run(generate_edge_speech(nepali_text, voice))
    return audio_bytes


# Single entry point the app calls, dispatches to the chosen engine
def narrate_nepali(nepali_text, engine="edge", voice=edge_voice_female):
    if engine == "gtts":
        return narrate_nepali_gtts(nepali_text)
    else:
        return narrate_nepali_edge(nepali_text, voice)


# test
if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:])
    if text == "":
        text = "Once upon a time, a curious dog ran along the beach. It chased the waves and barked at the seagulls."

    print("English:", text)
    nepali_text = translate_to_nepali(text)
    print("Nepali:", nepali_text)

    print("\nTesting gTTS...")
    gtts_audio = narrate_nepali_gtts(nepali_text)
    print("gTTS audio size (bytes):", len(gtts_audio))
    with open("test_output_gtts.mp3", "wb") as f:
        f.write(gtts_audio)
    print("Saved test_output_gtts.mp3")

    print("\nTesting edge-tts...")
    edge_audio = narrate_nepali_edge(nepali_text)
    print("edge-tts audio size (bytes):", len(edge_audio))
    with open("test_output_edge.mp3", "wb") as f:
        f.write(edge_audio)
    print("Saved test_output_edge.mp3")
