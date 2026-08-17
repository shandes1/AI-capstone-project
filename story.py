#  Import Required Libraries
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

story_model_name = "Qwen/Qwen2.5-1.5B-Instruct"


GENRES = {
    "Fantasy": "Fantasy",
    "Children's": "Children's",
    "Mystery": "Mystery",
    "Emotional": "Emotional",
    "Adventure": "Adventure",
    "Cinematic": "Cinematic",
    "Comedy": "Comedy",
    "Horror": "Horror",
}

DEFAULT_GENRE = "Fantasy"


def build_story_system_prompt(genre=DEFAULT_GENRE):
    return (
        f"You are a creative {genre} short story writer. "
        "You will receive a description of an image. Transform the scene into "
        f"an engaging {genre} story. "
        "Keep the same characters, objects, and setting described in the image. "
        "Do not contradict important visual details. You may creatively add "
        "emotions, dialogue, events, atmosphere, or backstory when appropriate "
        "for the genre. "
        "Keep the story between 4 and 5 sentences. "
        "Output only the story text without a title or explanation."
    )

#  Load the Story Generation Model
def load_story_model():
    tokenizer = AutoTokenizer.from_pretrained(story_model_name)
    model = AutoModelForCausalLM.from_pretrained(story_model_name)
    model = model.to(device)
    return tokenizer, model


#  Generate a Story from a Caption
def generate_story(caption, tokenizer, model, genre=DEFAULT_GENRE):
    system_prompt = build_story_system_prompt(genre)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Scene: " + caption + ". Write a story about exactly this scene."},
    ]

    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_ids = output[0][inputs["input_ids"].shape[1]:]
    story = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return story


# test
if __name__ == "__main__":
    import sys

    caption = " ".join(sys.argv[1:])
    if caption == "":
        caption = "a dog running on a beach"

    genre = DEFAULT_GENRE

    tokenizer, model = load_story_model()

    print("Caption:", caption)
    print("Genre:", genre)
    story = generate_story(caption, tokenizer, model, genre=genre)
    print("Story:", story)
