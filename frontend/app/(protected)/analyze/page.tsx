"use client";

import { useState, useEffect, useRef } from "react";
import { RotateCcw } from "lucide-react";
import { UploadZone } from "@/components/UploadZone";
import { ScoreBadge } from "@/components/ScoreBadge";
import { FeedbackList } from "@/components/FeedbackList";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import { CameraErrorCard } from "@/components/CameraErrorCard";
import { analyzeVideo, skeletonVideoUrl } from "@/lib/api";
import type { Analysis } from "@/types/analysis";

function AnimatedSection({
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
      style={{ animationDelay: `${delay}ms`, animationFillMode: "both" }}
    >
      {children}
    </div>
  );
}

export default function AnalyzePage() {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Tracks whether upload is done so the interval can simulate processing (60→97%)
  const uploadDoneRef = useRef(false);

  useEffect(() => {
    if (!loading) return;
    uploadDoneRef.current = false;
    const interval = setInterval(() => {
      if (uploadDoneRef.current) {
        // Processing phase: slow exponential approach towards 97%
        setProgress((p) => (p < 97 ? Math.min(p + (97 - p) * 0.05 + Math.random() * 0.3, 97) : p));
      }
    }, 700);
    return () => clearInterval(interval);
  }, [loading]);

  const handleAnalyze = async (file: File, exerciseId: string) => {
    setLoading(true);
    setProgress(0);
    setError(null);
    setResult(null);
    try {
      const analysis = await analyzeVideo(file, exerciseId, (p) => {
        setProgress(p);
        // XHR reports 0-60 during upload; once it reaches 60, hand off to interval
        if (p >= 60) uploadDoneRef.current = true;
      });
      setProgress(100);
      await new Promise((r) => setTimeout(r, 350));
      setResult(analysis);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    setProgress(0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-72px)]">
        <div className="glass-card p-8 animate-fade-in w-full max-w-md mx-4">
          <LoadingOverlay progress={progress} />
        </div>
      </div>
    );
  }

  if (result) {
    const cameraError = result.feedbackItems.find((i) => i.aspect === "camera_angle");
    if (cameraError) {
      return (
        <div className="flex items-center justify-center h-[calc(100vh-72px)] px-4 animate-fade-in" style={{ animationFillMode: "both" }}>
          <div className="w-full max-w-lg">
            <CameraErrorCard message={cameraError.message} />
            <div className="mt-4 flex justify-center">
              <button
                onClick={reset}
                className="py-3 px-6 rounded-xl text-white/40 border border-white/10 hover:border-green-500/30 hover:text-white/75 transition-all text-sm flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Try again
              </button>
            </div>
          </div>
        </div>
      );
    }

    {
      const n = result.feedbackItems.length;
      const feedbackDelay = 320;
      const metaDelay = feedbackDelay + n * 150 + 180;
      const resetDelay = feedbackDelay + n * 150 + 320;
      const videoDelay = feedbackDelay + n * 150 + 500;

      return (
        <div className="relative mx-auto max-w-5xl px-4 h-[calc(100vh-72px)] flex flex-col py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 min-h-0">

            {/* ── Left column ── */}
            <div className="flex flex-col gap-4 min-h-0">

              {/* ScoreBadge OUTSIDE the scroll container — shadow won't be clipped */}
              <ScoreBadge score={result.overallScore} delay={0} />

              {/* Scrollable: feedback + meta + reset */}
              <div className="flex flex-col gap-4 overflow-y-auto scrollbar-hide flex-1 pr-1">

                {n > 0 && (
                  <AnimatedSection delay={feedbackDelay}>
                    <div className="glass-card p-5">
                      <h2 className="text-white/40 text-xs font-semibold uppercase tracking-widest mb-4">
                        Feedback
                      </h2>
                      <FeedbackList items={result.feedbackItems} baseDelay={feedbackDelay} />
                    </div>
                  </AnimatedSection>
                )}

                <AnimatedSection delay={metaDelay}>
                  <div className="glass-card px-5 py-3.5 grid grid-cols-3 text-sm text-white/35">
                    <span className="capitalize">{result.exerciseId.replace(/_/g, " ")}</span>
                    <span className="capitalize text-center">{result.muscleGroup}</span>
                    <span className="text-right">{new Date(result.createdAt).toLocaleString()}</span>
                  </div>
                </AnimatedSection>

                <AnimatedSection delay={resetDelay}>
                  <button
                    onClick={reset}
                    className="w-full py-3 rounded-xl text-white/40 border border-white/10 hover:border-green-500/30 hover:text-white/75 transition-all text-sm flex items-center justify-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Analyze another video
                  </button>
                </AnimatedSection>

              </div>
            </div>

            {/* ── Right column: video — appears after left side ── */}
            <AnimatedSection delay={videoDelay} className="flex flex-col min-h-0">
              {result.skeletonVideoPath ? (
                <div className="glass-card p-5 flex flex-col flex-1 min-h-0">
                  <h2 className="text-white/40 text-xs font-semibold uppercase tracking-widest mb-4 shrink-0">
                    Skeleton Analysis
                  </h2>
                  <video
                    src={skeletonVideoUrl(result.id)}
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
            </AnimatedSection>

          </div>
        </div>
      );
    }
  }

  return (
    <div className="relative mx-auto max-w-lg px-4 py-4">
      <div className="glass-card p-6 animate-fade-in">
        <UploadZone onAnalyze={handleAnalyze} loading={loading} />
        {error && (
          <div className="mt-5 p-4 rounded-xl bg-red-500/10 border border-red-500/25 text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
