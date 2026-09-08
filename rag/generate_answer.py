import requests
from rag.search import semantic_search
from rag.rerank import rerank


OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"


def build_prompt(question: str, chunks: list) -> str:
    context = "\n\n".join(
        f"[{i}] {c.content}" for i, c in enumerate(chunks)
    )

    return f"""Context passages:
{context}

Question: {question}

Step 1: List the numbers of any passages above that contain information
relevant to answering the question. If none are relevant, write "none".

Step 2: Using ONLY the information in the relevant passages you listed
(combining them if needed), write a final answer. Do not use any outside
knowledge, even if you know it to be true. If you listed "none" in Step 1,
your final answer must be: "I don't have enough information in the provided
documents to answer that."

Format your response as:
Relevant passages: [your list]
Answer: [your answer]"""

def generate_answer(question: str, retrieve_k: int = 15, final_k: int = 5):
    candidates = semantic_search(question, top_k=retrieve_k)
    chunks = rerank(question, candidates, top_n=final_k)

    print("DEBUG - Chunks after reranking:")
    for c in chunks:
        print(f"chunk #{c.chunk_index}: {c.content[:80]}")

    prompt = build_prompt(question, chunks)

    try:
        response = requests.post(OLLAMA_GENERATE_URL, json={"model": LLM_MODEL, "prompt": prompt, "stream": False}, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"I don't have enough information in the provided documents to answer that. (Service temporarily unavailable: {e})", chunks

    raw_output = response.json()["response"]
    if "Answer:" in raw_output:
        clean_answer = raw_output.split("Answer:", 1)[1].strip()
    else:
        clean_answer = raw_output.strip()

    return clean_answer, chunks

if __name__ == "__main__":
    question = "A bank's independent testing confirms that its written BSA/AML policies are comprehensive, but transaction testing reveals that employees routinely fail to follow those policies. How should an examiner interpret this situation?"
    answer, sources = generate_answer(question)

    print(f"Question: {question}\n")
    print(f"Answer:\n{answer}\n")
    print("Sources used:")
    for c in sources:
        print(f"  - {c.source_document}, chunk #{c.chunk_index}")
