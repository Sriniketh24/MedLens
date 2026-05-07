"use client";

import { AlertTriangle } from "lucide-react";

export default function DisclaimerBanner() {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm text-amber-200">
      <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
      <p>
        This tool is for research purposes only. It does not provide medical
        advice. Consult a healthcare professional for clinical decisions.
      </p>
    </div>
  );
}
