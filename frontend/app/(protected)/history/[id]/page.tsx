"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Trash2 } from "lucide-react";
import { getAnalysisById, deleteAnalysis, skeletonVideoUrl } from "@/lib/api";
import { ScoreBadge } from "@/components/ScoreBadge";
import { FeedbackList } from "@/components/FeedbackList";
import { CameraErrorCard } from "@/components/CameraErrorCard";
import type { Analysis } from "@/types/analysis";

// Slides element in from bottom; animationDelay in ms from page load
function In({
  children,
  delay = 0,
  className = "",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  return (
    <div
      className={`animate-slide-up ${className}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

function DeleteModal({
  onConfirm,
  onCancel,
  deleting,
}: {
  onConfirm: () => void;
  onCancel: () => void;
  deleting: boolean;
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
        <h3 className="text-white font-semibold text-lg mb-2">Delete analysis?</h3>
        <p className="text-white/45 text-sm mb-6">
          This action cannot be undone. The analysis and its skeleton video will be permanently removed.
        </p>
        <div className="flex gap-3">
          <button
            onClick={close}
            disabled={deleting}
            className="flex-1 py-2.5 rounded-xl border border-white/10 text-white/55 hover:text-white/80 hover:border-white/20 transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={deleting}
            className="flex-1 py-2.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-400 hover:bg-red-500/25 hover:border-red-500/50 disabled:opacity-50 transition-colors text-sm font-medium"
          >
            {deleting ? "Deleting…" : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisDetailPage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    getAnalysisById(Number(id))
      .then(setAnalysis)
      .catch(() => setAnalysis(null))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteAnalysis(Number(id));
      router.push("/history");
    } catch {
      setDeleting(false);
      setShowModal(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-72px)] text-white/30 text-sm animate-pulse">
        Loading…
      </div>
    );
  }

  if (!analysis) {
    return (
      <div
        className="flex flex-col items-center justify-center h-[calc(100vh-72px)] gap-2 animate-fade-in"
        style={{ animationFillMode: "both" }}
      >
        <p className="text-white/40 text-sm">Analysis not found.</p>
      </div>
    );
  }

  const cameraError = analysis.feedbackItems.find((i) => i.aspect === "camera_angle");

  if (cameraError) {
    return (
      <div className="relative mx-auto max-w-lg px-4 py-12">
        <CameraErrorCard message={cameraError.message} />
      </div>
    );
  }

  const n = analysis.feedbackItems.length;
  // Animation timeline (ms from page load):
  // 0              — ScoreBadge (score-reveal ~550ms)
  // 320            — Feedback card slides in; items inside appear at 320 + i*150
  // 320 + n*150 + 180 — meta bar
  // 320 + n*150 + 320 — delete button
  // 320 + n*150 + 500 — video (right column, after all left items)
  const feedbackDelay = 320;
  const metaDelay = feedbackDelay + n * 150 + 180;
  const deleteDelay = feedbackDelay + n * 150 + 320;
  const videoDelay = feedbackDelay + n * 150 + 500;

  return (
    <>
      {showModal && (
        <DeleteModal
          onConfirm={handleDelete}
          onCancel={() => setShowModal(false)}
          deleting={deleting}
        />
      )}

      <div className="relative mx-auto max-w-5xl px-4 h-[calc(100vh-72px)] flex flex-col py-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 min-h-0">

          {/* ── Left column ── */}
          <div className="flex flex-col gap-4 min-h-0">

            {/* ScoreBadge is OUTSIDE the scroll container so its box-shadow is never clipped */}
            <ScoreBadge score={analysis.overallScore} delay={0} />

            {/* Scrollable: feedback + meta + delete */}
            <div className="flex flex-col gap-4 overflow-y-auto scrollbar-hide flex-1 pr-1">

              {n > 0 && (
                <In delay={feedbackDelay}>
                  <div className="glass-card p-5">
                    <h2 className="text-white/40 text-xs font-semibold uppercase tracking-widest mb-4">
                      Feedback
                    </h2>
                    {/* baseDelay = feedbackDelay so items start at feedbackDelay + i*150 */}
                    <FeedbackList items={analysis.feedbackItems} baseDelay={feedbackDelay} />
                  </div>
                </In>
              )}

              <In delay={metaDelay}>
                <div className="glass-card px-5 py-3.5 grid grid-cols-3 text-sm text-white/35">
                  <span className="capitalize">{analysis.exerciseId.replace(/_/g, " ")}</span>
                  <span className="capitalize text-center">{analysis.muscleGroup}</span>
                  <span className="text-right">{new Date(analysis.createdAt).toLocaleString()}</span>
                </div>
              </In>

              <In delay={deleteDelay}>
                <button
                  onClick={() => setShowModal(true)}
                  disabled={deleting}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400/70 hover:text-red-400 hover:bg-red-500/15 hover:border-red-500/35 disabled:opacity-40 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  <span className="font-medium">Delete analysis</span>
                </button>
              </In>

            </div>
          </div>

          {/* ── Right column: video appears after left side is done ── */}
          <In delay={videoDelay} className="flex flex-col min-h-0">
            {analysis.skeletonVideoPath ? (
              <div className="glass-card p-5 flex flex-col flex-1 min-h-0">
                <h2 className="text-white/40 text-xs font-semibold uppercase tracking-widest mb-4 shrink-0">
                  Skeleton Analysis
                </h2>
                <video
                  src={skeletonVideoUrl(analysis.id)}
                  controls
                  playsInline
                  className="flex-1 min-h-0 w-full rounded-xl bg-black"
                />
              </div>
            ) : (
              <div className="glass-card p-5 flex-1 flex items-center justify-center">
                <span className="text-white/20 text-sm">No skeleton video available</span>
              </div>
            )}
          </In>

        </div>
      </div>
    </>
  );
}
