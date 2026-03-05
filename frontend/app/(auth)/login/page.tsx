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
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    let valid = true;
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setEmailError("Enter a valid email address.");
      valid = false;
    } else {
      setEmailError(null);
    }
    if (password.length < 6) {
      setPasswordError("Password must be at least 6 characters.");
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
          <div className="glass-card p-8">
            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div>
                <label className="block text-white/50 text-xs font-medium uppercase tracking-widest mb-2">
                  Email
                </label>
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
                {emailError && <p className="mt-1.5 text-red-400 text-xs">{emailError}</p>}
              </div>

              <div>
                <label className="block text-white/50 text-xs font-medium uppercase tracking-widest mb-2">
                  Password
                </label>
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
                {passwordError && <p className="mt-1.5 text-red-400 text-xs">{passwordError}</p>}
              </div>

              {error && (
                <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/25 text-red-400 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
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
