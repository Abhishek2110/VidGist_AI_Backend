from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

LLM = os.getenv("LLM_MODEL")

llm = ChatGroq(model=LLM)


def generate_llm_response(prompt: str):
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return "Sorry, I couldn't generate an answer at this time."