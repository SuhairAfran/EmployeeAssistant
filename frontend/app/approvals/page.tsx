// app/approvals/page.tsx
"use client";

import { useState } from "react";
import { useAuth } from "@/lib/AuthContext";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { ShieldCheck, Check, X, AlertCircle, Hash, Search } from "lucide-react";
import { motion } from "framer-motion";

export default function ApprovalsPage() {
  const { user } = useAuth();
  const router = useRouter();
  
  const [sessionId, setSessionId] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Security redirect
  if (user && user.role === "employee") {
    router.push("/chat");
    return null;
  }

  const handleDecision = async (decision: "approved" | "rejected") => {
    if (!sessionId.trim()) {
      setStatus({ type: "error", msg: "Please enter a valid Session ID." });
      return;
    }

    setIsLoading(true);
    setStatus(null);

    try {
      const result = await api.approve(sessionId, decision, note, user!.role);
      setStatus({ 
        type: "success", 
        msg: `Success! The workflow was ${decision}. Final response: "${result.final_response}"` 
      });
      setSessionId("");
      setNote("");
    } catch (error) {
      setStatus({ type: "error", msg: "Failed to resume workflow. Ensure the Session ID is correct and currently paused." });
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950/50 p-8 md:p-12 relative">
      <div className="max-w-3xl mx-auto w-full relative z-10">
        
        <div className="mb-10 flex items-center gap-4">
          <div className="h-12 w-12 bg-emerald-500/20 rounded-2xl flex items-center justify-center border border-emerald-500/30 shadow-lg shadow-emerald-500/10">
            <ShieldCheck className="h-6 w-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-1">Pending Approvals</h1>
            <p className="text-sm text-zinc-400 font-medium">
              Review and manage paused workflow requests from your team.
            </p>
          </div>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-zinc-900/60 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-zinc-800/50"
        >
          <div className="space-y-6">
            <div>
              <label className="flex items-center gap-2 text-sm font-semibold text-zinc-300 mb-2">
                <Hash className="h-4 w-4 text-zinc-500" /> Workflow Session ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={sessionId}
                  onChange={(e) => setSessionId(e.target.value)}
                  placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000"
                  className="w-full rounded-xl bg-zinc-950 border border-zinc-800 p-4 pl-12 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 text-zinc-100 placeholder-zinc-600 transition-all font-mono text-sm"
                />
                <Search className="absolute left-4 top-4 h-5 w-5 text-zinc-500" />
              </div>
              <p className="text-xs text-zinc-500 mt-2 font-medium">Find this in the chat UI or automated alert email.</p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-zinc-300 mb-2">
                Manager Notes (Optional)
              </label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add reasoning for your decision (will be sent back to the workflow)..."
                className="w-full rounded-xl bg-zinc-950 border border-zinc-800 p-4 focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 text-zinc-100 placeholder-zinc-600 transition-all min-h-[120px] resize-none"
              />
            </div>

            {status && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`p-4 rounded-xl text-sm font-medium flex items-start gap-3 ${
                  status.type === "success" 
                    ? "bg-emerald-500/10 text-emerald-200 border border-emerald-500/30" 
                    : "bg-red-500/10 text-red-200 border border-red-500/30"
                }`}
              >
                {status.type === "success" ? (
                  <Check className="h-5 w-5 text-emerald-400 flex-shrink-0" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                )}
                <div>{status.msg}</div>
              </motion.div>
            )}

            <div className="flex gap-4 pt-6 border-t border-zinc-800/50">
              <button
                onClick={() => handleDecision("approved")}
                disabled={isLoading || !sessionId.trim()}
                className="flex-1 flex items-center justify-center gap-2 bg-emerald-600/90 text-white py-3.5 rounded-xl font-semibold hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-emerald-600/90 transition-all shadow-lg shadow-emerald-900/20 active:scale-[0.98]"
              >
                <Check className="h-5 w-5" />
                {isLoading ? "Processing..." : "Approve Request"}
              </button>
              <button
                onClick={() => handleDecision("rejected")}
                disabled={isLoading || !sessionId.trim()}
                className="flex-1 flex items-center justify-center gap-2 bg-zinc-800 text-white py-3.5 rounded-xl font-semibold hover:bg-red-600/90 disabled:opacity-50 disabled:hover:bg-zinc-800 transition-all active:scale-[0.98] border border-zinc-700/50 hover:border-red-500/50"
              >
                <X className="h-5 w-5" />
                {isLoading ? "Processing..." : "Reject Request"}
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}