"use client";

import React, { useState, useRef, useEffect } from "react";
import { Info, FileText } from "lucide-react";

type Props = {
  source: string;
  section?: string;
  pages?: string;
};

export default function CitationPill({ source, section, pages }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <span
      ref={ref}
      className="relative inline-flex align-middle mx-0.5"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-indigo-500/15 text-indigo-300 hover:bg-indigo-500/25 hover:text-indigo-200 transition-colors border border-indigo-400/30"
        aria-label="Source"
      >
        <Info className="h-2.5 w-2.5" />
      </button>

      {open && (
        <span
          role="tooltip"
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64 rounded-lg border border-zinc-700/70 bg-zinc-900/95 backdrop-blur-md px-3 py-2.5 text-[12px] text-zinc-200 shadow-xl shadow-black/40"
        >
          <span className="flex items-center gap-1.5 mb-1 text-indigo-300 font-semibold">
            <FileText className="h-3 w-3" />
            Source
          </span>
          <span className="block text-zinc-100 font-medium break-words">
            {source}
          </span>
          {section && (
            <span className="block text-zinc-300 mt-0.5">
              {section}
            </span>
          )}
          {pages && (
            <span className="block text-zinc-400 mt-0.5 text-[11px]">
              {pages}
            </span>
          )}
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-px h-2 w-2 rotate-45 border-r border-b border-zinc-700/70 bg-zinc-900/95" />
        </span>
      )}
    </span>
  );
}
