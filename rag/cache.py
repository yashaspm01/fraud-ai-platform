_embedding_cache = {}
_answer_cache = {}


def get_cached_embedding(text: str):
    """Returns a cached embedding for exact text match, or None."""
    return _embedding_cache.get(text)


def set_cached_embedding(text: str, vector: list):
    """Stores an embedding for exact text match."""
    _embedding_cache[text] = vector


def get_cached_answer(question: str):
    """Returns a cached (answer, sources) pair for exact question match, or None."""
    return _answer_cache.get(question)


def set_cached_answer(question: str, answer: str, sources: list):
    """Stores an (answer, sources) pair for exact question match."""
    _answer_cache[question] = (answer, sources)
