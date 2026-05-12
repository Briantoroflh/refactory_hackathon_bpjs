"use client";

import React from "react";
import { AppLayout } from "@/components/layout/app-layout";
import type { SprintTasks, TaskCard } from "@/lib/tasks/types";

type TasksPageProps = {
  tasks: SprintTasks;
  notice?: string | null;
};

function PriorityBadge({ priority }: { priority: string }) {
  const variants = {
    low: "bg-blue-50 text-blue-700 border-blue-200",
    medium: "bg-amber-50 text-amber-700 border-amber-200",
    high: "bg-rose-50 text-rose-700 border-rose-200",
  };
  return (
    <span
      className={`inline-flex rounded border px-2 py-0.5 text-[11px] font-semibold capitalize ${
        variants[priority as keyof typeof variants] || "bg-slate-50 text-slate-700 border-slate-200"
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
        className="h-full bg-[#4338ca] rounded-full transition-all"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

function TaskCardItem({ card }: { card: TaskCard }) {
  return (
    <div className="rounded-[20px] border border-slate-200 bg-white p-4 shadow-[0_4px_12px_rgba(15,23,42,0.03)] hover:shadow-[0_8px_24px_rgba(15,23,42,0.08)] transition-all cursor-grab active:cursor-grabbing group">
      <div className="flex items-start justify-between gap-2 mb-3">
        <span className="text-[11px] font-bold text-slate-500 uppercase bg-slate-100 px-2 py-0.5 rounded-lg">
          {card.label}
        </span>
        <PriorityBadge priority={card.priority} />
      </div>

      <h3 className="text-[14px] font-bold text-slate-900 mb-2 leading-snug group-hover:text-[#4338ca] transition-colors">
        {card.title}
      </h3>

      {card.description && (
        <p className="text-[13px] text-slate-600 mb-4 line-clamp-2">{card.description}</p>
      )}

      {card.progress !== undefined && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-bold text-slate-500">Progress</span>
            <span className="text-[11px] font-bold text-[#4338ca]">{card.progress}%</span>
          </div>
          <ProgressBar progress={card.progress} />
        </div>
      )}

      <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-50">
        {card.assignee && (
          <div className="flex items-center gap-2">
            <div className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-[#4338ca] to-[#6366f1] text-white text-[11px] font-bold shadow-sm">
              {card.assignee.avatar}
            </div>
            <span className="text-[12px] font-medium text-slate-700">{card.assignee.name}</span>
          </div>
        )}
        <button className="h-8 w-8 inline-flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition">⋮</button>
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
    <div className="flex flex-col w-[320px] bg-[#f1f3f9]/50 rounded-[24px] p-4 border border-slate-200/60 h-full">
      {/* Column Header */}
      <div className="flex items-center justify-between mb-5 px-1">
        <div className="flex items-center gap-2.5">
          <h3 className="text-[16px] font-bold text-slate-800">{title}</h3>
          <span className="inline-flex h-6 w-6 items-center justify-center rounded-xl bg-white border border-slate-200 text-[12px] font-bold text-[#4338ca] shadow-sm">
            {count}
          </span>
        </div>
        <button className="h-8 w-8 inline-flex items-center justify-center rounded-xl text-slate-400 hover:bg-white hover:text-[#4338ca] hover:border-slate-200 border border-transparent transition">⊕</button>
      </div>

      {/* Cards */}
      <div className="flex-1 space-y-4 overflow-y-auto pr-1 custom-scrollbar">
        {cards.map((card) => (
          <TaskCardItem key={card.id} card={card} />
        ))}
        <button className="w-full py-3 rounded-2xl border-2 border-dashed border-slate-200 text-slate-400 text-[13px] font-bold hover:border-[#4338ca] hover:text-[#4338ca] hover:bg-white transition-all">
          + Add Task
        </button>
      </div>
    </div>
  );
}

export function TasksPage({ tasks, notice }: TasksPageProps) {
  const title = tasks.sprintNumber
    ? `Sprint ${tasks.sprintNumber}: ${tasks.sprintTitle}`
    : tasks.sprintTitle;

  return (
    <AppLayout title={title}>
      <div className="h-full flex flex-col space-y-6">
        {notice ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-[14px] font-medium text-amber-800">
            {notice}
          </div>
        ) : null}

        {/* Header Extra Info */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-4 text-[14px] font-medium text-slate-500">
            <span className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm">
              📅 {tasks.dateRange}
            </span>
            <a
              href={tasks.repositoryHref ?? "#"}
              className="flex items-center gap-2 text-[#4338ca] hover:bg-[#4338ca] hover:text-white transition-colors bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm font-bold"
              target={tasks.repositoryHref ? "_blank" : undefined}
              rel={tasks.repositoryHref ? "noreferrer" : undefined}
            >
              🔗 {tasks.repositoryLink}
            </a>
          </div>
          <button className="inline-flex items-center gap-2 rounded-xl bg-[#4338ca] px-5 py-2.5 text-[14px] font-bold text-white hover:bg-[#3f2fd6] transition shadow-[0_10px_24px_rgba(67,56,202,0.25)]">
            ✨ AI Generate Kanban
          </button>
        </div>

        {/* Kanban Board */}
        <div className="flex-1 overflow-x-auto min-h-0">
          <div className="flex gap-6 pb-6 min-w-max h-full">
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
    </AppLayout>
  );
}
