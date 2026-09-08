import json
import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"


def rerank(query: str, chunks: list, top_n: int = 5) -> list:
    """
    Takes a wider list of candidate chunks (e.g. top 15 from vector search),
    asks the LLM to judge relevance directly, and returns the best top_n.
    """
    candidates_text = "\n\n".join(
        f"[{i}] {c.content[:300]}" for i, c in enumerate(chunks)
    )

    prompt = f"""You are ranking document passages by relevance to a question.

Question: {query}

Passages:
{candidates_text}

Return ONLY a JSON array of passage numbers, ordered from MOST to LEAST
relevant to the question. Example format: [3, 0, 4, 1, 2]
Do not include any other text."""

    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
    )
    response.raise_for_status()
    raw_output = response.json()["response"].strip()

    try:
        ranked_indices = json.loads(raw_output)
    except json.JSONDecodeError:
        # If the LLM didn't return clean JSON, fall back to original order
        # rather than crashing — a real reliability pattern, not just a hack.
        print(f"⚠️ Reranker returned non-JSON output, falling back: {raw_output}")
        ranked_indices = list(range(len(chunks)))

    reranked_chunks = [chunks[i] for i in ranked_indices if i < len(chunks)]
    return reranked_chunks[:top_n]
