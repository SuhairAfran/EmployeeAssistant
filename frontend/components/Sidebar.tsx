"use client";

import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { usePathname } from "next/navigation";
import { MessageSquare, CheckSquare, LogOut, Sparkles, User, Settings } from "lucide-react";
import { motion } from "framer-motion";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  if (!user) return null;

  const isManager = ["manager", "admin"].includes(user.role);

  return (
    <div className="flex h-screen w-72 flex-col border-r border-zinc-800/50 bg-zinc-950/80 backdrop-blur-xl px-4 py-6 z-20">
      <div className="mb-8 px-3 flex items-center gap-3">
        <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Sparkles className="text-white h-5 w-5" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight bg-gradient-to-br from-white to-zinc-400 bg-clip-text text-transparent">
            Aura
          </h1>
          <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold">Workspace</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1.5 px-1">
        <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-3">Menu</div>
        
        <Link href="/chat">
          <div className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-200 ${
            pathname === "/chat" 
              ? "bg-indigo-500/10 text-indigo-300 font-medium" 
              : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
          }`}>
            {pathname === "/chat" && (
              <motion.div layoutId="sidebar-active" className="absolute left-0 w-1 h-6 bg-indigo-500 rounded-r-full" />
            )}
            <MessageSquare className={`h-5 w-5 ${pathname === "/chat" ? "text-indigo-400" : "text-zinc-500 group-hover:text-zinc-300"}`} />
            Copilot Chat
          </div>
        </Link>

        {isManager && (
          <Link href="/approvals">
            <div className={`group relative flex items-center justify-between rounded-xl px-3 py-2.5 transition-all duration-200 ${
              pathname === "/approvals" 
                ? "bg-emerald-500/10 text-emerald-300 font-medium" 
                : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
            }`}>
              {pathname === "/approvals" && (
                <motion.div layoutId="sidebar-active" className="absolute left-0 w-1 h-6 bg-emerald-500 rounded-r-full" />
              )}
              <div className="flex items-center gap-3">
                <CheckSquare className={`h-5 w-5 ${pathname === "/approvals" ? "text-emerald-400" : "text-zinc-500 group-hover:text-zinc-300"}`} />
                Approvals
              </div>
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-[10px] font-bold text-emerald-400">
                2
              </span>
            </div>
          </Link>
        )}
        
        <div className="pt-4 mt-2 border-t border-zinc-800/50">
          <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3 px-3">Support</div>
          <button className="w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200 transition-colors">
            <Settings className="h-5 w-5 text-zinc-500" />
            Settings
          </button>
        </div>
      </nav>

      <div className="mt-auto border border-zinc-800/80 bg-zinc-900/50 rounded-2xl p-3">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-9 w-9 bg-zinc-800 rounded-full flex items-center justify-center border border-zinc-700">
            <User className="h-4 w-4 text-zinc-400" />
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="text-sm font-semibold text-zinc-200 truncate">{user.name}</div>
            <div className="text-xs text-zinc-500 truncate capitalize">{user.role}</div>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-zinc-800/80 py-2 text-xs font-medium text-zinc-300 hover:bg-red-500/10 hover:text-red-400 transition-colors border border-transparent hover:border-red-500/20"
        >
          <LogOut className="h-3.5 w-3.5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}