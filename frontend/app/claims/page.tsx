"use client";

import { Receipt, Hammer } from "lucide-react";
import Link from "next/link";

export default function ClaimsPage() {
  return (
    <div className="flex-1 flex items-center justify-center p-10">
      <div className="text-center max-w-md">
        <div className="inline-flex items-center justify-center h-14 w-14 rounded-2xl bg-amber-500/15 text-amber-300 mb-4">
          <Receipt className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-bold text-zinc-100">
          Reimbursements — coming soon
        </h1>
        <p className="text-sm text-zinc-400 mt-2 leading-relaxed">
          The Finance module (payslips, reimbursement claims, tax queries) is
          being built out. For urgent finance matters, please contact the
          Finance team directly. In the meantime, you can keep using HR and IT
          self-service via the chat assistant.
        </p>
        <div className="mt-6 inline-flex items-center gap-2 text-[11px] text-zinc-500">
          <Hammer className="h-3.5 w-3.5" /> In active development
        </div>
        <div className="mt-8">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold text-zinc-200 bg-zinc-800 border border-zinc-700 hover:bg-zinc-700 transition-colors"
          >
            Back to dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
