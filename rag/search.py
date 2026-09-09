from database.connection import SessionLocal
from database.models import DocumentChunk
from rag.ingest_documents import embed  # reuse the same embedding function


def semantic_search(query: str, top_k: int = 5):
    query_vector = embed(query)

    db = SessionLocal()
    try:
        results = (
            db.query(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(top_k)
            .all()
        )
        return results
    finally:
        db.close()

def semantic_search_with_scores(query: str, top_k: int = 15):
    query_vector = embed(query)
    db = SessionLocal()
    try:
        results = (
            db.query(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_vector).label("distance"),
            )
            .order_by("distance")
            .limit(top_k)
            .all()
        )
        return results
    finally:
        db.close()


if __name__ == "__main__":
    query = "What is required of a BSA compliance officer?"

    print(f"Query: {query}\n")
    results = semantic_search(query)

    for i, chunk in enumerate(results, 1):
        print(f"--- Result {i} (source: {chunk.source_document}, chunk #{chunk.chunk_index}) ---")
        print(chunk.content[:300].strip())
        print()
