import time
from groq import Groq

from app.config import get_settings

SYSTEM_PROMPT = """You are a medical literature assistant. Answer the user's question using ONLY the provided research paper abstracts. Follow these rules strictly:

1. Cite sources using [1], [2], etc. corresponding to the paper order provided.
2. If the evidence is insufficient to answer, say "The available evidence does not adequately address this question."
3. Never provide personal medical advice or diagnosis.
4. Be concise and evidence-based.
5. If papers conflict, note the disagreement and cite both sides.
6. State the level of evidence when possible (e.g., RCT, cohort study, case report)."""

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        settings = get_settings()
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def build_context(papers: list[dict]) -> str:
    context_parts = []
    for i, paper in enumerate(papers, 1):
        authors = ", ".join(paper.get("authors", [])[:3])
        if len(paper.get("authors", [])) > 3:
            authors += " et al."
        context_parts.append(
            f"[{i}] {paper['title']}\n"
            f"Authors: {authors}\n"
            f"Journal: {paper.get('journal', 'Unknown')}, {paper.get('year', 'N/A')}\n"
            f"Abstract: {paper.get('abstract', 'No abstract available.')}\n"
        )
    return "\n---\n".join(context_parts)


def generate_answer(query: str, papers: list[dict]) -> tuple[str, str, float]:
    """Returns (answer_text, confidence, elapsed_ms)."""
    start = time.perf_counter()
    client = _get_client()

    context = build_context(papers)
    user_message = f"Question: {query}\n\nResearch Papers:\n{context}"

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content or ""
    elapsed_ms = (time.perf_counter() - start) * 1000

    citation_count = sum(1 for i in range(1, len(papers) + 1) if f"[{i}]" in answer)
    if citation_count >= len(papers) * 0.6:
        confidence = "high"
    elif citation_count >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return answer, confidence, elapsed_ms
