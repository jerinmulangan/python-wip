import os
from dotenv import load_dotenv
from PIL import Image
from transformers import pipeline, AutoProcessor, AutoModelForImageTextToText, AutoTokenizer

load_dotenv()

processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/blip-image-captioning-large")
model = AutoModelForImageTextToText.from_pretrained("Salesforce/blip-image-captioning-large")

captioner = pipeline("image-to-text", model=model, image_processor=processor, tokenizer=tokenizer)

if __name__ == "__main__":
    image_path = "sample.jpg"
    if not os.path.exists(image_path):
        print("Image file not found:", image_path)
    else:
        image = Image.open(image_path)
        caption = captioner(image)[0]['generated_text']
        print("Generated Caption:\n", caption)