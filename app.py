# Import Required Libraries
import streamlit as st
from PIL import Image

from caption import load_caption_model, generate_caption
from story import load_story_model, generate_story, GENRES, DEFAULT_GENRE
from translate_tts import translate_to_nepali, narrate_nepali

st.set_page_config(page_title="Image-to-Nepali-Story", page_icon="📖")


# Load the Models (cached so they only load once)
@st.cache_resource
def get_caption_model():
    return load_caption_model()


@st.cache_resource
def get_story_model():
    return load_story_model()


# Build the Streamlit App
st.title("Image-to-Nepali-Story Generator")
st.write("Upload an image to generate an English caption, a short story, its Nepali translation, and narration.")

caption_processor, caption_model = get_caption_model()
story_tokenizer, story_model = get_story_model()

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("Or capture from camera")

image_file = uploaded_file or camera_file

if image_file:
    image = Image.open(image_file).convert("RGB")
    st.image(image, caption="Selected Image", use_container_width=True)

    # Caption
    st.subheader("1. Caption (English)")
    caption_key = "caption_" + str(hash(image.tobytes()))

    if caption_key not in st.session_state:
        with st.spinner("Generating caption..."):
            st.session_state[caption_key] = generate_caption(image, caption_processor, caption_model)
    caption = st.session_state[caption_key]
    st.write(caption)

    # Story
    st.subheader("2. Generated Story (English)")

    genre_labels = list(GENRES.values())
    default_index = list(GENRES.keys()).index(DEFAULT_GENRE)
    selected_label = st.radio("Genre", genre_labels, index=default_index, horizontal=True)
    # Map the emoji-labeled display string back to the clean genre name used in the prompt
    genre = next(g for g, label in GENRES.items() if label == selected_label)

    regenerate = st.button("Regenerate story")
    story_key = "story_" + str(hash((caption, genre)))

    if story_key not in st.session_state or regenerate:
        with st.spinner(f"Writing {genre.lower()} story..."):
            st.session_state[story_key] = generate_story(caption, story_tokenizer, story_model, genre=genre)
    story = st.session_state[story_key]
    st.write(story)

    # Translation 
    st.subheader("3. Nepali Translation")
    translation_key = "translation_" + str(hash(story))

    if translation_key not in st.session_state:
        with st.spinner("Translating to Nepali..."):
            try:
                st.session_state[translation_key] = translate_to_nepali(story)
            except Exception as e:
                st.error(f"Translation failed: {e}")
                st.stop()
    nepali_story = st.session_state[translation_key]
    st.write(nepali_story)

    # Narration
    st.subheader("4. Nepali Narration")

    engine_choice = st.radio("TTS Engine", ["Edge TTS (Edge)", "gTTS (Google)"], horizontal=True)

    if engine_choice == "Edge TTS (Edge)":
        voice_choice = st.radio("Voice", ["Female (Hemkala)", "Male (Sagar)"], horizontal=True)
        if voice_choice == "Female (Hemkala)":
            selected_voice = "ne-NP-HemkalaNeural"
        else:
            selected_voice = "ne-NP-SagarNeural"
        audio_key = "audio_edge_" + selected_voice + "_" + str(hash(nepali_story))
        engine, voice = "edge", selected_voice
    else:
        audio_key = "audio_gtts_" + str(hash(nepali_story))
        engine, voice = "gtts", None

    if audio_key not in st.session_state:
        with st.spinner("Generating narration..."):
            try:
                if engine == "gtts":
                    st.session_state[audio_key] = narrate_nepali(nepali_story, engine="gtts")
                else:
                    st.session_state[audio_key] = narrate_nepali(nepali_story, engine="edge", voice=voice)
            except Exception as e:
                st.error(f"Narration failed: {e}")
                st.stop()

    st.audio(st.session_state[audio_key], format="audio/mp3")

else:
    st.info("Upload an image or capture one from your camera to begin.")
