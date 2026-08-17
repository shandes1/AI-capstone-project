# Import Required Libraries
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


# Load the Pretrained BLIP Processor and Model
def load_caption_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    model = model.to(device)
    return processor, model


# Generate a Caption from an Image
def generate_caption(image, processor, model):
    image = image.convert('RGB')
    inputs = processor(image, return_tensors="pt").to(device)

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=60)

    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption


# test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python caption.py <path_to_image>")
        sys.exit(1)

    img_path = sys.argv[1]
    processor, model = load_caption_model()

    image = Image.open(img_path)
    caption = generate_caption(image, processor, model)
    print("Caption:", caption)
