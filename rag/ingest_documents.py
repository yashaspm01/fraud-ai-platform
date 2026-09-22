import requests
from pathlib import Path
from pypdf import PdfReader
from sqlalchemy import create_engine, text
from database.connection import SessionLocal, DATABASE_URL
from database.models import DocumentChunk
from rag.cache import get_cached_embedding, set_cached_embedding

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 800      # characters per chunk
CHUNK_OVERLAP = 100   # characters shared between consecutive chunks


def extract_text(file_path: Path) -> str:
    if file_path.suffix == ".txt":
        return file_path.read_text()

    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text

def chunk_text(text_content: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text_content):
        end = start + chunk_size
        chunks.append(text_content[start:end])
        start += chunk_size - overlap   # move forward, but re-include the overlap
    return chunks


def embed(text_chunk: str) -> list[float]:
    cached = get_cached_embedding(text_chunk)
    if cached is not None:
        return cached
    try:
        response = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text_chunk}, timeout=30)
        response.raise_for_status()
        vector = response.json()["embedding"]
        set_cached_embedding(text_chunk, vector)
        return vector
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Embedding service unavailable: {e}")

def store_chunks(source_document: str, chunks: list[str]):
    db = SessionLocal()
    try:
        # Idempotency: clear any existing chunks for this exact document first,
        # so re-running ingestion (e.g. after fixing a bug, or re-processing an
        # updated document) never silently duplicates data.
        db.query(DocumentChunk).filter(
            DocumentChunk.source_document == source_document
        ).delete()

        for i, chunk in enumerate(chunks):
            vector = embed(chunk)
            db_chunk = DocumentChunk(
                source_document=source_document,
                chunk_index=i,
                content=chunk,
                embedding=vector,
            )
            db.add(db_chunk)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    documents_dir = Path("rag/documents")
    doc_files = list(documents_dir.glob("*.pdf")) + list(documents_dir.glob("*.txt"))

    for doc_path in doc_files:
        print(f"\n--- Processing {doc_path.name} ---")
        raw_text = extract_text(doc_path)
        print(f"  → {len(raw_text):,} characters extracted")

        chunks = chunk_text(raw_text, CHUNK_SIZE, CHUNK_OVERLAP)
        print(f"  → {len(chunks)} chunks created")

        store_chunks(doc_path.name, chunks)
        print(f"✅ Done with {doc_path.name}")
