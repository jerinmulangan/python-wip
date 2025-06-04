import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda


load_dotenv()
api_key = os.getenv("APIKEY")

client = InferenceClient(model="nlptown/bert-base-multilingual-uncased-sentiment", token=api_key)

prompt = PromptTemplate(
    input_variables=["question"],
    template="Please analyze the sentiment of the following statement: {question}"
)


def hf_infer(prompt_text):
    plain_text = str(prompt_text)
    result = client.text_classification(plain_text)
    return result[0]["label"] + " (score: {:.2f})".format(result[0]["score"])

llm = RunnableLambda(lambda x: hf_infer(x))

qa_chain = prompt | llm

if __name__ == "__main__":
    question = {"question": "I hate the new update, it is the worst, the new UI is so ugly it hurts my eyes"}
    answer = qa_chain.invoke(question)
    print("Answer:\n", answer)
