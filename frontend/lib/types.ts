export interface Filters {
  year_min?: number;
  year_max?: number;
  study_types?: string[];
}

export interface Paper {
  pmid: string;
  title: string;
  abstract: string;
  authors: string[];
  journal: string;
  year: number;
  study_type?: string;
  similarity_score?: number;
  rerank_score?: number;
}

export interface QueryResponse {
  answer: string;
  citations: Paper[];
  confidence: string;
  latency_ms: Record<string, number>;
  disclaimer: string;
}
