"use client";

import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Dumbbell, History, LogOut, Activity } from "lucide-react";
import { clearToken, getEmail } from "@/lib/auth";

export function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const email = getEmail();

  const logout = () => {
    clearToken();
    router.push("/login");
  };

  return (
    <header className="fixed top-3 inset-x-0 z-50 flex justify-center px-4 animate-slide-down">
      <nav className="w-full max-w-4xl bg-[#070b0f]/90 backdrop-blur-md border border-white/10 rounded-2xl h-12 flex items-center justify-between px-5">
        <Link href="/analyze" className="flex items-center gap-2 text-white/80 hover:text-white transition-colors">
          <Dumbbell className="w-4.5 h-4.5 text-green-500" />
          <span className="font-semibold tracking-tight text-[0.9rem]">LiftLens</span>
        </Link>

        <div className="flex items-center gap-1">
          <Link
            href="/analyze"
            className={[
              "px-3 py-1.5 rounded-xl text-[0.82rem] flex items-center gap-1.5 transition-all duration-200",
              pathname === "/analyze" ? "text-white bg-white/8" : "text-white/50 hover:text-white/80 hover:bg-white/5",
            ].join(" ")}
          >
            <Activity className="w-3.5 h-3.5" />
            Analyze
          </Link>

          <span className="text-green-500 text-[0.78rem] px-3 hidden sm:block truncate max-w-[160px]">{email}</span>

          <Link
            href="/history"
            className={[
              "px-3 py-1.5 rounded-xl text-[0.82rem] flex items-center gap-1.5 transition-all duration-200",
              pathname.startsWith("/history") ? "text-white bg-white/8" : "text-white/50 hover:text-white/80 hover:bg-white/5",
            ].join(" ")}
          >
            <History className="w-3.5 h-3.5" />
            History
          </Link>
        </div>

        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-[0.82rem] text-white/35 hover:text-red-400/70 transition-colors duration-200"
        >
          <LogOut className="w-3.5 h-3.5" />
          Logout
        </button>
      </nav>
    </header>
  );
}
