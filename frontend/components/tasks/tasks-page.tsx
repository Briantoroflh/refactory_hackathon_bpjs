"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { updateTaskStatus, generateKanbanWithAI, pollAIJobStatus, type AIJobResponse } from "@/lib/tasks/api";
import type { SprintTasks, TaskCard } from "@/lib/tasks/types";

type TasksPageProps = {
  tasks: SprintTasks;
  projectId: number;
  notice?: string | null;
};

type TaskStatus = "todo" | "in_progress" | "review" | "done";

const columnOrder: TaskStatus[] = ["todo", "in_progress", "review", "done"];

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
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
      <div
        className="h-full rounded-full bg-[#4338ca] transition-all"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

function normalizeTaskStatus(status?: string): TaskStatus {
  if (status === "in_progress" || status === "review" || status === "done") {
    return status;
  }
  return "todo";
}

function moveTask(
  columns: SprintTasks["columns"],
  taskId: string,
  nextStatus: TaskStatus,
) {
  let movedTask: TaskCard | null = null;

  const nextColumns = columns.map((column) => {
    const taskIndex = column.cards.findIndex((card) => card.id === taskId);
    if (taskIndex === -1) {
      return column;
    }

    const task = column.cards[taskIndex];
    movedTask = { ...task, status: nextStatus, version: (task.version ?? 1) + 1 };

    return {
      ...column,
      cards: column.cards.filter((card) => card.id !== taskId),
    };
  });

  if (!movedTask) {
    return columns;
  }

  return nextColumns.map((column) => {
    if (column.id !== nextStatus) {
      return {
        ...column,
        count: column.cards.length,
      };
    }

    return {
      ...column,
      cards: [...column.cards, movedTask],
      count: column.cards.length + 1,
    };
  });
}

function TaskCardItem({
  card,
  onDragStart,
  onDragEnd,
}: {
  card: TaskCard;
  onDragStart: (taskId: string) => void;
  onDragEnd: () => void;
}) {
  return (
    <div
      draggable
      onDragStart={() => onDragStart(card.id)}
      onDragEnd={onDragEnd}
      className="group cursor-grab rounded-[20px] border border-slate-200 bg-white p-4 shadow-[0_4px_12px_rgba(15,23,42,0.03)] transition-all hover:shadow-[0_8px_24px_rgba(15,23,42,0.08)] active:cursor-grabbing"
    >
      <div className="mb-3 flex items-start justify-between gap-2">
        <span className="rounded-lg bg-slate-100 px-2 py-0.5 text-[11px] font-bold uppercase text-slate-500">
          {card.label}
        </span>
        <PriorityBadge priority={card.priority} />
      </div>

      <h3 className="mb-2 text-[14px] font-bold leading-snug text-slate-900 transition-colors group-hover:text-[#4338ca]">
        {card.title}
      </h3>

      {card.description && (
        <p className="mb-4 line-clamp-2 text-[13px] text-slate-600">{card.description}</p>
      )}

      {card.progress !== undefined && (
        <div className="mb-4">
          <div className="mb-1.5 flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500">Progress</span>
            <span className="text-[11px] font-bold text-[#4338ca]">{card.progress}%</span>
          </div>
          <ProgressBar progress={card.progress} />
        </div>
      )}

      <div className="mt-auto flex items-center justify-between border-t border-slate-50 pt-2">
        {card.assignee && (
          <div className="flex items-center gap-2">
            <div className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-[#4338ca] to-[#6366f1] text-[11px] font-bold text-white shadow-sm">
              {card.assignee.avatar}
            </div>
            <span className="text-[12px] font-medium text-slate-700">{card.assignee.name}</span>
          </div>
        )}
        <button className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-600">
          ⋮
        </button>
      </div>
    </div>
  );
}

function KanbanColumn({
  title,
  count,
  cards,
  onDrop,
  onDragStart,
  onDragEnd,
}: {
  title: string;
  count: number;
  cards: TaskCard[];
  onDrop: () => void;
  onDragStart: (taskId: string) => void;
  onDragEnd: () => void;
}) {
  return (
    <div
      onDragOver={(event) => event.preventDefault()}
      onDrop={onDrop}
      className="flex h-full w-[320px] flex-col rounded-[24px] border border-slate-200/60 bg-[#f1f3f9]/50 p-4"
    >
      <div className="mb-5 flex items-center justify-between px-1">
        <div className="flex items-center gap-2.5">
          <h3 className="text-[16px] font-bold text-slate-800">{title}</h3>
          <span className="inline-flex h-6 w-6 items-center justify-center rounded-xl border border-slate-200 bg-white text-[12px] font-bold text-[#4338ca] shadow-sm">
            {count}
          </span>
        </div>
      </div>

      <div className="custom-scrollbar flex-1 space-y-4 overflow-y-auto pr-1">
        {cards.map((card) => (
          <TaskCardItem
            key={card.id}
            card={card}
            onDragStart={onDragStart}
            onDragEnd={onDragEnd}
          />
        ))}
        <div className="rounded-2xl border-2 border-dashed border-slate-200 py-3 text-center text-[13px] font-bold text-slate-400 transition-all hover:border-[#4338ca] hover:bg-white hover:text-[#4338ca]">
          + Add Task
        </div>
      </div>
    </div>
  );
}

export function TasksPage({ tasks, projectId, notice }: TasksPageProps) {
  const [board, setBoard] = useState(tasks);
  const [draggingTaskId, setDraggingTaskId] = useState<string | null>(null);
  const [statusNotice, setStatusNotice] = useState<string | null>(notice ?? null);
  const [savingTaskId, setSavingTaskId] = useState<string | null>(null);
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiJobId, setAiJobId] = useState<string | null>(null);

  useEffect(() => {
    setBoard(tasks);
  }, [tasks]);

  useEffect(() => {
    setStatusNotice(notice ?? null);
  }, [notice]);

  const title = board.sprintNumber
    ? `Sprint ${board.sprintNumber}: ${board.sprintTitle}`
    : board.sprintTitle;

  const updateLocalBoard = useCallback((taskId: string, nextStatus: TaskStatus) => {
    setBoard((current) => ({
      ...current,
      columns: moveTask(current.columns, taskId, nextStatus),
    }));
  }, []);

  const handleDrop = useCallback(
    async (nextStatus: TaskStatus) => {
      if (!draggingTaskId) {
        return;
      }

      const sourceCard = board.columns.flatMap((column) => column.cards).find((card) => card.id === draggingTaskId);
      if (!sourceCard) {
        setDraggingTaskId(null);
        return;
      }

      const currentStatus = normalizeTaskStatus(sourceCard.status);
      if (currentStatus === nextStatus) {
        setDraggingTaskId(null);
        return;
      }

      const previousBoard = board;
      updateLocalBoard(draggingTaskId, nextStatus);
      setSavingTaskId(draggingTaskId);
      setStatusNotice(null);
      setDraggingTaskId(null);

      try {
        await updateTaskStatus(draggingTaskId, nextStatus, sourceCard.version ?? 1, projectId);
      } catch (error) {
        setBoard(previousBoard);
        setStatusNotice(error instanceof Error ? error.message : "Failed to update task status");
      } finally {
        setSavingTaskId(null);
      }
    },
    [board, draggingTaskId, projectId, updateLocalBoard],
  );

  const pollJobCompletion = useCallback(
    async (jobId: string) => {
      let attempts = 0;
      const maxAttempts = 60;

      while (attempts < maxAttempts) {
        try {
          const result = await pollAIJobStatus(jobId);

          if (result.status === "completed" || result.status === "success") {
            if (result.result?.structured_output) {
              const generatedTasks = result.result.structured_output.tasks as unknown[];
              if (Array.isArray(generatedTasks) && generatedTasks.length > 0) {
                setStatusNotice(`✅ Generated ${generatedTasks.length} new tasks`);
              }
            }
            setAiJobId(null);
            setAiGenerating(false);
            return;
          }

          if (result.status === "failed" || result.status === "error") {
            setStatusNotice(result.error || "AI generation failed");
            setAiJobId(null);
            setAiGenerating(false);
            return;
          }

          attempts += 1;
          await new Promise((resolve) => setTimeout(resolve, 1000));
        } catch (error) {
          setStatusNotice(error instanceof Error ? error.message : "Polling failed");
          setAiJobId(null);
          setAiGenerating(false);
          return;
        }
      }

      setStatusNotice("AI generation timed out after 60s");
      setAiJobId(null);
      setAiGenerating(false);
    },
    [],
  );

  useEffect(() => {
    if (aiJobId) {
      void pollJobCompletion(aiJobId);
    }
  }, [aiJobId, pollJobCompletion]);

  const handleAIGenerate = useCallback(async () => {
    setAiGenerating(true);
    setStatusNotice(null);

    try {
      const response = await generateKanbanWithAI(
        projectId,
        "Generate optimized kanban tasks for this project based on best practices and industry standards.",
      );

      const jobId = (response as Record<string, unknown>)?.job_id;
      if (jobId) {
        setAiJobId(String(jobId));
        setStatusNotice("🔄 AI is generating kanban tasks...");
      } else {
        setStatusNotice("Failed to start AI generation");
        setAiGenerating(false);
      }
    } catch (error) {
      setStatusNotice(error instanceof Error ? error.message : "Failed to start AI generation");
      setAiGenerating(false);
    }
  }, [projectId]);

  const columns = useMemo(
    () =>
      columnOrder
        .map((status) => {
          const column = board.columns.find((item) => item.id === status);
          return {
            id: status,
            title: column?.title ?? status,
            count: column?.count ?? 0,
            cards: column?.cards ?? [],
          };
        }),
    [board.columns],
  );

  return (
    <AppLayout title={title}>
      <div className="flex h-full flex-col space-y-6">
        {statusNotice ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-[14px] font-medium text-amber-800">
            {statusNotice}
          </div>
        ) : null}

        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex flex-wrap items-center gap-4 text-[14px] font-medium text-slate-500">
            <span className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-1.5 shadow-sm">
              📅 {board.dateRange}
            </span>
            <a
              href={board.repositoryHref ?? "#"}
              className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-1.5 font-bold text-[#4338ca] shadow-sm transition-colors hover:bg-[#4338ca] hover:text-white"
              target={board.repositoryHref ? "_blank" : undefined}
              rel={board.repositoryHref ? "noreferrer" : undefined}
            >
              🔗 {board.repositoryLink}
            </a>
          </div>
          <button 
            onClick={() => void handleAIGenerate()}
            disabled={aiGenerating}
            className="inline-flex items-center gap-2 rounded-xl bg-[#4338ca] px-5 py-2.5 text-[14px] font-bold text-white shadow-[0_10px_24px_rgba(67,56,202,0.25)] transition hover:bg-[#3f2fd6] disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {aiGenerating ? "⏳ Generating..." : "✨ AI Generate Kanban"}
          </button>
        </div>

        <div className="flex-1 min-h-0 overflow-x-auto">
          <div className="flex min-w-max gap-6 pb-6">
            {columns.map((column) => (
              <KanbanColumn
                key={column.id}
                title={column.title}
                count={column.count}
                cards={column.cards}
                onDrop={() => void handleDrop(column.id)}
                onDragStart={setDraggingTaskId}
                onDragEnd={() => setDraggingTaskId(null)}
              />
            ))}
          </div>
        </div>
      </div>

      {savingTaskId ? (
        <div className="fixed right-4 bottom-4 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-[0_10px_28px_rgba(15,23,42,0.32)]">
          Saving task {savingTaskId}...
        </div>
      ) : null}
    </AppLayout>
  );
}
