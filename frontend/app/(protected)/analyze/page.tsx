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
  const [errorExiting, setErrorExiting] = useState(false);
  // Tracks whether upload is done so the interval can simulate processing (60→97%)
  const uploadDoneRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Cancel in-flight XHR if the component unmounts during analysis
  useEffect(() => {
    return () => { abortControllerRef.current?.abort(); };
  }, []);

  // Warn before tab close/refresh while analysis is running
  useEffect(() => {
    if (!loading) return;
    const prevent = (e: BeforeUnloadEvent) => { e.preventDefault(); };
    window.addEventListener("beforeunload", prevent);
    return () => window.removeEventListener("beforeunload", prevent);
  }, [loading]);

  useEffect(() => {
    if (!loading) return;
    uploadDoneRef.current = false;
    const interval = setInterval(() => {
      if (uploadDoneRef.current) {
        // Steady slow increment — reaches 99% in ~70s so bar never stalls visually
        setProgress((p) => Math.min(p + 0.3 + Math.random() * 0.15, 99));
      }
    }, 700);
    return () => clearInterval(interval);
  }, [loading]);

  const handleAnalyze = async (file: File, exerciseId: string) => {
    abortControllerRef.current = new AbortController();
    setLoading(true);
    setProgress(1); // Start at 1% immediately so bar is never empty
    setError(null);
    setResult(null);
    try {
      const analysis = await analyzeVideo(file, exerciseId, (p) => {
        // api.ts sends 0-60 for upload bytes, 100 when request completes.
        // Map 0-60 → 1-55% so the bar starts smoothly from 1 instead of jumping.
        if (p <= 60) setProgress(1 + (p / 60) * 54);
        if (p >= 60) uploadDoneRef.current = true;
      }, abortControllerRef.current.signal);
      setProgress(100);
      await new Promise((r) => setTimeout(r, 350));
      setResult(analysis);
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const dismissError = () => {
    setErrorExiting(true);
    setTimeout(() => {
      setError(null);
      setErrorExiting(false);
    }, 250);
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
          <p className="text-white/40 text-sm text-center">
            Please don&apos;t navigate away — analysis is in progress
          </p>
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
                    onLoadedMetadata={(e) => { e.currentTarget.currentTime = 0.04; }}
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
      <div className="glass-card p-6 animate-fade-in relative overflow-hidden">
        <UploadZone onAnalyze={handleAnalyze} loading={loading} />
        {error && (
          <div
            className={`absolute inset-0 z-10 flex flex-col items-center justify-center rounded-[inherit] backdrop-blur-sm bg-black/50 ${errorExiting ? "animate-fade-out" : "animate-fade-in"}`}
          >
            <div className="bg-zinc-900/90 border border-white/10 rounded-2xl px-6 py-5 text-center max-w-[260px]">
              <p className="text-red-400 text-sm font-medium">{error}</p>
              <button
                onClick={dismissError}
                className="mt-4 px-5 py-2 text-sm text-white/50 border border-white/10 rounded-xl hover:border-white/30 hover:text-white/80 transition-all w-full"
              >
                Try again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
