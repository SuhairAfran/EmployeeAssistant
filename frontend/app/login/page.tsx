"use client";

import { useState } from "react";
import { useAuth } from "@/lib/AuthContext";
import { Sparkles, Activity, CheckCircle2, Mail, Lock, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

const QUICK_PICKS: { label: string; email: string; role: string }[] = [
  { label: "Rajesh Kumar (Admin · Agentic AI)", email: "admin.1@novigosolutions.com", role: "admin" },
  { label: "Amit Patel (Manager · Agentic AI)", email: "manager.1@novigosolutions.com", role: "manager" },
  { label: "Neha Reddy (HR Manager)", email: "manager.4@novigosolutions.com", role: "manager" },
  { label: "Vikram Singh (IT Manager)", email: "manager.3@novigosolutions.com", role: "manager" },
  { label: "Suresh Kumar (Employee · Agentic AI)", email: "emp.1@novigosolutions.com", role: "employee" },
  { label: "Anita Desai (Employee · Agentic AI)", email: "emp.2@novigosolutions.com", role: "employee" },
  { label: "Kavita Iyer (HR Team)", email: "hr.1@novigosolutions.com", role: "hr_team" },
  { label: "Arjun Mehta (IT Team)", email: "it.1@novigosolutions.com", role: "it_team" },
];

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState("emp.1@novigosolutions.com");
  const [password, setPassword] = useState("Password@123");
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    try {
      await login(email.trim(), password);
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : "Login failed");
    }
  };

  const displayError = localError || error;

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 font-sans text-zinc-100 overflow-hidden relative selection:bg-indigo-500/30 px-4 py-10">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md relative z-10"
      >
        <div className="bg-zinc-900/60 backdrop-blur-xl border border-zinc-800/50 rounded-3xl p-8 shadow-2xl">
          <div className="flex justify-center mb-5">
            <div className="h-14 w-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="text-white h-7 w-7" />
            </div>
          </div>

          <div className="text-center mb-7">
            <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-br from-white to-zinc-400 bg-clip-text text-transparent">
              Aura Copilot
            </h2>
            <p className="mt-2 text-sm text-zinc-400 font-medium">
              Sign in to your enterprise account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-xs font-semibold text-zinc-400 mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@novigosolutions.com"
                  className="w-full pl-10 pr-3 py-2.5 rounded-xl bg-zinc-800/60 border border-zinc-700/60 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-semibold text-zinc-400 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-3 py-2.5 rounded-xl bg-zinc-800/60 border border-zinc-700/60 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50"
                />
              </div>
            </div>

            {displayError && (
              <div className="flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/30 px-3 py-2 text-xs text-rose-300">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                <span>{displayError}</span>
              </div>
            )}

            <motion.button
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-semibold text-sm py-2.5 shadow-lg shadow-indigo-500/20 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </motion.button>
          </form>

          <div className="mt-6">
            <div className="text-[11px] uppercase tracking-wider text-zinc-500 font-semibold mb-2">
              Quick test accounts
            </div>
            <div className="grid grid-cols-1 gap-1.5 max-h-44 overflow-y-auto pr-1">
              {QUICK_PICKS.map((p) => (
                <button
                  key={p.email}
                  type="button"
                  onClick={() => {
                    setEmail(p.email);
                    setPassword("Password@123");
                  }}
                  className="text-left text-xs rounded-lg px-3 py-2 bg-zinc-800/40 border border-zinc-700/40 hover:bg-indigo-500/10 hover:border-indigo-500/40 transition-colors"
                >
                  <div className="font-medium text-zinc-200">{p.label}</div>
                  <div className="text-[11px] text-zinc-500">{p.email}</div>
                </button>
              ))}
            </div>
            <p className="mt-3 text-[11px] text-zinc-500">
              Default password for all seeded users: <span className="font-mono text-zinc-300">Password@123</span>
            </p>
          </div>

          <div className="mt-6 flex items-center justify-center gap-6 text-xs text-zinc-600 font-medium">
            <div className="flex items-center gap-1.5"><Activity className="h-3.5 w-3.5" /> All systems operational</div>
            <div className="flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5" /> End-to-end encrypted</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
