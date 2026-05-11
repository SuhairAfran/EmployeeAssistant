"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  CalendarDays,
  Wrench,
  Users,
  Inbox,
  ArrowRight,
  Sparkles,
  MessageSquare,
} from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import {
  api,
  ActivityItem,
  ITTicketItem,
  LeaveBalanceItem,
  TeamLeaveTodayItem,
} from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

export default function DashboardPage() {
  const { user, token } = useAuth();
  const [balances, setBalances] = useState<LeaveBalanceItem[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [openTickets, setOpenTickets] = useState<ITTicketItem[]>([]);
  const [team, setTeam] = useState<TeamLeaveTodayItem[]>([]);
  const [pendingCount, setPendingCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  const isManager =
    user?.role === "manager" || user?.role === "admin" || user?.role === "hr_team";

  useEffect(() => {
    if (!user || !token) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const [bal, act, tix, tm, pc] = await Promise.all([
          api.myLeaveBalance(token).catch(() => []),
          api.recentActivity(token, 6).catch(() => []),
          api.myITTickets(token, 5).catch(() => []),
          api.teamLeavesToday(token).catch(() => []),
          isManager
            ? api.pendingApprovalsCount(token).catch(() => ({ count: 0 }))
            : Promise.resolve({ count: 0 }),
        ]);
        if (cancelled) return;
        setBalances(bal);
        setActivity(act);
        setOpenTickets(
          tix.filter((t) => !["resolved", "closed"].includes(t.status)),
        );
        setTeam(tm);
        setPendingCount(pc.count);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user, token, isManager]);

  if (!user) return null;

  const earned = balances.find((b) => b.leave_type === "earned");
  const sick = balances.find((b) => b.leave_type === "sick");

  return (
    <div className="flex-1 overflow-y-auto px-6 md:px-10 py-8">
      <div className="mx-auto max-w-6xl space-y-8">
        {/* Greeting */}
        <header className="space-y-1">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5" /> Good day
          </div>
          <h1 className="text-3xl font-bold text-zinc-100">
            Welcome, {(user.full_name || "there").split(" ")[0]}.
          </h1>
          <p className="text-zinc-400 text-sm">
            Here&apos;s a snapshot of your workspace.
          </p>
        </header>

        {/* Stat row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={<CalendarDays className="h-4 w-4" />}
            label="Earned leave"
            value={
              earned ? `${earned.available_days.toFixed(1)} days` : "—"
            }
            sub={
              earned
                ? `${earned.used_days} used · ${earned.pending_days} pending`
                : "no balance"
            }
            href="/leaves"
          />
          <StatCard
            icon={<CalendarDays className="h-4 w-4" />}
            label="Sick leave"
            value={sick ? `${sick.available_days.toFixed(1)} days` : "—"}
            sub={
              sick
                ? `${sick.used_days} used · ${sick.pending_days} pending`
                : "no balance"
            }
            href="/leaves"
          />
          <StatCard
            icon={<Wrench className="h-4 w-4" />}
            label="Open IT tickets"
            value={loading ? "…" : `${openTickets.length}`}
            sub="across all categories"
            href="/tickets"
          />
          {isManager ? (
            <StatCard
              icon={<Inbox className="h-4 w-4" />}
              label="Pending approvals"
              value={loading ? "…" : `${pendingCount}`}
              sub={pendingCount === 0 ? "all caught up" : "needs your action"}
              href="/approvals"
              accent={pendingCount > 0}
            />
          ) : (
            <StatCard
              icon={<Users className="h-4 w-4" />}
              label="Team on leave today"
              value={loading ? "…" : `${team.length}`}
              sub="in your department"
              href="#"
            />
          )}
        </div>

        {/* Two-column area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent activity */}
          <Card title="Recent activity" className="lg:col-span-2">
            {loading ? (
              <SkeletonRows />
            ) : activity.length === 0 ? (
              <Empty
                hint="You haven't applied for leave or raised any IT tickets yet. Try the chat!"
              />
            ) : (
              <ul className="divide-y divide-zinc-800/70">
                {activity.map((a, i) => (
                  <li
                    key={i}
                    className="py-3 flex items-center gap-3 group"
                  >
                    <div
                      className={`h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        a.kind === "leave"
                          ? "bg-indigo-500/15 text-indigo-300"
                          : "bg-amber-500/15 text-amber-300"
                      }`}
                    >
                      {a.kind === "leave" ? (
                        <CalendarDays className="h-4 w-4" />
                      ) : (
                        <Wrench className="h-4 w-4" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-zinc-200 truncate">
                        {a.title}
                      </div>
                      <div className="text-[11px] text-zinc-500">
                        {new Date(a.when).toLocaleString()}
                      </div>
                    </div>
                    <StatusBadge status={a.status} />
                  </li>
                ))}
              </ul>
            )}
          </Card>

          {/* Right column: quick actions + team */}
          <div className="space-y-6">
            <Card title="Quick actions">
              <div className="grid grid-cols-1 gap-2">
                <ActionLink
                  href="/chat"
                  icon={<MessageSquare className="h-4 w-4" />}
                  label="Ask Aura"
                  sub="Apply leave, raise a ticket, search policies"
                />
                <ActionLink
                  href="/leaves"
                  icon={<CalendarDays className="h-4 w-4" />}
                  label="My leaves"
                  sub="Balances and history"
                />
                <ActionLink
                  href="/tickets"
                  icon={<Wrench className="h-4 w-4" />}
                  label="My IT tickets"
                  sub="Open & resolved"
                />
              </div>
            </Card>

            <Card title="On leave today">
              {loading ? (
                <SkeletonRows count={3} />
              ) : team.length === 0 ? (
                <Empty hint="No one in your team is on leave today." />
              ) : (
                <ul className="space-y-2">
                  {team.map((t) => (
                    <li
                      key={t.user_id}
                      className="flex items-center gap-3 py-1.5"
                    >
                      <div className="h-7 w-7 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-[11px] text-zinc-300 font-semibold">
                        {(t.full_name || "?")
                          .split(" ")
                          .map((p) => p[0])
                          .slice(0, 2)
                          .join("")}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-zinc-200 truncate">
                          {t.full_name}
                        </div>
                        <div className="text-[11px] text-zinc-500 capitalize truncate">
                          {t.leave_type} · back after {t.end_date}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  sub,
  href,
  accent,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub: string;
  href: string;
  accent?: boolean;
}) {
  return (
    <Link
      href={href}
      className={`group relative rounded-2xl border p-4 transition-colors ${
        accent
          ? "bg-amber-500/10 border-amber-500/30 hover:bg-amber-500/15"
          : "bg-zinc-900/60 border-zinc-800/70 hover:border-zinc-700"
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span
          className={`inline-flex items-center justify-center h-8 w-8 rounded-lg ${
            accent
              ? "bg-amber-500/20 text-amber-300"
              : "bg-zinc-800 text-zinc-400"
          }`}
        >
          {icon}
        </span>
        <ArrowRight className="h-3.5 w-3.5 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
      </div>
      <div className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium">
        {label}
      </div>
      <div className="text-2xl font-bold text-zinc-100 mt-0.5">{value}</div>
      <div className="text-[11px] text-zinc-500 mt-0.5">{sub}</div>
    </Link>
  );
}

function Card({
  title,
  children,
  className = "",
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-2xl border border-zinc-800/70 bg-zinc-900/40 backdrop-blur-sm ${className}`}
    >
      <header className="px-5 py-3.5 border-b border-zinc-800/60">
        <h2 className="text-sm font-semibold text-zinc-200">{title}</h2>
      </header>
      <div className="px-5 py-3">{children}</div>
    </section>
  );
}

function ActionLink({
  href,
  icon,
  label,
  sub,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
  sub: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-zinc-800/60 transition-colors group"
    >
      <div className="h-8 w-8 rounded-lg bg-zinc-800 text-zinc-400 flex items-center justify-center group-hover:bg-indigo-500/20 group-hover:text-indigo-300 transition-colors">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm text-zinc-200">{label}</div>
        <div className="text-[11px] text-zinc-500 truncate">{sub}</div>
      </div>
      <ArrowRight className="h-3.5 w-3.5 text-zinc-600 group-hover:text-zinc-300 transition-colors" />
    </Link>
  );
}

function SkeletonRows({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-2 py-2">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="h-10 rounded-lg bg-zinc-800/40 animate-pulse"
        />
      ))}
    </div>
  );
}

function Empty({ hint }: { hint: string }) {
  return (
    <div className="py-6 text-center text-sm text-zinc-500">{hint}</div>
  );
}
