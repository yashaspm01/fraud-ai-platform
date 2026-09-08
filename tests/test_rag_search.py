from rag.search import semantic_search

def test_semantic_search_returns_expected_count():
    results = semantic_search("What is required of a BSA compliance officer?", top_k=5)
    assert len(results) == 5

def test_semantic_search_no_duplicates():
    # Regression guard — Week 2 duplicate-chunk incident
    results = semantic_search("BSA compliance officer requirements", top_k=5)
    assert len(set(r.chunk_index for r in results)) == 5
