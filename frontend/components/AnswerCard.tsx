"use client";

import { Shield, ShieldAlert, ShieldCheck } from "lucide-react";
import { QueryResponse } from "@/lib/types";
import MetricsBadge from "./MetricsBadge";
import DisclaimerBanner from "./DisclaimerBanner";

interface AnswerCardProps {
  response: QueryResponse;
  onCitationHover: (index: number | null) => void;
}

export default function AnswerCard({ response, onCitationHover }: AnswerCardProps) {
  const confidenceConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
    high: {
      icon: <ShieldCheck className="h-4 w-4" />,
      color: "text-green-400",
      label: "High confidence",
    },
    medium: {
      icon: <Shield className="h-4 w-4" />,
      color: "text-yellow-400",
      label: "Medium confidence",
    },
    low: {
      icon: <ShieldAlert className="h-4 w-4" />,
      color: "text-red-400",
      label: "Low confidence",
    },
  };

  const conf = confidenceConfig[response.confidence] || confidenceConfig.low;

  const renderAnswer = (text: string) => {
    const parts = text.split(/(\[\d+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const citIndex = parseInt(match[1]) - 1;
        return (
          <button
            key={i}
            className="mx-0.5 inline-flex items-center justify-center rounded bg-primary-500/20 px-1.5 py-0.5 text-xs font-bold text-primary-300 transition-colors hover:bg-primary-500/40"
            onMouseEnter={() => onCitationHover(citIndex)}
            onMouseLeave={() => onCitationHover(null)}
          >
            {part}
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="space-y-4 rounded-xl border border-slate-700 bg-slate-800/50 p-6">
      <div className="flex items-center justify-between">
        <div className={`flex items-center gap-1.5 text-xs ${conf.color}`}>
          {conf.icon}
          <span>{conf.label}</span>
        </div>
        <MetricsBadge latency={response.latency_ms} />
      </div>
      <div className="text-sm leading-relaxed text-slate-200">
        {renderAnswer(response.answer)}
      </div>
      <DisclaimerBanner />
    </div>
  );
}
