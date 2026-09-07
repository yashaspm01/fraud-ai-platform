import requests
import numpy as np

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"


def get_embedding(text: str) -> np.ndarray:
    response = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": text})
    response.raise_for_status()
    return np.array(response.json()["embedding"])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


if __name__ == "__main__":
    sentences = {
        "a": "The account balance dropped to zero",
        "b": "Funds were completely withdrawn from the account",
        "c": "The weather was sunny today",
    }

    embeddings = {key: get_embedding(text) for key, text in sentences.items()}

    print("Similarity (a vs b) — should be HIGH (related meaning):")
    print(f"  {cosine_similarity(embeddings['a'], embeddings['b']):.4f}")

    print("Similarity (a vs c) — should be LOW (unrelated meaning):")
    print(f"  {cosine_similarity(embeddings['a'], embeddings['c']):.4f}")
