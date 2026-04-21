from vector_db import search
from rag_pipeline import generate_llm_response
from utils import clean_text


def multi_agent_pipeline(query, video_id):

    # Step 1: understand query
    intent = query_agent(query)

    # Step 2: retrieve context
    chunks = retriever_agent(query, video_id)

    if not chunks:
        return "No relevant content found in this video."

    # Step 3: generate answer
    raw_answer = answer_agent(query, chunks, intent)

    # Step 4: clean output
    final_answer = clean_text(raw_answer)

    return final_answer

# -----------------------------
# 🧠 Query Analyzer Agent
# -----------------------------
def query_agent(query: str):
    query = query.lower()

    if "summary" in query or "about" in query:
        return "summary"
    elif "explain" in query or "how" in query:
        return "explanation"
    else:
        return "general"

# -----------------------------
# 📚 Retriever Agent
# -----------------------------
def retriever_agent(query, video_id):
    results = search(query, video_id)

    if not results:
        return []

    return results

# -----------------------------
# 🤖 Answer Generation Agent
# -----------------------------
def answer_agent(query, context_chunks, intent):
    context = "\n\n".join(context_chunks)

    if intent == "summary":
        prompt = f"""
            You are an AI assistant.

            Summarize the following video content clearly.

            IMPORTANT:
            - Do NOT use markdown formatting
            - Do NOT use **stars**, bullet points, or special characters
            - Do NOT use headings like "Summary"
            - Write in clean plain text
            - Use simple and clear sentences
            - Write in paragraph form

            Content:
            {context}
        """

    elif intent == "explanation":
        prompt = f"""
            You are an AI assistant.

            Explain the following content in detail.

            IMPORTANT:
            - Do NOT use markdown formatting
            - Do NOT use **stars**, bullet points, or special characters
            - Write in clean plain text
            - Use simple and clear sentences

            Content:
            {context}
        """

    else:
        prompt = f"""
            You are an AI assistant.

            Answer the question based ONLY on the context below.

            IMPORTANT:
            - Do NOT use markdown formatting
            - Do NOT use **stars**, bullet points, or special characters
            - Write in clean plain text
            - Use simple sentences

            Context:
            {context}

            Question:
            {query}
        """

    return generate_llm_response(prompt)