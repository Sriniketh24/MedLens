import numpy as np


def compute_ndcg(retrieved_pmids: list[str], relevant_pmids: set[str], k: int = 10) -> float:
    """Normalized Discounted Cumulative Gain at k."""
    retrieved = retrieved_pmids[:k]
    dcg = sum(
        (1.0 / np.log2(i + 2)) for i, pmid in enumerate(retrieved) if pmid in relevant_pmids
    )
    ideal = sorted([1] * min(len(relevant_pmids), k) + [0] * max(0, k - len(relevant_pmids)), reverse=True)
    idcg = sum((rel / np.log2(i + 2)) for i, rel in enumerate(ideal) if rel > 0)
    return dcg / idcg if idcg > 0 else 0.0


def compute_mrr(retrieved_pmids: list[str], relevant_pmids: set[str]) -> float:
    """Mean Reciprocal Rank."""
    for i, pmid in enumerate(retrieved_pmids):
        if pmid in relevant_pmids:
            return 1.0 / (i + 1)
    return 0.0


def compute_citation_precision(cited_pmids: list[str], relevant_pmids: set[str]) -> float:
    """Fraction of cited papers that are actually relevant."""
    if not cited_pmids:
        return 0.0
    hits = sum(1 for pmid in cited_pmids if pmid in relevant_pmids)
    return hits / len(cited_pmids)


def compute_faithfulness(answer: str, source_texts: list[str]) -> float:
    """Simple overlap-based faithfulness: fraction of answer sentences with source support."""
    answer_sentences = [s.strip() for s in answer.split(".") if len(s.strip()) > 10]
    if not answer_sentences:
        return 0.0

    combined_sources = " ".join(source_texts).lower()
    supported = 0
    for sentence in answer_sentences:
        words = sentence.lower().split()
        key_words = [w for w in words if len(w) > 4]
        if not key_words:
            supported += 1
            continue
        overlap = sum(1 for w in key_words if w in combined_sources)
        if overlap / len(key_words) > 0.4:
            supported += 1

    return supported / len(answer_sentences)
