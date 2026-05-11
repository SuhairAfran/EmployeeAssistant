"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CalendarDays,
  Inbox,
  Laptop,
  Receipt,
  Check,
  X,
  RefreshCw,
} from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import { api, EntityType, PendingItem } from "@/lib/api";

type Filter = "all" | EntityType;

const ICONS: Record<EntityType, React.ComponentType<{ className?: string }>> = {
  leave: CalendarDays,
  asset: Laptop,
  reimbursement: Receipt,
};

export default function ApprovalsPage() {
  const { user, token } = useAuth();
  const [items, setItems] = useState<PendingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [noteDraft, setNoteDraft] = useState<Record<string, string>>({});

  const isManager =
    user?.role === "manager" || user?.role === "admin" || user?.role === "hr_team";

  const load = async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.pendingApprovals(token);
      setItems(res.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load approvals");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isManager) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isManager, token]);

  const filtered = useMemo(
    () => (filter === "all" ? items : items.filter((i) => i.entity_type === filter)),
    [items, filter],
  );

  const counts = useMemo(() => {
    const c = { leave: 0, asset: 0, reimbursement: 0 };
    items.forEach((it) => (c[it.entity_type] += 1));
    return c;
  }, [items]);

  const decide = async (
    item: PendingItem,
    decision: "approve" | "reject",
  ) => {
    if (!token) return;
    setBusyId(item.entity_id);
    try {
      await api.decideApproval(
        item.entity_type,
        item.entity_id,
        decision,
        noteDraft[item.entity_id] || "",
        token,
      );
      // Optimistically remove the item from the list
      setItems((prev) =>
        prev.filter((i) => i.entity_id !== item.entity_id),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Decision failed");
    } finally {
      setBusyId(null);
    }
  };

  if (!user) return null;

  if (!isManager) {
    return (
      <div className="flex-1 flex items-center justify-center p-10">
        <div className="text-center max-w-sm">
          <Inbox className="h-10 w-10 mx-auto text-zinc-600 mb-3" />
          <h2 className="text-lg font-semibold text-zinc-200">
            Approvals are for managers only
          </h2>
          <p className="text-sm text-zinc-500 mt-1">
            Once you become a reporting manager, your direct reports&apos; pending
            requests will show up here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-6 md:px-10 py-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">Approvals</h1>
            <p className="text-sm text-zinc-400 mt-0.5">
              Pending requests from your direct reports.
            </p>
          </div>
          <button
            onClick={load}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-800/60 border border-zinc-700/60 hover:bg-zinc-800 transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </header>

        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <FilterChip
            active={filter === "all"}
            label={`All · ${items.length}`}
            onClick={() => setFilter("all")}
          />
          <FilterChip
            active={filter === "leave"}
            label={`Leave · ${counts.leave}`}
            onClick={() => setFilter("leave")}
          />
          <FilterChip
            active={filter === "asset"}
            label={`Asset · ${counts.asset}`}
            onClick={() => setFilter("asset")}
          />
          {counts.reimbursement > 0 && (
            <FilterChip
              active={filter === "reimbursement"}
              label={`Reimbursement · ${counts.reimbursement}`}
              onClick={() => setFilter("reimbursement")}
            />
          )}
        </div>

        {loading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-32 rounded-2xl bg-zinc-900/40 border border-zinc-800/60 animate-pulse"
              />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="rounded-2xl border border-zinc-800/60 bg-zinc-900/40 p-12 text-center">
            <Inbox className="h-10 w-10 mx-auto text-zinc-600 mb-3" />
            <h3 className="text-zinc-200 font-medium">All caught up</h3>
            <p className="text-sm text-zinc-500 mt-1">
              You have no pending approvals at this time.
            </p>
          </div>
        ) : (
          <ul className="space-y-3">
            {filtered.map((item) => {
              const Icon = ICONS[item.entity_type];
              const busy = busyId === item.entity_id;
              return (
                <li
                  key={item.entity_id}
                  className="rounded-2xl border border-zinc-800/60 bg-zinc-900/50 p-5 backdrop-blur-sm"
                >
                  <div className="flex items-start gap-4">
                    <div className="h-10 w-10 rounded-xl bg-indigo-500/15 text-indigo-300 flex items-center justify-center flex-shrink-0">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-semibold text-zinc-100">
                          {item.employee_name}
                        </span>
                        {item.employee_designation && (
                          <span className="text-[11px] text-zinc-500">
                            · {item.employee_designation}
                          </span>
                        )}
                        <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-md bg-zinc-800 border border-zinc-700 text-zinc-400">
                          {item.entity_type}
                        </span>
                      </div>
                      <RequestSummary item={item} />
                      <div className="text-[11px] text-zinc-500">
                        Submitted{" "}
                        {new Date(item.submitted_at).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-col sm:flex-row gap-3">
                    <input
                      type="text"
                      placeholder="Optional note for the employee…"
                      value={noteDraft[item.entity_id] || ""}
                      onChange={(e) =>
                        setNoteDraft((prev) => ({
                          ...prev,
                          [item.entity_id]: e.target.value,
                        }))
                      }
                      className="flex-1 bg-zinc-950/40 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500/60"
                      disabled={busy}
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => decide(item, "reject")}
                        disabled={busy}
                        className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold text-rose-200 bg-rose-500/10 border border-rose-500/30 hover:bg-rose-500/20 transition-colors disabled:opacity-50"
                      >
                        <X className="h-3.5 w-3.5" /> Reject
                      </button>
                      <button
                        onClick={() => decide(item, "approve")}
                        disabled={busy}
                        className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold text-emerald-200 bg-emerald-500/15 border border-emerald-500/30 hover:bg-emerald-500/25 transition-colors disabled:opacity-50"
                      >
                        <Check className="h-3.5 w-3.5" /> Approve
                      </button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}

function FilterChip({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
        active
          ? "bg-indigo-500/20 text-indigo-200 border-indigo-500/40"
          : "bg-zinc-900/40 text-zinc-400 border-zinc-800 hover:bg-zinc-800/60"
      }`}
    >
      {label}
    </button>
  );
}

function RequestSummary({ item }: { item: PendingItem }) {
  if (item.entity_type === "leave") {
    return (
      <div className="text-sm text-zinc-300">
        <span className="capitalize font-medium">{item.leave_type}</span> leave —{" "}
        <span className="text-zinc-200">
          {item.start_date} → {item.end_date}
        </span>{" "}
        ({item.business_days} business days)
        {item.reason && (
          <div className="text-[12px] text-zinc-500 mt-0.5">
            Reason: {item.reason}
          </div>
        )}
      </div>
    );
  }
  if (item.entity_type === "asset") {
    return (
      <div className="text-sm text-zinc-300">
        Asset request —{" "}
        <span className="capitalize font-medium">
          {item.asset_type?.replace("_", " ")}
        </span>
        {item.justification && (
          <div className="text-[12px] text-zinc-500 mt-0.5">
            {item.justification}
          </div>
        )}
      </div>
    );
  }
  if (item.entity_type === "reimbursement") {
    return (
      <div className="text-sm text-zinc-300">
        Reimbursement {item.claim_no} — {item.currency || "INR"}{" "}
        {item.amount?.toFixed(2)}
        {item.description && (
          <div className="text-[12px] text-zinc-500 mt-0.5">
            {item.description}
          </div>
        )}
      </div>
    );
  }
  return null;
}
