"use client";

import { useState, useEffect } from "react";
import { Microscope } from "lucide-react";
import SearchBar from "@/components/SearchBar";
import AnswerCard from "@/components/AnswerCard";
import CitationCard from "@/components/CitationCard";
import FilterPanel from "@/components/FilterPanel";
import QueryHistory from "@/components/QueryHistory";
import { submitQuery } from "@/lib/api";
import { Filters, QueryResponse } from "@/lib/types";

export default function Home() {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>({});
  const [highlightedCitation, setHighlightedCitation] = useState<number | null>(null);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("medlens-history");
    if (saved) setQueryHistory(JSON.parse(saved));
  }, []);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await submitQuery(query, filters);
      setResponse(result);

      const updated = [query, ...queryHistory.filter((q) => q !== query)].slice(0, 20);
      setQueryHistory(updated);
      localStorage.setItem("medlens-history", JSON.stringify(updated));
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <div className="mb-4 flex items-center justify-center gap-3">
            <Microscope className="h-10 w-10 text-primary-400" />
            <h1 className="text-4xl font-bold tracking-tight text-white">
              Med<span className="text-primary-400">Lens</span>
            </h1>
          </div>
          <p className="text-slate-400">
            AI-powered clinical evidence search over 30K+ PubMed abstracts
          </p>
        </div>

        <div className="mx-auto max-w-3xl mb-8">
          <SearchBar onSubmit={handleSearch} loading={loading} />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
          <div className="space-y-4 lg:col-span-1">
            <FilterPanel filters={filters} onChange={setFilters} />
            <QueryHistory
              queries={queryHistory}
              onSelect={handleSearch}
              onClear={() => {
                setQueryHistory([]);
                localStorage.removeItem("medlens-history");
              }}
            />
          </div>

          <div className="space-y-6 lg:col-span-3">
            {error && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
                {error}
              </div>
            )}

            {response && (
              <>
                <AnswerCard
                  response={response}
                  onCitationHover={setHighlightedCitation}
                />
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-slate-300">
                    Sources ({response.citations.length})
                  </h3>
                  {response.citations.map((paper, i) => (
                    <CitationCard
                      key={paper.pmid}
                      paper={paper}
                      index={i}
                      highlighted={highlightedCitation === i}
                    />
                  ))}
                </div>
              </>
            )}

            {!response && !loading && !error && (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <Microscope className="mb-4 h-16 w-16 text-slate-700" />
                <p className="text-lg text-slate-500">
                  Ask a medical research question to get started
                </p>
                <p className="mt-2 text-sm text-slate-600">
                  Example: &quot;What are first-line treatments for community-acquired pneumonia?&quot;
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
