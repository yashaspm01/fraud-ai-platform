import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"


def rewrite_query(question: str) -> str:
    """Rewrites a user's question into clearer, retrieval-friendly phrasing."""
    prompt = f"""Rewrite the question below to be clearer and use standard
BSA/AML compliance terminology, without changing its meaning or adding new
requirements. If it's already clear, return it unchanged. Return ONLY the
rewritten question, nothing else.

Question: {question}

Rewritten:"""

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        rewritten = response.json()["response"].strip()
        return rewritten if rewritten else question
    except requests.exceptions.RequestException:
        return question
