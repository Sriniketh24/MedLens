"use client";

import { History, X } from "lucide-react";

interface QueryHistoryProps {
  queries: string[];
  onSelect: (query: string) => void;
  onClear: () => void;
}

export default function QueryHistory({ queries, onSelect, onClear }: QueryHistoryProps) {
  if (queries.length === 0) return null;

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <History className="h-3 w-3" />
          Recent Queries
        </div>
        <button onClick={onClear} className="text-slate-500 hover:text-slate-300">
          <X className="h-3 w-3" />
        </button>
      </div>
      <div className="space-y-1.5">
        {queries.slice(0, 10).map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            className="block w-full truncate rounded px-2 py-1.5 text-left text-xs text-slate-300 transition-colors hover:bg-slate-700"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
