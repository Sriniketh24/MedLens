# MedLens

![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Next.js 14](https://img.shields.io/badge/Next.js-14-black)
![pgvector](https://img.shields.io/badge/pgvector-0.7-purple)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

**A hybrid retrieval-augmented generation engine for clinical evidence search over 30K+ PubMed abstracts.**

MedLens combines BM25 keyword search with dense vector retrieval, cross-encoder reranking, and LLM synthesis to deliver citation-grounded answers to medical research questions.

## Architecture

```
User Query
    |
    v
[Embed Query — MiniLM-L6-v2, 384-dim]
    |
    v
[Hybrid Retrieval]
    |-- Dense: pgvector cosine similarity (top 30)
    |-- Sparse: PostgreSQL tsvector BM25 (top 30)
    |
    v
[Reciprocal Rank Fusion — merge + deduplicate -> top 20]
    |
    v
[Cross-Encoder Rerank — ms-marco-MiniLM-L-6-v2 -> top 5]
    |
    v
[Safety Check — refuse personal diagnosis, flag uncertainty]
    |
    v
[Groq LLM — llama-3.1-8b-instant, citation-grounded synthesis]
    |
    v
[Response: answer + inline [1][2][3] citations + confidence + latency]
```

## Key Metrics

| Metric | Value |
|--------|-------|
| NDCG@10 (hybrid+rerank) | — |
| MRR | — |
| Citation Precision | — |
| Faithfulness Score | — |
| p95 Latency | — |
| Papers Indexed | 30K+ |

## Retrieval Strategy Comparison

Benchmarked on a 50-query labeled eval set with MeSH-based relevance judgments:

| Strategy | NDCG@10 | MRR | Avg Latency |
|----------|---------|-----|-------------|
| Keyword only (BM25) | — | — | — |
| Dense only (pgvector) | — | — | — |
| Hybrid (BM25 + dense) | — | — | — |
| Hybrid + rerank | — | — | — |
| No retrieval (LLM only) | — | — | — |

## Tech Stack

- **Frontend:** Next.js 14, Tailwind CSS, TypeScript
- **Backend:** FastAPI, Pydantic v2, Python 3.11
- **Database:** Supabase PostgreSQL + pgvector (384-dim embeddings)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **Reranker:** cross-encoder/ms-marco-MiniLM-L-6-v2
- **LLM:** Groq API (llama-3.1-8b-instant)
- **Data:** PubMed E-utilities API (30K+ abstracts)
- **CI/CD:** GitHub Actions
- **Deployment:** Vercel (frontend) + Railway (backend)

## Quick Start

```bash
# Clone
git clone https://github.com/Sriniketh24/MedLens.git
cd MedLens

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your keys

# Ingest PubMed data
python scripts/ingest_pubmed.py

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Design Decisions

**Why hybrid retrieval?**
Dense retrieval (pgvector cosine) captures semantic meaning but misses exact terminology. BM25 catches precise medical terms but misses synonyms. Reciprocal Rank Fusion combines both, consistently outperforming either alone in our benchmarks.

**Why cross-encoder reranking?**
Bi-encoder retrieval is fast but coarse. A cross-encoder jointly encodes query-document pairs for much finer relevance scoring. The added ~200ms latency is worth the precision gain for medical evidence.

**Why not GPT-4?**
Cost and speed. Groq serves llama-3.1-8b-instant at zero cost with sub-second latency. For citation-grounded synthesis (where the answer quality is bounded by retrieval quality, not generation capability), a smaller model with good instruction-following is sufficient.

## Eval Methodology

1. **Eval set:** 50 medical queries with MeSH-based relevance labels
2. **Metrics:** NDCG@10, MRR, citation precision, faithfulness (overlap-based)
3. **Baselines:** keyword-only, dense-only, hybrid, hybrid+rerank, no-retrieval
4. **Observability:** per-stage latency tracing (embed, retrieve, rerank, generate)

## License

MIT
