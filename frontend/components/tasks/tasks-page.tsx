"use client";

import { useState } from "react";
import { TasksNavbar } from "./tasks-navbar";
import { TasksSidebar } from "./tasks-sidebar";
import type { SprintTasks, TaskCard } from "@/lib/tasks/types";

type TasksPageProps = {
  tasks: SprintTasks;
};

function PriorityBadge({ priority }: { priority: string }) {
  const variants = {
    low: "bg-blue-50 text-blue-700 border-blue-200",
    medium: "bg-amber-50 text-amber-700 border-amber-200",
    high: "bg-rose-50 text-rose-700 border-rose-200",
  };
  return (
    <span
      className={`inline-flex rounded border px-2 py-0.5 text-[11px] font-semibold capitalize border ${
        variants[priority as keyof typeof variants]
      }`}
    >
      {priority}
    </span>
  );
}

function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="h-1.5 w-full rounded-full bg-slate-200 overflow-hidden">
      <div
        className="h-full bg-blue-500 rounded-full transition-all"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

function TaskCard({ card }: { card: TaskCard }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm hover:shadow-md transition cursor-grab active:cursor-grabbing">
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-[11px] font-semibold text-slate-500 uppercase bg-slate-100 px-1.5 py-0.5 rounded">
          {card.label}
        </span>
        <PriorityBadge priority={card.priority} />
      </div>

      <h3 className="text-[13px] font-semibold text-slate-900 mb-2 leading-snug">
        {card.title}
      </h3>

      {card.description && (
        <p className="text-[12px] text-slate-600 mb-3">{card.description}</p>
      )}

      {card.progress !== undefined && (
        <div className="mb-3">
          <ProgressBar progress={card.progress} />
          <span className="text-[11px] text-slate-500 mt-1 inline-block">
            {card.progress}%
          </span>
        </div>
      )}

      <div className="flex items-center justify-between">
        {card.assignee && (
          <div className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-[#4338ca] text-white text-[10px] font-bold">
            {card.assignee.avatar}
          </div>
        )}
        <button className="text-slate-400 hover:text-slate-600">⋮</button>
      </div>
    </div>
  );
}

function KanbanColumn({
  title,
  count,
  cards,
}: {
  title: string;
  count: number;
  cards: TaskCard[];
}) {
  return (
    <div className="flex flex-col w-full sm:w-80 bg-slate-50 rounded-lg p-4 border border-slate-200">
      {/* Column Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-[14px] font-semibold text-slate-900">{title}</h3>
          <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-200 text-[11px] font-bold text-slate-700">
            {count}
          </span>
        </div>
        <button className="text-slate-400 hover:text-slate-600">⊕</button>
      </div>

      {/* Cards */}
      <div className="flex-1 space-y-2 overflow-y-auto">
        {cards.map((card) => (
          <TaskCard key={card.id} card={card} />
        ))}
      </div>
    </div>
  );
}

export function TasksPage({ tasks }: TasksPageProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [query, setQuery] = useState("");

  return (
    <div className="flex h-screen bg-slate-50">
      <TasksSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <TasksNavbar
          query={query}
          onOpenSidebar={() => setSidebarOpen(true)}
          onQueryChange={setQuery}
        />

        <main className="flex-1 overflow-hidden">
          <div className="h-full flex flex-col p-4 sm:p-6 lg:p-8">
            {/* Header */}
            <div className="mb-6 flex flex-col gap-4">
              <div>
                <h1 className="text-[28px] font-bold text-slate-900">
                  Sprint {tasks.sprintNumber}: {tasks.sprintTitle}
                </h1>
                <div className="mt-2 flex flex-wrap items-center gap-4 text-[14px] text-slate-600">
                  <span>📅 {tasks.dateRange}</span>
                  <a
                    href="#"
                    className="flex items-center gap-1.5 text-[#4338ca] hover:underline"
                  >
                    🔗 {tasks.repositoryLink}
                  </a>
                </div>
              </div>
              <button className="inline-flex w-fit items-center gap-2 rounded-lg bg-[#4338ca] px-4 py-2.5 text-[14px] font-semibold text-white hover:bg-[#3f2fd6] transition">
                💬 AI Generate Kanban
              </button>
            </div>

            {/* Kanban Board */}
            <div className="flex-1 overflow-x-auto">
              <div className="flex gap-4 pb-4 min-w-min">
                {tasks.columns.map((column) => (
                  <KanbanColumn
                    key={column.id}
                    title={column.title}
                    count={column.count}
                    cards={column.cards}
                  />
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
