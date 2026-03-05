"use client";

import { useState, useLayoutEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import { Navbar } from "@/components/Navbar";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  // useLayoutEffect fires synchronously before paint — eliminates the 1-frame blank flash
  useLayoutEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    } else {
      setReady(true);
    }
  }, [router]);

  if (!ready) return null;

  return (
    <div className="min-h-screen bg-[#070b0f]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_80%_45%_at_50%_-10%,rgba(34,197,94,0.12),transparent)]" />
      <Navbar />
      <div className="pt-[72px]">
        {children}
      </div>
    </div>
  );
}
