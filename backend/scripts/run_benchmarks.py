#!/usr/bin/env python3
"""Benchmark 5 retrieval strategies on the eval set."""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.services.embedder import embed_query
from app.services.retriever import dense_search, sparse_search, reciprocal_rank_fusion
from app.services.reranker import rerank
from app.eval.metrics import compute_ndcg, compute_mrr, compute_citation_precision


def run_strategy(strategy: str, query: str, query_embedding: list[float]) -> list[str]:
    """Run a retrieval strategy and return ranked PMIDs."""
    if strategy == "keyword_only":
        results = sparse_search(query, top_k=10)
        return [r["pmid"] for r in results]

    elif strategy == "dense_only":
        results = dense_search(query_embedding, top_k=10)
        return [r["pmid"] for r in results]

    elif strategy == "hybrid":
        dense_results = dense_search(query_embedding, top_k=30)
        sparse_results = sparse_search(query, top_k=30)
        fused = reciprocal_rank_fusion(dense_results, sparse_results)
        return [r["pmid"] for r in fused[:10]]

    elif strategy == "hybrid_rerank":
        dense_results = dense_search(query_embedding, top_k=30)
        sparse_results = sparse_search(query, top_k=30)
        fused = reciprocal_rank_fusion(dense_results, sparse_results)
        reranked, _ = rerank(query, fused[:20], top_k=10)
        return [r["pmid"] for r in reranked]

    elif strategy == "no_retrieval":
        return []

    return []


def main():
    eval_path = Path(__file__).parent.parent / "eval_set.json"
    if not eval_path.exists():
        print("Error: eval_set.json not found. Run generate_eval_set.py first.")
        sys.exit(1)

    with open(eval_path) as f:
        eval_set = json.load(f)

    strategies = ["keyword_only", "dense_only", "hybrid", "hybrid_rerank", "no_retrieval"]
    results = {s: {"ndcg_scores": [], "mrr_scores": [], "latencies": []} for s in strategies}

    print(f"Running benchmarks on {len(eval_set)} queries across {len(strategies)} strategies")
    print("=" * 70)

    for item in eval_set:
        query = item["query"]
        relevant = set(item["relevant_pmids"])
        if not relevant:
            continue

        query_embedding = embed_query(query)

        for strategy in strategies:
            start = time.perf_counter()
            retrieved_pmids = run_strategy(strategy, query, query_embedding)
            elapsed = (time.perf_counter() - start) * 1000

            ndcg = compute_ndcg(retrieved_pmids, relevant, k=10)
            mrr = compute_mrr(retrieved_pmids, relevant)

            results[strategy]["ndcg_scores"].append(ndcg)
            results[strategy]["mrr_scores"].append(mrr)
            results[strategy]["latencies"].append(elapsed)

    print(f"\n{'Strategy':<20} {'NDCG@10':<10} {'MRR':<10} {'Latency (ms)':<15}")
    print("-" * 55)

    summary = {}
    for strategy in strategies:
        scores = results[strategy]
        avg_ndcg = sum(scores["ndcg_scores"]) / max(len(scores["ndcg_scores"]), 1)
        avg_mrr = sum(scores["mrr_scores"]) / max(len(scores["mrr_scores"]), 1)
        avg_latency = sum(scores["latencies"]) / max(len(scores["latencies"]), 1)

        print(f"{strategy:<20} {avg_ndcg:<10.4f} {avg_mrr:<10.4f} {avg_latency:<15.1f}")
        summary[strategy] = {
            "ndcg_at_10": round(avg_ndcg, 4),
            "mrr": round(avg_mrr, 4),
            "avg_latency_ms": round(avg_latency, 1),
            "num_queries": len(scores["ndcg_scores"]),
        }

    output_path = Path(__file__).parent.parent / "benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
