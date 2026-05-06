"use client";

import { useAuth } from "@/lib/AuthContext";
import Sidebar from "./Sidebar";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted && !user && pathname !== "/login") {
      router.push("/login");
    }
  }, [user, pathname, router, isMounted]);

  // Don't render until mounted to avoid hydration mismatch
  if (!isMounted) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center">Loading...</div>;

  if (!user || pathname === "/login") {
    return <main className="flex-1">{children}</main>;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-950 text-zinc-100 font-sans selection:bg-indigo-500/30">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-zinc-950 to-zinc-950 z-0"></div>
        <div className="relative z-10 flex flex-col h-full">{children}</div>
      </main>
    </div>
  );
}
