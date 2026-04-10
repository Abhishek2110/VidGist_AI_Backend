from langchain_groq import ChatGroq
from vector_db import search

llm = ChatGroq(model="openai/gpt-oss-120b")

def generate_answer(query):
    context_chunks = search(query)
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