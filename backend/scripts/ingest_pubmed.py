#!/usr/bin/env python3
"""Ingest PubMed abstracts into Supabase with embeddings for MedLens."""

import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx
from tqdm import tqdm

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.services.embedder import embed_documents
from supabase import create_client

SEARCH_QUERIES = [
    "pneumonia diagnosis treatment",
    "chest radiograph findings pathology",
    "community acquired pneumonia pediatric",
    "lung cancer screening CT",
    "tuberculosis detection machine learning",
    "cardiac imaging echocardiography",
    "stroke diagnosis neuroimaging",
    "diabetes mellitus management",
    "hypertension treatment guidelines",
    "antibiotic resistance mechanisms",
    "COVID-19 treatment outcomes",
    "breast cancer screening mammography",
    "chronic obstructive pulmonary disease",
    "acute respiratory distress syndrome",
    "deep learning medical imaging",
]

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
BATCH_SIZE = 200
EMBED_BATCH_SIZE = 64
TARGET_PAPERS = 30000


def _request_with_retry(url: str, params: dict, max_retries: int = 3) -> httpx.Response:
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=90) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                return resp
        except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  Retry {attempt + 1}/{max_retries} after {e.__class__.__name__}, waiting {wait}s...")
            time.sleep(wait)


def search_pubmed(query: str, retmax: int = 2000) -> list[str]:
    """Search PubMed and return list of PMIDs."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
        "sort": "relevance",
    }
    resp = _request_with_retry(PUBMED_SEARCH_URL, params)
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_abstracts(pmids: list[str]) -> list[dict]:
    """Fetch article details for a batch of PMIDs."""
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    resp = _request_with_retry(PUBMED_FETCH_URL, params)

    root = ET.fromstring(resp.content)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        try:
            medline = article.find(".//MedlineCitation")
            pmid = medline.find(".//PMID").text
            art = medline.find(".//Article")
            title = art.find(".//ArticleTitle").text or ""

            abstract_elem = art.find(".//Abstract")
            if abstract_elem is None:
                continue
            abstract_parts = abstract_elem.findall(".//AbstractText")
            abstract = " ".join(t.text or "" for t in abstract_parts).strip()
            if len(abstract) < 50:
                continue

            authors = []
            author_list = art.find(".//AuthorList")
            if author_list is not None:
                for author in author_list.findall(".//Author"):
                    last = author.find("LastName")
                    first = author.find("ForeName")
                    if last is not None and first is not None:
                        authors.append(f"{first.text} {last.text}")

            journal_elem = art.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else "Unknown"

            year_elem = art.find(".//Journal/JournalIssue/PubDate/Year")
            year = int(year_elem.text) if year_elem is not None else 0

            pub_types = [
                pt.text for pt in medline.findall(".//PublicationTypeList/PublicationType")
            ]
            study_type = classify_study_type(pub_types)

            papers.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors[:10],
                "journal": journal,
                "year": year,
                "study_type": study_type,
            })
        except (AttributeError, TypeError):
            continue

    return papers


def classify_study_type(pub_types: list[str]) -> str:
    pub_types_lower = [pt.lower() for pt in pub_types]
    if any("randomized controlled trial" in pt for pt in pub_types_lower):
        return "RCT"
    if any("meta-analysis" in pt for pt in pub_types_lower):
        return "Meta-analysis"
    if any("systematic review" in pt or "review" in pt for pt in pub_types_lower):
        return "Review"
    if any("case reports" in pt for pt in pub_types_lower):
        return "Case Report"
    if any("cohort" in pt or "observational" in pt for pt in pub_types_lower):
        return "Cohort"
    return "Other"


def main():
    settings = get_settings()
    client = create_client(settings.supabase_url, settings.supabase_key)

    all_pmids: set[str] = set()
    all_papers: list[dict] = []

    print(f"Target: {TARGET_PAPERS} papers from {len(SEARCH_QUERIES)} queries")
    print("=" * 60)

    for query in tqdm(SEARCH_QUERIES, desc="Searching PubMed"):
        per_query = TARGET_PAPERS // len(SEARCH_QUERIES)
        pmids = search_pubmed(query, retmax=per_query)
        new_pmids = [p for p in pmids if p not in all_pmids]
        all_pmids.update(new_pmids)

        for i in tqdm(range(0, len(new_pmids), BATCH_SIZE), desc=f"  Fetching '{query[:30]}'", leave=False):
            batch_pmids = new_pmids[i:i + BATCH_SIZE]
            papers = fetch_abstracts(batch_pmids)
            all_papers.extend(papers)
            time.sleep(0.34)  # respect 3 req/sec rate limit

    print(f"\nFetched {len(all_papers)} papers with abstracts")
    print("Embedding papers...")

    texts = [f"{p['title']} {p['abstract']}" for p in all_papers]
    embeddings = embed_documents(texts, batch_size=EMBED_BATCH_SIZE)

    print("Upserting to Supabase...")
    upsert_batch_size = 100
    for i in tqdm(range(0, len(all_papers), upsert_batch_size), desc="Upserting"):
        batch = []
        for j in range(i, min(i + upsert_batch_size, len(all_papers))):
            paper = all_papers[j]
            paper["embedding"] = embeddings[j]
            batch.append(paper)

        for attempt in range(3):
            try:
                client.table("papers").upsert(batch, on_conflict="pmid").execute()
                break
            except Exception as e:
                if attempt == 2:
                    print(f"\n  Failed batch at index {i}: {e}")
                    break
                time.sleep(2 ** attempt)

    print(f"\nDone! Indexed {len(all_papers)} papers.")


if __name__ == "__main__":
    main()
