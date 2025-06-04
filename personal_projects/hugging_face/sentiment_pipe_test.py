from transformers import pipeline

classifier = pipeline (
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    framework="pt" 
)


res = classifier("I've been waiting for a HuggingFace course my whole life")

print(res)

