import time
from fastapi import APIRouter

from app.models.schemas import QueryRequest, QueryResponse, Paper, AnalyticsEvent
from app.services.embedder import embed_query
from app.services.retriever import hybrid_retrieve
from app.services.reranker import rerank
from app.services.generator import generate_answer
from app.services.safety import check_query_safety
from app.config import get_settings

router = APIRouter()


def _log_analytics(event: AnalyticsEvent):
    """Log query analytics to Supabase."""
    try:
        from supabase import create_client
        settings = get_settings()
        client = create_client(settings.supabase_url, settings.supabase_key)
        client.table("analytics").insert(event.model_dump()).execute()
    except Exception:
        pass


@router.post("/query", response_model=QueryResponse)
async def query_papers(request: QueryRequest):
    total_start = time.perf_counter()

    is_safe, refusal = check_query_safety(request.question)
    if not is_safe:
        return QueryResponse(
            answer=refusal,
            citations=[],
            confidence="n/a",
            latency_ms={"total": 0},
        )

    filters = None
    if request.filters:
        filters = request.filters.model_dump(exclude_none=True)

    embed_start = time.perf_counter()
    query_embedding = embed_query(request.question)
    embed_ms = (time.perf_counter() - embed_start) * 1000

    retrieved, retrieve_ms = hybrid_retrieve(
        query_text=request.question,
        query_embedding=query_embedding,
        top_k=get_settings().top_k_fused,
        filters=filters,
    )

    reranked, rerank_ms = rerank(request.question, retrieved, top_k=get_settings().top_k_rerank)

    answer_text, confidence, generate_ms = generate_answer(request.question, reranked)

    total_ms = (time.perf_counter() - total_start) * 1000

    citations = [
        Paper(
            pmid=doc["pmid"],
            title=doc["title"],
            abstract=doc.get("abstract", ""),
            authors=doc.get("authors", []),
            journal=doc.get("journal", "Unknown"),
            year=doc.get("year", 0),
            study_type=doc.get("study_type"),
            similarity_score=doc.get("rrf_score"),
            rerank_score=doc.get("rerank_score"),
        )
        for doc in reranked
    ]

    latency_ms = {
        "embed": round(embed_ms, 1),
        "retrieve": round(retrieve_ms, 1),
        "rerank": round(rerank_ms, 1),
        "generate": round(generate_ms, 1),
        "total": round(total_ms, 1),
    }

    _log_analytics(AnalyticsEvent(
        query=request.question,
        num_citations=len(citations),
        latency_total_ms=total_ms,
        latency_embed_ms=embed_ms,
        latency_retrieve_ms=retrieve_ms,
        latency_rerank_ms=rerank_ms,
        latency_generate_ms=generate_ms,
        confidence=confidence,
    ))

    return QueryResponse(
        answer=answer_text,
        citations=citations,
        confidence=confidence,
        latency_ms=latency_ms,
    )
