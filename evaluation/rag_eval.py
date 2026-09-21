from rag.generate_answer import generate_answer

GOLDEN_SET = [
    {"question": "What is required of a BSA compliance officer?", "expected_keywords": ["compliance officer", "authority", "independence"]},
    {"question": "What is BSA/AML", "expected_keywords": ["Bank Secrecy Act", "Anti-Money Laundering"]},
    {"question": "What happens if a bank fails to comply with BSA/AML requirements?", "expected_keywords": ["violation", "enforcement", "supervisory"]},
    {"question": "What is the capital of France?", "expected_keywords": None},
]


def evaluate():
    """Runs the golden set and scores retrieval relevance + refusal correctness by keyword match."""
    hits, total = 0, len(GOLDEN_SET)
    for case in GOLDEN_SET:
        answer, sources = generate_answer(case["question"])

        if case["expected_keywords"] is None:
            correct = len(sources) == 0
        else:
            combined_text = " ".join(s.content.lower() for s in sources)
            correct = any(kw.lower() in combined_text for kw in case["expected_keywords"])

        hits += correct
        print(f"{'✅' if correct else '❌'} {case['question']}")
        print(f"   retrieved chunks: {sorted(s.chunk_index for s in sources)}")

    print(f"\nScore: {hits}/{total}")


if __name__ == "__main__":
    evaluate()
