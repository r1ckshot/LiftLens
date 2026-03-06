import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import type { OverallScore } from "@/types/analysis";

const CONFIG: Record<
  OverallScore,
  {
    label: string;
    Icon: React.ComponentType<{ className?: string }>;
    className: string;
    iconClass: string;
  }
> = {
  good: {
    label: "Good",
    Icon: CheckCircle2,
    className:
      "text-green-400 border-green-500/40 bg-green-500/10 shadow-[0_0_50px_rgba(34,197,94,0.2)]",
    iconClass: "text-green-400",
  },
  needs_improvement: {
    label: "Needs Improvement",
    Icon: AlertTriangle,
    className:
      "text-yellow-400 border-yellow-500/40 bg-yellow-500/10 shadow-[0_0_50px_rgba(234,179,8,0.15)]",
    iconClass: "text-yellow-400",
  },
  poor: {
    label: "Poor",
    Icon: XCircle,
    className:
      "text-red-400 border-red-500/40 bg-red-500/10 shadow-[0_0_50px_rgba(239,68,68,0.15)]",
    iconClass: "text-red-400",
  },
};

export function ScoreBadge({
  score,
  compact = false,
  delay = 0,
}: {
  score: OverallScore;
  compact?: boolean;
  delay?: number;
}) {
  const { label, Icon, className, iconClass } = CONFIG[score];

  if (compact) {
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${className}`}>
        <Icon className={`w-3.5 h-3.5 ${iconClass}`} />
        {label}
      </span>
    );
  }

  return (
    <div
      className={`animate-score-reveal border-2 rounded-2xl px-6 py-6 text-center ${className}`}
      style={{ animationDelay: `${delay}ms`, animationFillMode: "both" }}
    >
      <Icon className={`w-12 h-12 mx-auto mb-3 ${iconClass}`} />
      <div className="text-xl font-bold tracking-wide">{label}</div>
    </div>
  );
}
