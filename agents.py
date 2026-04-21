from vector_db import search
from rag_pipeline import generate_llm_response

def multi_agent_pipeline(query, video_id):
    
    # Step 1: understand query
    intent = query_agent(query)
    
    # Step 2: retrieve context
    chunks = retriever_agent(query, video_id)

    if not chunks:
        return "No relevant content found in this video."

    # Step 3: generate answer
    final_answer = answer_agent(query, chunks, intent)

    return final_answer


# Agents

# Query Analyzer Agent
def query_agent(query: str):
    query = query.lower()

    if "summary" in query or "about" in query:
        return "summary"
    elif "explain" in query or "how" in query:
        return "explanation"
    else:
        return "general"
    
# Retriever Agent
def retriever_agent(query, video_id):
    results = search(query, video_id)

    if not results:
        return []

    return results

# Answer Generation Agent
def answer_agent(query, context_chunks, intent):
    context = "\n\n".join(context_chunks)

    if intent == "summary":
        prompt = f"""
        Summarize the following video content clearly:

        {context}
        """

    elif intent == "explanation":
        prompt = f"""
        Explain the following content in detail:

        {context}
        """

    else:
        prompt = f"""
        Answer the question based ONLY on the context below.

        Context:
        {context}

        Question:
        {query}

        Answer:
        """

    return generate_llm_response(prompt)