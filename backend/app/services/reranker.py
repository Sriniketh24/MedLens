import time
from sentence_transformers import CrossEncoder

from app.config import get_settings

_reranker: CrossEncoder | None = None


def _get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        settings = get_settings()
        _reranker = CrossEncoder(settings.reranker_model)
    return _reranker


def rerank(query: str, documents: list[dict], top_k: int = 5) -> tuple[list[dict], float]:
    start = time.perf_counter()
    reranker = _get_reranker()

    pairs = [(query, doc.get("abstract", "") or doc.get("title", "")) for doc in documents]
    scores = reranker.predict(pairs)

    for i, doc in enumerate(documents):
        doc["rerank_score"] = float(scores[i])

    ranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return ranked[:top_k], elapsed_ms
