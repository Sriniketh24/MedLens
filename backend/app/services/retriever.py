import time
from supabase import create_client, Client

from app.config import get_settings
from app.models.schemas import Paper

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


def dense_search(query_embedding: list[float], top_k: int = 30, filters: dict | None = None) -> list[dict]:
    client = _get_client()
    params = {"query_embedding": query_embedding, "match_count": top_k}
    if filters and filters.get("year_min"):
        params["filter_year_min"] = filters["year_min"]
    if filters and filters.get("year_max"):
        params["filter_year_max"] = filters["year_max"]

    response = client.rpc("match_papers_dense", params).execute()
    return response.data or []


def sparse_search(query_text: str, top_k: int = 30, filters: dict | None = None) -> list[dict]:
    client = _get_client()
    params = {"search_query": query_text, "match_count": top_k}
    if filters and filters.get("year_min"):
        params["filter_year_min"] = filters["year_min"]
    if filters and filters.get("year_max"):
        params["filter_year_max"] = filters["year_max"]

    response = client.rpc("match_papers_sparse", params).execute()
    return response.data or []


def reciprocal_rank_fusion(dense_results: list[dict], sparse_results: list[dict], k: int = 60) -> list[dict]:
    """Merge dense and sparse results using RRF scoring."""
    scores: dict[str, float] = {}
    paper_map: dict[str, dict] = {}

    for rank, doc in enumerate(dense_results):
        pmid = doc["pmid"]
        scores[pmid] = scores.get(pmid, 0) + 1.0 / (k + rank + 1)
        paper_map[pmid] = doc

    for rank, doc in enumerate(sparse_results):
        pmid = doc["pmid"]
        scores[pmid] = scores.get(pmid, 0) + 1.0 / (k + rank + 1)
        if pmid not in paper_map:
            paper_map[pmid] = doc

    sorted_pmids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    results = []
    for pmid in sorted_pmids:
        paper = paper_map[pmid]
        paper["rrf_score"] = scores[pmid]
        results.append(paper)

    return results


def hybrid_retrieve(
    query_text: str,
    query_embedding: list[float],
    top_k: int = 20,
    filters: dict | None = None,
) -> tuple[list[dict], float]:
    start = time.perf_counter()
    settings = get_settings()

    dense_results = dense_search(query_embedding, settings.top_k_dense, filters)
    sparse_results = sparse_search(query_text, settings.top_k_sparse, filters)
    fused = reciprocal_rank_fusion(dense_results, sparse_results)

    elapsed_ms = (time.perf_counter() - start) * 1000
    return fused[:top_k], elapsed_ms
