from langchain_groq import ChatGroq
from vector_db import search
import os
from dotenv import load_dotenv

load_dotenv()

LLM = os.getenv("LLM_MODEL")

llm = ChatGroq(model=LLM)

def generate_answer(query, video_id):
    try:
        context_chunks = search(query, video_id)
        
        if not context_chunks:
            return "Please upload a video first."
        
        context = "\n\n".join(context_chunks)

        prompt = f"""
        You are an AI assistant.

        Answer the question based ONLY on the context below.

        Context:
        {context}

        Question:
        {query}

        Answer:
        """

        response = llm.invoke(prompt)

        return response.content
    except Exception as e:
        return "Sorry, I couldn't generate an answer at this time."