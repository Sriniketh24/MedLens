"use client";

import { Clock } from "lucide-react";

interface MetricsBadgeProps {
  latency: Record<string, number>;
}

export default function MetricsBadge({ latency }: MetricsBadgeProps) {
  return (
    <div className="group relative inline-flex items-center gap-1 rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">
      <Clock className="h-3 w-3" />
      <span>{Math.round(latency.total || 0)}ms</span>
      <div className="absolute bottom-full left-0 z-10 mb-2 hidden w-48 rounded-lg border border-slate-700 bg-slate-800 p-3 text-xs shadow-xl group-hover:block">
        <div className="space-y-1">
          <div className="flex justify-between">
            <span className="text-slate-400">Embed</span>
            <span className="text-slate-200">{Math.round(latency.embed || 0)}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Retrieve</span>
            <span className="text-slate-200">{Math.round(latency.retrieve || 0)}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Rerank</span>
            <span className="text-slate-200">{Math.round(latency.rerank || 0)}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Generate</span>
            <span className="text-slate-200">{Math.round(latency.generate || 0)}ms</span>
          </div>
        </div>
      </div>
    </div>
  );
}
