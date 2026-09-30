import requests

from rag.llm_client import generate_text



def rewrite_query(question: str) -> str:
    """Rewrites a user's question into clearer, retrieval-friendly phrasing."""
    prompt = f"""Rewrite the question below to be clearer and use standard
BSA/AML compliance terminology, without changing its meaning or adding new
requirements. If it's already clear, return it unchanged. Return ONLY the
rewritten question, nothing else.

Question: {question}

Rewritten:"""

    try:
        rewritten = generate_text(prompt, temperature=0.0).strip()
        return rewritten if rewritten else question
    except Exception as e:
        return question
