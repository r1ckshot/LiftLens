"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronRight, History, Trash2 } from "lucide-react";
import { getAnalyses, deleteAllAnalyses } from "@/lib/api";
import { ScoreBadge } from "@/components/ScoreBadge";
import type { Analysis } from "@/types/analysis";

function ClearAllModal({
  onConfirm,
  onCancel,
  clearing,
}: {
  onConfirm: () => void;
  onCancel: () => void;
  clearing: boolean;
}) {
  const [closing, setClosing] = useState(false);

  const close = () => {
    setClosing(true);
    setTimeout(onCancel, 280);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div
        className={`absolute inset-0 bg-black/60 backdrop-blur-sm ${closing ? "animate-fade-out" : "animate-fade-in"}`}
        style={{ animationFillMode: "both" }}
        onClick={close}
      />
      <div
        className={`relative glass-card p-6 w-full max-w-sm ${closing ? "animate-slide-down-out" : "animate-slide-up"}`}
        style={{ animationFillMode: "both" }}
      >
        <h3 className="text-white font-semibold text-lg mb-2">Clear all history?</h3>
        <p className="text-white/45 text-sm mb-6">
          This will permanently delete all your analyses and their skeleton videos. This cannot be undone.
        </p>
        <div className="flex gap-3">
          <button
            onClick={close}
            disabled={clearing}
            className="flex-1 py-2.5 rounded-xl border border-white/10 text-white/55 hover:text-white/80 hover:border-white/20 transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={clearing}
            className="flex-1 py-2.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-400 hover:bg-red-500/25 hover:border-red-500/50 disabled:opacity-50 transition-colors text-sm font-medium"
          >
            {clearing ? "Clearing…" : "Clear all"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showClearModal, setShowClearModal] = useState(false);
  const [clearing, setClearing] = useState(false);

  useEffect(() => {
    getAnalyses()
      .then(setAnalyses)
      .catch(() => setError("Failed to load history. Please try again."))
      .finally(() => setLoading(false));
  }, []);

  const handleClearAll = async () => {
    setClearing(true);
    try {
      await deleteAllAnalyses();
      setAnalyses([]);
      setShowClearModal(false);
    } catch {
      setShowClearModal(false);
    } finally {
      setClearing(false);
    }
  };

  return (
    <>
      {showClearModal && (
        <ClearAllModal
          onConfirm={handleClearAll}
          onCancel={() => setShowClearModal(false)}
          clearing={clearing}
        />
      )}

      <div className="relative mx-auto max-w-2xl px-4 py-12 pb-20">
        <div
          className="flex items-center justify-between mb-8 animate-fade-in"
          style={{ animationFillMode: "both" }}
        >
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <History className="w-6 h-6 text-white/50" />
            History
          </h1>

          {analyses.length > 0 && (
            <button
              onClick={() => setShowClearModal(true)}
              className="flex items-center gap-1.5 text-white/25 text-sm hover:text-red-400/60 transition-colors duration-200"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear all
            </button>
          )}
        </div>

        {loading ? (
          <div className="text-white/30 text-sm text-center py-12 animate-pulse">
            Loading…
          </div>
        ) : error ? (
          <div
            className="glass-card p-6 text-center text-red-400/70 text-sm animate-fade-in"
            style={{ animationFillMode: "both" }}
          >
            {error}
          </div>
        ) : analyses.length === 0 ? (
          <div
            className="glass-card p-8 text-center text-white/30 text-sm animate-fade-in"
            style={{ animationFillMode: "both" }}
          >
            No analyses yet. Upload a video to get started.
          </div>
        ) : (
          <div className="space-y-3">
            {analyses.map((a, i) => (
              <Link
                key={a.id}
                href={`/history/${a.id}`}
                className="glass-card px-5 py-4 flex items-center gap-4 hover:border-green-500/20 hover:scale-[1.01] transition-all duration-200 group animate-fade-in"
                style={{ animationDelay: `${i * 70}ms`, animationFillMode: "both" }}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-white/85 text-base font-semibold capitalize">
                      {a.exerciseId.replace(/_/g, " ")}
                    </span>
                    <span className="text-white/35 text-sm capitalize">{a.muscleGroup}</span>
                  </div>
                  <span className="text-white/30 text-xs">
                    {new Date(a.createdAt).toLocaleString()}
                  </span>
                </div>
                <div className="shrink-0">
                  <ScoreBadge score={a.overallScore} compact />
                </div>
                <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-white/40 transition-colors shrink-0" />
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
