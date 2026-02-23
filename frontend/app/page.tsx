"use client";

import { useState, useEffect } from "react";
import { Dumbbell, RotateCcw } from "lucide-react";
import { UploadZone } from "@/components/UploadZone";
import { ScoreBadge } from "@/components/ScoreBadge";
import { FeedbackList } from "@/components/FeedbackList";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import { analyzeVideo, skeletonVideoUrl } from "@/lib/api";
import type { Analysis } from "@/types/analysis";

function AnimatedSection({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <div
      className="animate-slide-up"
      style={{ animationDelay: `${delay}ms`, animationFillMode: "both" }}
    >
      {children}
    </div>
  );
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Simulate progress while loading
  useEffect(() => {
    if (!loading) return;
    setProgress(6);
    const interval = setInterval(() => {
      setProgress((p) => Math.min(p + (97 - p) * 0.06 + Math.random() * 0.5, 97));
    }, 700);
    return () => clearInterval(interval);
  }, [loading]);

  const handleAnalyze = async (file: File, exerciseId: string) => {
    setLoading(true);
    setProgress(0);
    setError(null);
    setResult(null);
    try {
      const analysis = await analyzeVideo(file, exerciseId);
      setProgress(100);
      // Brief pause so the 100% state is visible
      await new Promise((r) => setTimeout(r, 350));
      setResult(analysis);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Analysis failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    setProgress(0);
  };

  return (
    <div className="min-h-screen bg-[#070b0f]">
      {/* Ambient green gradient */}
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_80%_45%_at_50%_-10%,rgba(34,197,94,0.12),transparent)]" />

      <div
        className={[
          "relative mx-auto px-4 py-12 pb-20 transition-[max-width] duration-500 ease-in-out",
          result ? "max-w-4xl" : "max-w-lg",
        ].join(" ")}
      >
        {/* Header */}
        <header className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-3 mb-3">
            <Dumbbell className="w-9 h-9 text-green-500" />
            <h1 className="text-5xl font-bold text-white tracking-tight">
              LiftLens
            </h1>
          </div>
          <p className="text-white/45 text-base tracking-wide">
            AI-powered exercise form analysis
          </p>
        </header>

        {/* Content area */}
        {loading ? (
          <div className="glass-card p-8 animate-fade-in max-w-md mx-auto">
            <LoadingOverlay progress={progress} />
          </div>
        ) : result ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Left column: Score + Feedback */}
            <div className="space-y-4">
              <AnimatedSection delay={0}>
                <ScoreBadge score={result.overallScore} />
              </AnimatedSection>

              {result.feedbackItems.length > 0 && (
                <AnimatedSection delay={200}>
                  <div className="glass-card p-5">
                    <h2 className="text-white/40 text-sm font-semibold uppercase tracking-widest mb-4">
                      Feedback
                    </h2>
                    <FeedbackList items={result.feedbackItems} />
                  </div>
                </AnimatedSection>
              )}
            </div>

            {/* Right column: Video + Meta + Reset */}
            <div className="space-y-4">
              {result.skeletonVideoPath && (
                <AnimatedSection delay={120}>
                  <div className="glass-card p-5">
                    <h2 className="text-white/40 text-sm font-semibold uppercase tracking-widest mb-4">
                      Skeleton Analysis
                    </h2>
                    <video
                      src={skeletonVideoUrl(result.id)}
                      controls
                      playsInline
                      className="w-full rounded-xl bg-black"
                    />
                  </div>
                </AnimatedSection>
              )}

              <AnimatedSection delay={280}>
                <div className="glass-card px-5 py-3.5 grid grid-cols-3 text-sm text-white/35">
                  <span className="capitalize">
                    {result.exerciseId.replace(/_/g, " ")}
                  </span>
                  <span className="capitalize text-center">
                    {result.muscleGroup}
                  </span>
                  <span className="text-right">
                    {new Date(result.createdAt).toLocaleString()}
                  </span>
                </div>
              </AnimatedSection>

              <AnimatedSection delay={400}>
                <button
                  onClick={reset}
                  className="w-full py-3.5 rounded-xl text-white/40 border border-white/10 hover:border-green-500/30 hover:text-white/75 transition-all duration-250 text-sm flex items-center justify-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Analyze another video
                </button>
              </AnimatedSection>
            </div>
          </div>
        ) : (
          <div className="glass-card p-6 animate-fade-in">
            <UploadZone onAnalyze={handleAnalyze} loading={loading} />
            {error && (
              <div className="mt-5 p-4 rounded-xl bg-red-500/10 border border-red-500/25 text-red-400 text-sm">
                {error}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
