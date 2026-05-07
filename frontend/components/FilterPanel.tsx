"use client";

import { Filters } from "@/lib/types";

interface FilterPanelProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
}

const STUDY_TYPES = ["RCT", "Meta-analysis", "Review", "Cohort", "Case Report"];

export default function FilterPanel({ filters, onChange }: FilterPanelProps) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Filters
      </h3>
      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-xs text-slate-400">Year Range</label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={2000}
              max={2026}
              value={filters.year_min || ""}
              onChange={(e) =>
                onChange({ ...filters, year_min: e.target.value ? parseInt(e.target.value) : undefined })
              }
              placeholder="2015"
              className="w-20 rounded border border-slate-600 bg-slate-900 px-2 py-1 text-xs text-slate-200 outline-none focus:border-primary-500"
            />
            <span className="text-slate-500">—</span>
            <input
              type="number"
              min={2000}
              max={2026}
              value={filters.year_max || ""}
              onChange={(e) =>
                onChange({ ...filters, year_max: e.target.value ? parseInt(e.target.value) : undefined })
              }
              placeholder="2026"
              className="w-20 rounded border border-slate-600 bg-slate-900 px-2 py-1 text-xs text-slate-200 outline-none focus:border-primary-500"
            />
          </div>
        </div>
        <div>
          <label className="mb-2 block text-xs text-slate-400">Study Type</label>
          <div className="flex flex-wrap gap-2">
            {STUDY_TYPES.map((type) => {
              const selected = filters.study_types?.includes(type);
              return (
                <button
                  key={type}
                  onClick={() => {
                    const current = filters.study_types || [];
                    const updated = selected
                      ? current.filter((t) => t !== type)
                      : [...current, type];
                    onChange({ ...filters, study_types: updated.length > 0 ? updated : undefined });
                  }}
                  className={`rounded-full border px-2.5 py-1 text-[11px] font-medium transition-all ${
                    selected
                      ? "border-primary-500 bg-primary-500/20 text-primary-300"
                      : "border-slate-600 text-slate-400 hover:border-slate-500"
                  }`}
                >
                  {type}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
