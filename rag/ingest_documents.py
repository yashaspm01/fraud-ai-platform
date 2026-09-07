import requests
from pathlib import Path
from pypdf import PdfReader
from sqlalchemy import create_engine, text
from database.connection import SessionLocal, DATABASE_URL
from database.models import DocumentChunk

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 800      # characters per chunk
CHUNK_OVERLAP = 100   # characters shared between consecutive chunks


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(pdf_path)
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
    response = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text_chunk})
    response.raise_for_status()
    return response.json()["embedding"]


def store_chunks(source_document: str, chunks: list[str]):
    db = SessionLocal()
    try:
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
    pdf_path = Path("rag/documents/bsa_aml_manual.pdf")

    print("Extracting text...")
    raw_text = extract_text(pdf_path)
    print(f"  → {len(raw_text):,} characters extracted")

    print("Chunking...")
    chunks = chunk_text(raw_text, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"  → {len(chunks)} chunks created")

    print("Embedding and storing (this calls Ollama once per chunk — may take a bit)...")
    store_chunks(pdf_path.name, chunks)

    print("✅ Done.")
