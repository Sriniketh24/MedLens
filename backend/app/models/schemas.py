from pydantic import BaseModel, Field
from typing import Optional


class Filters(BaseModel):
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    study_types: Optional[list[str]] = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    filters: Optional[Filters] = None


class Paper(BaseModel):
    pmid: str
    title: str
    abstract: str
    authors: list[str]
    journal: str
    year: int
    study_type: Optional[str] = None
    similarity_score: Optional[float] = None
    rerank_score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Paper]
    confidence: str
    latency_ms: dict[str, float]
    disclaimer: str = (
        "This tool is for research purposes only. "
        "It does not provide medical advice. "
        "Consult a healthcare professional for clinical decisions."
    )


class AnalyticsEvent(BaseModel):
    query: str
    num_citations: int
    latency_total_ms: float
    latency_embed_ms: float
    latency_retrieve_ms: float
    latency_rerank_ms: float
    latency_generate_ms: float
    confidence: str
    was_refused: bool = False
