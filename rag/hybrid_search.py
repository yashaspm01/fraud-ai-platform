from rank_bm25 import BM25Okapi
from database.connection import SessionLocal
from database.models import DocumentChunk
from rag.search import semantic_search_with_scores


def _load_all_chunks():
    """Loads every chunk once for BM25 indexing."""
    db = SessionLocal()
    try:
        return db.query(DocumentChunk).all()
    finally:
        db.close()


_all_chunks = _load_all_chunks()
_tokenized = [c.content.lower().split() for c in _all_chunks]
_bm25 = BM25Okapi(_tokenized)


def bm25_search(query: str, top_k: int = 15):
    """Keyword-ranks all chunks against the query using BM25."""
    scores = _bm25.get_scores(query.lower().split())
    ranked = sorted(zip(_all_chunks, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def hybrid_search(query: str, top_k: int = 15, vector_weight: float = 0.6):
    """Combines vector and BM25 rankings into one score per chunk."""
    vector_results = semantic_search_with_scores(query, top_k=top_k * 2)
    bm25_results = bm25_search(query, top_k=top_k * 2)

    vector_scores = {c.id: 1 - d for c, d in vector_results}
    max_bm25 = max((s for _, s in bm25_results), default=1) or 1
    bm25_scores = {c.id: s / max_bm25 for c, s in bm25_results}

    all_ids = set(vector_scores) | set(bm25_scores)
    combined = {}
    chunk_by_id = {c.id: c for c, _ in vector_results}
    chunk_by_id.update({c.id: c for c, _ in bm25_results})

    for cid in all_ids:
        v = vector_scores.get(cid, 0)
        b = bm25_scores.get(cid, 0)
        combined[cid] = vector_weight * v + (1 - vector_weight) * b

    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return [(chunk_by_id[cid], score) for cid, score in ranked[:top_k]]
