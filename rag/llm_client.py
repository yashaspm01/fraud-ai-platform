import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_LLM_MODEL = "llama3.2"
OLLAMA_EMBED_MODEL = "nomic-embed-text"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_EMBED_MODEL = "embed-english-v3.0"


def _post(url: str, **kwargs):
    """POSTs and converts any network or HTTP failure into a RuntimeError that includes the response body."""
    try:
        response = requests.post(url, **kwargs)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request to {url} failed: {e}")
    if not response.ok:
        raise RuntimeError(f"{response.status_code} from {url}: {response.text[:300]}")
    return response


def generate_text(prompt: str, temperature: float = 0.3, timeout: int = 60) -> str:
    """Routes text generation to Ollama (local) or Groq (hosted), based on LLM_PROVIDER."""
    if LLM_PROVIDER == "groq":
        response = _post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            },
            timeout=timeout,
        )
        return response.json()["choices"][0]["message"]["content"]

    response = _post(
        OLLAMA_GENERATE_URL,
        json={"model": OLLAMA_LLM_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": temperature}},
        timeout=timeout,
    )
    return response.json()["response"]


def embed_text(text: str, input_type: str = "search_document", timeout: int = 30) -> list[float]:
    """Routes embedding to Ollama (local) or Cohere (hosted), based on EMBEDDING_PROVIDER."""
    if EMBEDDING_PROVIDER == "cohere":
        response = _post(
            "https://api.cohere.com/v1/embed",
            headers={"Authorization": f"Bearer {COHERE_API_KEY}"},
            json={"model": COHERE_EMBED_MODEL, "texts": [text], "input_type": input_type},
            timeout=timeout,
        )
        return response.json()["embeddings"][0]

    response = _post(
        OLLAMA_EMBED_URL,
        json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
        timeout=timeout,
    )
    return response.json()["embedding"]
