import { Check, AlertTriangle, X } from "lucide-react";
import type { FeedbackItem, FeedbackStatus } from "@/types/analysis";

const STATUS_CONFIG: Record<
  FeedbackStatus,
  {
    Icon: React.ComponentType<{ className?: string }>;
    className: string;
  }
> = {
  ok: {
    Icon: Check,
    className: "text-green-400 bg-green-500/[0.08] border-green-500/25",
  },
  warning: {
    Icon: AlertTriangle,
    className: "text-yellow-400 bg-yellow-500/[0.08] border-yellow-500/25",
  },
  error: {
    Icon: X,
    className: "text-red-400 bg-red-500/[0.08] border-red-500/25",
  },
};

export function FeedbackList({ items }: { items: FeedbackItem[] }) {
  return (
    <div className="space-y-2">
      {items.map((item, i) => {
        const config = STATUS_CONFIG[item.status as FeedbackStatus];
        const { Icon } = config;
        return (
          <div
            key={item.id}
            className={`flex items-start gap-3 rounded-xl border px-4 py-3 animate-slide-up ${config.className}`}
            style={{
              animationDelay: `${i * 0.12}s`,
              animationFillMode: "both",
            }}
          >
            <Icon className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold capitalize text-white/85 text-base">
                {item.aspect.replace(/_/g, " ")}
              </div>
              <div className="text-sm text-white/50 mt-0.5">{item.message}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
