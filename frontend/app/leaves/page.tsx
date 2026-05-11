"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CalendarDays, MessageSquare, RefreshCw } from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import { api, LeaveBalanceItem, LeaveHistoryItem } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

export default function LeavesPage() {
  const { user, token } = useAuth();
  const [balances, setBalances] = useState<LeaveBalanceItem[]>([]);
  const [history, setHistory] = useState<LeaveHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [b, h] = await Promise.all([
        api.myLeaveBalance(token).catch(() => []),
        api.myLeaveHistory(token, 100).catch(() => []),
      ]);
      setBalances(b);
      setHistory(h);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  if (!user) return null;

  return (
    <div className="flex-1 overflow-y-auto px-6 md:px-10 py-8">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">My Leaves</h1>
            <p className="text-sm text-zinc-400 mt-0.5">
              Balances and request history for {new Date().getFullYear()}.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={load}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-800/60 border border-zinc-700/60 hover:bg-zinc-800 transition-colors"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <Link
              href="/chat"
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 transition-colors"
            >
              <MessageSquare className="h-3.5 w-3.5" />
              Apply via chat
            </Link>
          </div>
        </header>

        {/* Balances */}
        <section>
          <h2 className="text-sm font-semibold text-zinc-200 mb-3">
            Available balances
          </h2>
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="h-28 rounded-2xl bg-zinc-900/40 border border-zinc-800/60 animate-pulse"
                />
              ))}
            </div>
          ) : balances.length === 0 ? (
            <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-8 text-center text-sm text-zinc-500">
              No leave balances configured for the current year.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {balances.map((b) => (
                <div
                  key={b.leave_type}
                  className="rounded-2xl border border-zinc-800/70 bg-zinc-900/50 p-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="text-[11px] uppercase tracking-wider text-zinc-500 font-semibold capitalize">
                      {b.leave_type}
                    </div>
                    <CalendarDays className="h-3.5 w-3.5 text-zinc-600" />
                  </div>
                  <div className="text-3xl font-bold text-zinc-100 mt-1">
                    {b.available_days.toFixed(1)}
                    <span className="text-sm font-medium text-zinc-500 ml-1">
                      days
                    </span>
                  </div>
                  <div className="mt-2 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                    <div
                      className="h-full bg-indigo-500"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(
                            0,
                            (b.used_days /
                              Math.max(b.entitled_days + b.carried_over, 1)) *
                              100,
                          ),
                        )}%`,
                      }}
                    />
                  </div>
                  <div className="text-[11px] text-zinc-500 mt-1.5">
                    {b.used_days} used · {b.pending_days} pending · entitled{" "}
                    {b.entitled_days}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* History */}
        <section>
          <h2 className="text-sm font-semibold text-zinc-200 mb-3">
            Request history
          </h2>
          {loading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div
                  key={i}
                  className="h-12 rounded-xl bg-zinc-900/40 animate-pulse"
                />
              ))}
            </div>
          ) : history.length === 0 ? (
            <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-8 text-center text-sm text-zinc-500">
              You haven&apos;t applied for any leave yet.
            </div>
          ) : (
            <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-zinc-900/60 text-zinc-400 text-[11px] uppercase tracking-wider">
                  <tr>
                    <th className="text-left font-semibold px-4 py-3">Type</th>
                    <th className="text-left font-semibold px-4 py-3">Dates</th>
                    <th className="text-left font-semibold px-4 py-3">Days</th>
                    <th className="text-left font-semibold px-4 py-3">Reason</th>
                    <th className="text-left font-semibold px-4 py-3">Status</th>
                    <th className="text-left font-semibold px-4 py-3">Applied</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {history.map((h) => (
                    <tr key={h.id} className="hover:bg-zinc-800/30">
                      <td className="px-4 py-3 capitalize text-zinc-200">
                        {h.leave_type}
                      </td>
                      <td className="px-4 py-3 text-zinc-300 whitespace-nowrap">
                        {h.start_date} → {h.end_date}
                      </td>
                      <td className="px-4 py-3 text-zinc-300">
                        {h.business_days}
                      </td>
                      <td className="px-4 py-3 text-zinc-400 max-w-[18rem] truncate">
                        {h.reason || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={h.status} />
                      </td>
                      <td className="px-4 py-3 text-zinc-500 text-[11px] whitespace-nowrap">
                        {new Date(h.applied_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
