"use client";

import type { CodeSnippet } from "@/lib/ai/types";
import { CopyIcon } from "./ai-icons";
import { useState } from "react";

type CodeBlockProps = {
  snippet: CodeSnippet;
};

export function CodeBlock({ snippet }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(snippet.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg bg-slate-950 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-900 px-4 py-2">
        <span className="text-xs font-mono text-slate-400">
          {snippet.code.split("\n")[0]}
        </span>
        <button
          onClick={handleCopy}
          className="text-slate-400 hover:text-slate-200 transition"
          title={copied ? "Copied!" : "Copy"}
        >
          <CopyIcon className="h-4 w-4" />
        </button>
      </div>

      {/* Code */}
      <pre className="overflow-x-auto px-4 py-3">
        <code className="text-xs font-mono text-slate-300 leading-relaxed">
          {snippet.code}
        </code>
      </pre>
    </div>
  );
}
