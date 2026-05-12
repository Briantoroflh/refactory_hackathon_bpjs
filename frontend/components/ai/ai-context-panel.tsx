"use client";

import type { AIDocument, AIContextItem } from "@/lib/ai/types";

type AIContextPanelProps = {
  documents: AIDocument[];
  contextItems: AIContextItem[];
};

export function AIContextPanel({
  documents,
  contextItems,
}: AIContextPanelProps) {
  return (
    <aside className="flex flex-col overflow-hidden rounded-[24px] border border-slate-200 bg-white shadow-[0_12px_28px_rgba(15,23,42,0.05)] lg:h-full">
      {/* Header */}
      <div className="border-b border-slate-200 px-6 py-5">
        <h2 className="text-lg font-semibold text-slate-900">Active Context</h2>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Documents Section */}
        <div className="border-b border-slate-200 px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
            Documents
          </p>
          <div className="mt-3 space-y-2">
            {documents.length ? documents.map((doc) => (
              <div
                key={doc.id}
                className="rounded-lg border border-slate-200 bg-slate-50 p-3 hover:bg-slate-100 transition cursor-pointer"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-slate-900 truncate">
                      {doc.title}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {doc.updated || doc.status}
                    </p>
                  </div>
                  <span
                    className={`whitespace-nowrap rounded px-2 py-0.5 text-xs font-medium ${
                      doc.type === "documentation"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-purple-100 text-purple-700"
                    }`}
                  >
                    {doc.type === "documentation" ? "📄" : "🐛"}
                  </span>
                </div>
              </div>
            )) : (
              <p className="rounded-lg border border-dashed border-slate-200 bg-slate-50 px-3 py-4 text-sm text-slate-500">
                No live documents loaded yet.
              </p>
            )}
          </div>
        </div>

        {/* Active Items Section */}
        <div className="px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
            Active Items
          </p>
          <div className="mt-3 space-y-2">
            {contextItems.length ? contextItems.map((item) => (
              <div
                key={item.id}
                className={`rounded-lg border px-3 py-3 ${
                  item.type === "active"
                    ? "border-indigo-200 bg-indigo-50"
                    : "border-slate-200 bg-slate-50"
                } hover:shadow-md transition cursor-pointer`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm text-indigo-600">◆</span>
                  <p className="text-sm font-medium text-slate-900 truncate">
                    {item.label}
                  </p>
                </div>
              </div>
            )) : (
              <p className="rounded-lg border border-dashed border-slate-200 bg-slate-50 px-3 py-4 text-sm text-slate-500">
                No active context loaded yet.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-slate-200 px-4 py-3">
        <button className="w-full rounded-lg bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-100 transition">
          + Add Context
        </button>
      </div>
    </aside>
  );
}
