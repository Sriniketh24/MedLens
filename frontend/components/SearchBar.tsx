"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";

interface SearchBarProps {
  onSubmit: (query: string) => void;
  loading: boolean;
}

export default function SearchBar({ onSubmit, loading }: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative group">
        <div className="absolute -inset-0.5 rounded-xl bg-gradient-to-r from-primary-600 to-primary-400 opacity-20 blur transition-opacity group-focus-within:opacity-40" />
        <div className="relative flex items-center rounded-xl border border-slate-700 bg-slate-900 shadow-2xl transition-all focus-within:border-primary-500/50">
          <Search className="ml-4 h-5 w-5 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a medical research question..."
            className="flex-1 bg-transparent px-4 py-4 text-lg text-slate-100 placeholder-slate-500 outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!query.trim() || loading}
            className="mr-2 flex items-center gap-2 rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-medium text-white transition-all hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Search"
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
