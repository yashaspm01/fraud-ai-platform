import requests
from rag.search import semantic_search

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"


def build_prompt(question: str, chunks: list) -> str:
    context = "\n\n".join(
        f"[Source: {c.source_document}, chunk #{c.chunk_index}]\n{c.content}"
        for c in chunks
    )

    return f"""Answer the question using ONLY the context below. If the context
does not contain enough information to answer, say "I don't have enough
information in the provided documents to answer that."

Context:
{context}

Question: {question}

Answer:"""


def generate_answer(question: str, top_k: int = 5) -> str:
    chunks = semantic_search(question, top_k=top_k)
    prompt = build_prompt(question, chunks)

    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
    )
    response.raise_for_status()
    return response.json()["response"], chunks


if __name__ == "__main__":
    question = "What is required of a BSA compliance officer?"

    answer, sources = generate_answer(question)

    print(f"Question: {question}\n")
    print(f"Answer:\n{answer}\n")
    print("Sources used:")
    for c in sources:
        print(f"  - {c.source_document}, chunk #{c.chunk_index}")
