"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Dumbbell } from "lucide-react";
import { login } from "@/lib/api";
import { setToken } from "@/lib/auth";

function FadeIn({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <div
      className="animate-fade-in"
      style={{ animationDelay: `${delay}ms`, animationFillMode: "both" }}
    >
      {children}
    </div>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [errorKey, setErrorKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(false);

  const validate = (): boolean => {
    let valid = true;
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setEmailError("Invalid email");
      valid = false;
    } else {
      setEmailError(null);
    }
    if (password.length < 6) {
      setPasswordError("Min. 6 characters");
      valid = false;
    } else {
      setPasswordError(null);
    }
    return valid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await login(email, password);
      setToken(res.token, res.email);
      router.push("/analyze");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
      setErrorKey((k) => k + 1);
      setCooldown(true);
      setTimeout(() => setCooldown(false), 1500);
      setTimeout(() => setError(null), 2000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md">
        <FadeIn delay={0}>
          <div className="text-center mb-10">
            <Link
              href="/"
              className="inline-flex items-center gap-3 mb-3 hover:opacity-80 transition-opacity"
            >
              <Dumbbell className="w-9 h-9 text-green-500" />
              <span className="text-4xl font-bold text-white tracking-tight">LiftLens</span>
            </Link>
            <p className="text-white/40">Sign in to your account</p>
          </div>
        </FadeIn>

        <FadeIn delay={100}>
          <div className="glass-card p-8 relative overflow-hidden">
            {error && (
              <div key={errorKey} className="absolute inset-0 z-10 flex items-center justify-center rounded-[inherit] backdrop-blur-sm bg-black/50 animate-error-overlay">
                <p className="text-red-400 text-base font-medium px-8 text-center">{error}</p>
              </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-white/50 text-xs font-medium uppercase tracking-widest">Email</label>
                  <span className={`text-xs transition-opacity duration-200 ${emailError ? "text-red-400" : "opacity-0 pointer-events-none"}`}>
                    {emailError ?? "·"}
                  </span>
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setEmailError(null); }}
                  className={[
                    "w-full rounded-xl bg-white/5 border px-4 py-3.5 text-white placeholder-white/20 focus:outline-none transition-colors",
                    emailError ? "border-red-500/50 focus:border-red-500/70" : "border-white/10 focus:border-green-500/50",
                  ].join(" ")}
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-white/50 text-xs font-medium uppercase tracking-widest">Password</label>
                  <span className={`text-xs transition-opacity duration-200 ${passwordError ? "text-red-400" : "opacity-0 pointer-events-none"}`}>
                    {passwordError ?? "·"}
                  </span>
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setPasswordError(null); }}
                  className={[
                    "w-full rounded-xl bg-white/5 border px-4 py-3.5 text-white placeholder-white/20 focus:outline-none transition-colors",
                    passwordError ? "border-red-500/50 focus:border-red-500/70" : "border-white/10 focus:border-green-500/50",
                  ].join(" ")}
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading || cooldown}
                className="w-full py-3.5 rounded-xl bg-green-500 hover:bg-green-400 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold transition-all duration-200 mt-2 shadow-lg shadow-green-500/15 hover:shadow-green-500/30"
              >
                {loading ? "Signing in…" : "Sign in"}
              </button>
            </form>
          </div>
        </FadeIn>

        <FadeIn delay={200}>
          <p className="mt-5 text-center text-white/35">
            No account?{" "}
            <Link href="/register" className="text-green-500 hover:text-green-400 transition-colors">
              Create one
            </Link>
          </p>
        </FadeIn>
      </div>
    </div>
  );
}
