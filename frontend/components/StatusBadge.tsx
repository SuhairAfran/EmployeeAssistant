import React from "react";

const PALETTE: Record<string, string> = {
  // approvals
  pending: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  submitted: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  under_review: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  manager_approved: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  it_approved: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  approved: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  fulfilled: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  paid: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  resolved: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  closed: "bg-zinc-500/15 text-zinc-300 border-zinc-500/30",
  rejected: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  cancelled: "bg-zinc-500/15 text-zinc-300 border-zinc-500/30",
  draft: "bg-zinc-500/15 text-zinc-300 border-zinc-500/30",
  // tickets
  open: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  in_progress: "bg-indigo-500/15 text-indigo-300 border-indigo-500/30",
  on_hold: "bg-zinc-500/15 text-zinc-300 border-zinc-500/30",
};

export default function StatusBadge({ status }: { status: string }) {
  const cls = PALETTE[status] ?? "bg-zinc-700/40 text-zinc-300 border-zinc-600/40";
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium border ${cls}`}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}
