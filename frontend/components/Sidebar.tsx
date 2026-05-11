"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  MessageSquare,
  CalendarDays,
  Wrench,
  Receipt,
  Inbox,
  LogOut,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import { api } from "@/lib/api";

type NavItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
  managerOnly?: boolean;
};

export default function Sidebar() {
  const { user, token, logout } = useAuth();
  const pathname = usePathname();
  const [pendingCount, setPendingCount] = useState(0);

  const isManager =
    user?.role === "manager" || user?.role === "admin" || user?.role === "hr_team";

  // Poll the pending-approvals badge every 30 s for managers.
  useEffect(() => {
    if (!isManager || !token) {
      setPendingCount(0);
      return;
    }

    let cancelled = false;
    const tick = async () => {
      try {
        const res = await api.pendingApprovalsCount(token);
        if (!cancelled) setPendingCount(res.count);
      } catch {
        // ignore — keep last known value
      }
    };
    tick();
    const id = setInterval(tick, 30_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [isManager, token]);

  if (!user) return null;

  const items: NavItem[] = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/chat", label: "Chat", icon: MessageSquare },
    { href: "/leaves", label: "My Leaves", icon: CalendarDays },
    { href: "/tickets", label: "IT Tickets", icon: Wrench },
    { href: "/claims", label: "Reimbursements", icon: Receipt },
    {
      href: "/approvals",
      label: "Approvals",
      icon: Inbox,
      badge: pendingCount,
      managerOnly: true,
    },
  ];

  const visible = items.filter((it) => !it.managerOnly || isManager);

  const initials = (user.full_name || "User")
    .split(/\s+/)
    .map((p) => p[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <aside className="hidden md:flex w-64 flex-shrink-0 flex-col bg-zinc-900/60 backdrop-blur-xl border-r border-zinc-800/60">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-zinc-800/60 flex items-center gap-2.5">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-900/40">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-sm font-semibold text-zinc-100">Aura</span>
          <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-medium">
            Enterprise Copilot
          </span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        {visible.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                active
                  ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/20"
                  : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60 border border-transparent"
              }`}
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              <span className="flex-1 truncate">{item.label}</span>
              {typeof item.badge === "number" && item.badge > 0 && (
                <span className="ml-auto inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 rounded-full text-[10px] font-bold bg-amber-500 text-zinc-950">
                  {item.badge > 99 ? "99+" : item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User card */}
      <div className="px-3 py-4 border-t border-zinc-800/60">
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl">
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-800 border border-zinc-600 flex items-center justify-center text-xs font-semibold text-zinc-200">
            {initials || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-zinc-100 truncate">
              {user.full_name || "User"}
            </div>
            <div className="text-[11px] text-zinc-500 truncate capitalize">
              {user.role?.replace("_", " ") || ""}
            </div>
          </div>
          <button
            onClick={logout}
            className="p-2 rounded-lg text-zinc-500 hover:text-zinc-100 hover:bg-zinc-800/80 transition-colors"
            title="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
