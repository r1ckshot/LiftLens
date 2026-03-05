"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Dumbbell, Zap, Brain, BarChart3 } from "lucide-react";
import { isAuthenticated } from "@/lib/auth";

const features = [
  {
    icon: Brain,
    title: "12 exercises",
    desc: "Squat, deadlift, bench press, pull-up, row & more",
  },
  {
    icon: Zap,
    title: "Pose estimation",
    desc: "Skeleton overlay rendered frame-by-frame on your video",
  },
  {
    icon: BarChart3,
    title: "Per-aspect scoring",
    desc: "Depth, back angle, bar path and other key metrics graded",
  },
];

export default function LandingPage() {
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) router.replace("/analyze");
  }, [router]);

  return (
    <div className="min-h-screen bg-[#070b0f]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_90%_55%_at_50%_-5%,rgba(34,197,94,0.15),transparent)]" />
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_40%_30%_at_80%_80%,rgba(34,197,94,0.04),transparent)]" />

      <div className="relative flex min-h-screen flex-col items-center justify-center px-4 text-center">
        {/* Pulsing badge */}
        <div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-sm font-medium mb-8 animate-fade-in"
          style={{ animationFillMode: "both" }}
        >
          <span className="relative flex w-2 h-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-60" />
            <span className="relative inline-flex rounded-full w-2 h-2 bg-green-400" />
          </span>
          AI-powered form analysis
        </div>

        {/* Logo + title */}
        <div
          className="inline-flex items-center gap-4 mb-5 animate-fade-in"
          style={{ animationDelay: "80ms", animationFillMode: "both" }}
        >
          <Dumbbell className="w-12 h-12 text-green-500" />
          <h1 className="text-6xl sm:text-7xl font-bold text-white tracking-tight">
            LiftLens
          </h1>
        </div>

        {/* Tagline */}
        <p
          className="text-white/50 text-lg sm:text-xl mb-12 max-w-md leading-relaxed animate-fade-in"
          style={{ animationDelay: "160ms", animationFillMode: "both" }}
        >
          Upload your workout video and get detailed form feedback powered by computer vision.
        </p>

        {/* Feature cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12 max-w-3xl w-full">
          {features.map(({ icon: Icon, title, desc }, i) => (
            <div
              key={title}
              className="bg-white/5 border border-transparent hover:border-green-500/25 rounded-2xl px-5 py-5 text-left transition-all duration-300 hover:scale-[1.03] hover:bg-white/[0.07] animate-fade-in cursor-default"
              style={{
                animationDelay: `${240 + i * 120}ms`,
                animationFillMode: "both",
              }}
            >
              <Icon className="w-6 h-6 text-green-500 mb-3" />
              <p className="text-white/85 text-sm font-semibold mb-1.5">{title}</p>
              <p className="text-white/40 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>

        {/* CTAs */}
        <div
          className="flex items-center gap-4 animate-fade-in"
          style={{ animationDelay: "600ms", animationFillMode: "both" }}
        >
          <Link
            href="/register"
            className="px-8 py-4 rounded-xl bg-green-500 hover:bg-green-400 active:scale-[0.97] hover:scale-[1.02] text-black font-bold text-base transition-all duration-200 shadow-lg shadow-green-500/20 hover:shadow-green-500/35"
          >
            Get started
          </Link>
          <Link
            href="/login"
            className="px-8 py-4 rounded-xl border border-white/15 text-white/60 hover:text-white/90 hover:border-white/35 hover:scale-[1.02] active:scale-[0.97] text-base transition-all duration-200"
          >
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
