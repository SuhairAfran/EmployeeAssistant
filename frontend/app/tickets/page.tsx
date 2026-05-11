"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Wrench, MessageSquare, RefreshCw } from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import { api, ITTicketItem } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

type View = "open" | "all";

export default function TicketsPage() {
  const { user, token } = useAuth();
  const [tickets, setTickets] = useState<ITTicketItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>("open");

  const load = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const t = await api.myITTickets(token, 200).catch(() => []);
      setTickets(t);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const filtered = useMemo(() => {
    if (view === "all") return tickets;
    return tickets.filter(
      (t) => !["resolved", "closed"].includes(t.status),
    );
  }, [tickets, view]);

  const openCount = tickets.filter(
    (t) => !["resolved", "closed"].includes(t.status),
  ).length;

  if (!user) return null;

  return (
    <div className="flex-1 overflow-y-auto px-6 md:px-10 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">IT Tickets</h1>
            <p className="text-sm text-zinc-400 mt-0.5">
              Tickets you&apos;ve raised with the IT helpdesk.
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
              Raise via chat
            </Link>
          </div>
        </header>

        <div className="flex gap-2">
          <button
            onClick={() => setView("open")}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              view === "open"
                ? "bg-indigo-500/20 text-indigo-200 border-indigo-500/40"
                : "bg-zinc-900/40 text-zinc-400 border-zinc-800 hover:bg-zinc-800/60"
            }`}
          >
            Open · {openCount}
          </button>
          <button
            onClick={() => setView("all")}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              view === "all"
                ? "bg-indigo-500/20 text-indigo-200 border-indigo-500/40"
                : "bg-zinc-900/40 text-zinc-400 border-zinc-800 hover:bg-zinc-800/60"
            }`}
          >
            All · {tickets.length}
          </button>
        </div>

        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="h-20 rounded-2xl bg-zinc-900/40 border border-zinc-800/60 animate-pulse"
              />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-12 text-center">
            <Wrench className="h-10 w-10 mx-auto text-zinc-600 mb-3" />
            <h3 className="text-zinc-200 font-medium">No tickets here</h3>
            <p className="text-sm text-zinc-500 mt-1">
              {view === "open"
                ? "You have no open tickets right now."
                : "You haven't raised any IT tickets yet."}
            </p>
          </div>
        ) : (
          <ul className="space-y-2">
            {filtered.map((t) => (
              <li
                key={t.id}
                className="rounded-2xl border border-zinc-800/70 bg-zinc-900/50 p-4 backdrop-blur-sm"
              >
                <div className="flex items-start gap-4">
                  <div className="h-9 w-9 rounded-xl bg-amber-500/15 text-amber-300 flex items-center justify-center flex-shrink-0">
                    <Wrench className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-mono text-zinc-500">
                        {t.ticket_no}
                      </span>
                      <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-md bg-zinc-800 border border-zinc-700 text-zinc-400 capitalize">
                        {t.category.replace("_", " ")}
                      </span>
                      <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-md bg-zinc-800 border border-zinc-700 text-zinc-400 capitalize">
                        {t.priority}
                      </span>
                    </div>
                    <div className="text-sm text-zinc-100 font-medium mt-1">
                      {t.subject}
                    </div>
                    {t.resolution && (
                      <div className="text-[12px] text-zinc-400 mt-1">
                        <span className="text-emerald-400 font-medium">
                          Resolution:
                        </span>{" "}
                        {t.resolution}
                      </div>
                    )}
                    <div className="text-[11px] text-zinc-500 mt-1">
                      Raised {new Date(t.created_at).toLocaleString()}
                    </div>
                  </div>
                  <StatusBadge status={t.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
