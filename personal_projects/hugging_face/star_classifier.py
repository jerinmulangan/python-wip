# End-to-End GenAI App using Hugging Face + LangChain

# Phase 1: Setup and Basic QA using Hugging Face Inference API + LangChain (Corrected with supported sentiment model)

# Step 1: Install Required Libraries
# pip install langchain-core huggingface_hub streamlit python-dotenv

import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# Step 2: Load API key from .env
load_dotenv()
api_key = os.getenv("APIKEY")

# Step 3: Set up Hugging Face Inference Client with a correct hosted model
client = InferenceClient(model="nlptown/bert-base-multilingual-uncased-sentiment", token=api_key)

# Step 4: Define a prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="Please analyze the sentiment of the following statement: {question}"
)

# Step 5: Define a simple LLM wrapper using RunnableLambda for sentiment analysis

def hf_infer(prompt_text):
    # Ensure prompt_text is treated as a plain string
    plain_text = str(prompt_text)
    result = client.text_classification(plain_text)
    return result[0]["label"] + " (score: {:.2f})".format(result[0]["score"])

llm = RunnableLambda(lambda x: hf_infer(x))

# Step 6: Create final runnable pipeline
qa_chain = prompt | llm

# Step 7: Run example
if __name__ == "__main__":
    question = {"question": "I hate the new update, it is the worst, the new UI is so ugly it hurts my eyes"}
    answer = qa_chain.invoke(question)
    print("Answer:\n", answer)
