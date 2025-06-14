import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import torch
from transformers import pipeline, AutoProcessor, AutoModelForImageTextToText, AutoTokenizer, T5ForConditionalGeneration

load_dotenv()

processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
tokenizer = AutoTokenizer.from_pretrained("Salesforce/blip-image-captioning-large")
model = AutoModelForImageTextToText.from_pretrained("Salesforce/blip-image-captioning-large")
captioner = pipeline("image-to-text", model=model, image_processor=processor, tokenizer=tokenizer)

device = 0 if torch.cuda.is_available() else -1
summarizer = pipeline("summarization", model="t5-large", tokenizer="t5-large", device=device)

from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer

login(token=os.getenv("APIKEY"))

qa_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", use_auth_token=True)
qa_model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", use_auth_token=True)

st.set_page_config(page_title="GenAI Image Captioner & Summarizer", layout="centered")
st.title("GenAI Image Captioning, Summarization, and Q&A")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with st.spinner("Generating caption..."):
        caption = captioner(image)[0]['generated_text']
        st.success("Caption Generated")
        st.write("**Caption:**", caption)

    with st.spinner("Summarizing caption..."):
        input_text = "summarize: " + caption
        summary = summarizer(input_text, max_length=80, min_length=25, do_sample=False)[0]['summary_text']
        st.success("Summary Ready")
        st.write("**Summary:**", summary)

    st.markdown("---")
    st.subheader("Ask a question about the image")
    user_question = st.text_input("Enter your question:")

    if user_question:
        prompt = f"You are a helpful assistant. Based on the image caption and summary, answer the user's question.\n\nCaption: {caption}\nSummary: {summary}\nQuestion: {user_question}\nAnswer:"
        inputs = qa_tokenizer(prompt, return_tensors="pt")
        outputs = qa_model.generate(**inputs, max_new_tokens=200, pad_token_id=qa_tokenizer.eos_token_id)
        response = qa_tokenizer.decode(outputs[0], skip_special_tokens=True).split("Answer:")[-1].strip()
        st.write("**Answer:**", response)
else:
    st.info("Please upload an image to begin.")
