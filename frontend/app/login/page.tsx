"use client";

import { useAuth } from "@/lib/AuthContext";
import { UserCircle, ShieldAlert, Sparkles, Activity, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

export default function LoginPage() {
  const { login } = useAuth();

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 font-sans text-zinc-100 overflow-hidden relative selection:bg-indigo-500/30">
      
      {/* Background gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md relative z-10"
      >
        <div className="bg-zinc-900/60 backdrop-blur-xl border border-zinc-800/50 rounded-3xl p-10 shadow-2xl">
          <div className="flex justify-center mb-6">
            <div className="h-16 w-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="text-white h-8 w-8" />
            </div>
          </div>
          
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-br from-white to-zinc-400 bg-clip-text text-transparent">
              Aura Copilot
            </h2>
            <p className="mt-3 text-sm text-zinc-400 font-medium">
              Enterprise Agentic Intelligence
            </p>
          </div>

          <div className="space-y-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => login("employee")}
              className="group relative w-full overflow-hidden rounded-xl bg-zinc-800/50 border border-zinc-700/50 p-4 transition-all hover:bg-indigo-500/10 hover:border-indigo-500/50"
            >
              <div className="flex items-center gap-4">
                <div className="bg-indigo-500/20 p-2 rounded-lg group-hover:bg-indigo-500 transition-colors">
                  <UserCircle className="h-6 w-6 text-indigo-400 group-hover:text-white transition-colors" />
                </div>
                <div className="text-left">
                  <div className="text-sm font-semibold text-zinc-200">Continue as Employee</div>
                  <div className="text-xs text-zinc-500">Access HR, IT, and personal tools</div>
                </div>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => login("manager")}
              className="group relative w-full overflow-hidden rounded-xl bg-zinc-800/50 border border-zinc-700/50 p-4 transition-all hover:bg-emerald-500/10 hover:border-emerald-500/50"
            >
              <div className="flex items-center gap-4">
                <div className="bg-emerald-500/20 p-2 rounded-lg group-hover:bg-emerald-500 transition-colors">
                  <ShieldAlert className="h-6 w-6 text-emerald-400 group-hover:text-white transition-colors" />
                </div>
                <div className="text-left">
                  <div className="text-sm font-semibold text-zinc-200">Continue as Manager</div>
                  <div className="text-xs text-zinc-500">Review approvals and team insights</div>
                </div>
              </div>
            </motion.button>
          </div>
          
          <div className="mt-8 flex items-center justify-center gap-6 text-xs text-zinc-600 font-medium">
            <div className="flex items-center gap-1.5"><Activity className="h-3.5 w-3.5" /> All systems operational</div>
            <div className="flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5" /> End-to-end encrypted</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}