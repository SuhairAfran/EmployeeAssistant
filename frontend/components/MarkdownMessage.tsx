"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CitationPill from "./CitationPill";

type Props = { content: string };

// Replace [cite: file | section | pages] tokens with placeholders, then
// render the rest as markdown and re-inject CitationPill components.
const CITE_RE = /\[cite:\s*([^\]]+?)\s*\]/g;

type Cite = { source: string; section?: string; pages?: string };

function parseCitations(text: string): { segments: Array<string | Cite> } {
  const segments: Array<string | Cite> = [];
  let last = 0;
  let m: RegExpExecArray | null;
  CITE_RE.lastIndex = 0;
  while ((m = CITE_RE.exec(text)) !== null) {
    if (m.index > last) segments.push(text.slice(last, m.index));
    const parts = m[1].split("|").map((s) => s.trim()).filter(Boolean);
    segments.push({ source: parts[0] || "Source", section: parts[1], pages: parts[2] });
    last = m.index + m[0].length;
  }
  if (last < text.length) segments.push(text.slice(last));
  return { segments };
}

function renderWithCitations(text: string): React.ReactNode {
  const { segments } = parseCitations(text);
  if (segments.length === 1 && typeof segments[0] === "string") return text;
  return segments.map((seg, i) =>
    typeof seg === "string" ? (
      <React.Fragment key={i}>{seg}</React.Fragment>
    ) : (
      <CitationPill key={i} source={seg.source} section={seg.section} pages={seg.pages} />
    )
  );
}

function withCitationChildren(children: React.ReactNode): React.ReactNode {
  return React.Children.map(children, (child) => {
    if (typeof child === "string") return renderWithCitations(child);
    return child;
  });
}

export default function MarkdownMessage({ content }: Props) {
  return (
    <div className="markdown-body text-[15px] leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => (
            <p className="mb-2 last:mb-0">{withCitationChildren(children)}</p>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-white">
              {withCitationChildren(children)}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic">{withCitationChildren(children)}</em>
          ),
          ul: ({ children }) => (
            <ul className="list-disc pl-5 my-2 space-y-1 marker:text-indigo-400">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-5 my-2 space-y-1 marker:text-indigo-400">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="leading-relaxed">{withCitationChildren(children)}</li>
          ),
          h1: ({ children }) => (
            <h1 className="text-lg font-semibold text-white mt-2 mb-1.5">
              {withCitationChildren(children)}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-base font-semibold text-white mt-2 mb-1.5">
              {withCitationChildren(children)}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-[15px] font-semibold text-white mt-2 mb-1">
              {withCitationChildren(children)}
            </h3>
          ),
          code: ({ children, ...props }) => {
            const inline = !(props as { className?: string }).className;
            return inline ? (
              <code className="px-1.5 py-0.5 rounded bg-zinc-700/60 text-indigo-200 text-[13px] font-mono">
                {children}
              </code>
            ) : (
              <code className="block px-3 py-2 rounded-lg bg-zinc-900/80 border border-zinc-700/60 text-zinc-100 text-[13px] font-mono overflow-x-auto">
                {children}
              </code>
            );
          },
          a: ({ children, href }) => (
            <a
              href={href}
              target="_blank"
              rel="noreferrer"
              className="text-indigo-300 underline underline-offset-2 hover:text-indigo-200"
            >
              {children}
            </a>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-indigo-500/60 pl-3 my-2 text-zinc-300 italic">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-lg border border-zinc-700/60">
              <table className="w-full text-sm">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="px-3 py-2 text-left font-semibold bg-zinc-800/80 border-b border-zinc-700/60">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 border-b border-zinc-800/60">
              {withCitationChildren(children)}
            </td>
          ),
          hr: () => <hr className="my-3 border-zinc-700/60" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
