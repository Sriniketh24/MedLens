"use client";

import { useState } from "react";
import { ExternalLink, ChevronDown, ChevronUp } from "lucide-react";
import { Paper } from "@/lib/types";

interface CitationCardProps {
  paper: Paper;
  index: number;
  highlighted: boolean;
}

export default function CitationCard({ paper, index, highlighted }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);

  const studyTypeBadgeColor: Record<string, string> = {
    RCT: "bg-green-500/20 text-green-300 border-green-500/30",
    "Meta-analysis": "bg-purple-500/20 text-purple-300 border-purple-500/30",
    Review: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    "Case Report": "bg-orange-500/20 text-orange-300 border-orange-500/30",
    Cohort: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
    Other: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  };

  return (
    <div
      className={`rounded-lg border p-4 transition-all duration-200 ${
        highlighted
          ? "border-primary-500/50 bg-primary-500/10 citation-highlight"
          : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-600 text-xs font-bold text-white">
              {index + 1}
            </span>
            <h4 className="text-sm font-medium text-slate-100 line-clamp-2">
              {paper.title}
            </h4>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
            <span>{paper.authors.slice(0, 3).join(", ")}{paper.authors.length > 3 ? " et al." : ""}</span>
            <span>·</span>
            <span>{paper.journal}</span>
            <span>·</span>
            <span>{paper.year}</span>
            {paper.study_type && (
              <span className={`rounded-full border px-2 py-0.5 text-[10px] font-medium ${studyTypeBadgeColor[paper.study_type] || studyTypeBadgeColor.Other}`}>
                {paper.study_type}
              </span>
            )}
          </div>
          {paper.rerank_score !== undefined && (
            <div className="mt-2 flex items-center gap-2">
              <div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-700">
                <div
                  className="h-full rounded-full bg-primary-500"
                  style={{ width: `${Math.min(paper.rerank_score * 100, 100)}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-500">
                relevance {(paper.rerank_score * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
        <a
          href={`https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}`}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 rounded p-1 text-slate-400 hover:bg-slate-700 hover:text-primary-400"
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
      {paper.abstract && (
        <div className="mt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
          >
            {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            {expanded ? "Hide abstract" : "Show abstract"}
          </button>
          {expanded && (
            <p className="mt-2 text-xs leading-relaxed text-slate-300">
              {paper.abstract}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
