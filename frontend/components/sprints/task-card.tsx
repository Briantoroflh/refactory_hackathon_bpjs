"use client";

import { memo } from "react";
import type { SprintMember, SprintTask } from "@/lib/sprints/types";
import { CalendarIcon } from "./sprint-icons";

type TaskCardProps = {
  task: SprintTask;
  membersMap: Record<string, SprintMember>;
  dueLabel: string;
  dueTone: "neutral" | "warning" | "danger";
  onDragStart: (taskId: string) => void;
  onDragEnd: () => void;
};

const priorityClasses: Record<SprintTask["priority"], string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-[#e5ecff] text-[#3150d8]",
  high: "bg-[#fff1db] text-[#ca7a15]",
  critical: "bg-[#fee2e2] text-[#b91c1c]",
};

const dueClasses: Record<TaskCardProps["dueTone"], string> = {
  neutral: "bg-slate-100 text-slate-600",
  warning: "bg-amber-100 text-amber-700",
  danger: "bg-rose-100 text-rose-700",
};

const tagDotClasses: Record<string, string> = {
  backend: "bg-[#6d4cff]",
  database: "bg-[#ef4444]",
  devops: "bg-[#0ea5e9]",
  design: "bg-[#8b5cf6]",
  chore: "bg-[#f59e0b]",
};

function TaskCardComponent({
  task,
  membersMap,
  dueLabel,
  dueTone,
  onDragStart,
  onDragEnd,
}: TaskCardProps) {
  const firstTag = task.tags[0] ?? "General";
  const tagKey = firstTag.toLowerCase();

  return (
    <article
      draggable
      onDragStart={() => onDragStart(task.id)}
      onDragEnd={onDragEnd}
      className="rounded-2xl border border-[#dce0ef] bg-white p-4 shadow-[0_8px_18px_rgba(15,23,42,0.06)]"
    >
      <div className="flex items-start justify-between gap-2">
        <span className="rounded-lg bg-[#f2f1fb] px-2.5 py-1 text-[14px] font-semibold text-slate-500">
          {task.id}
        </span>
        <span className="inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-[#eeedf7] px-2 text-[14px] font-semibold text-slate-500">
          {task.storyPoints}
        </span>
      </div>

      <h4 className="mt-3 text-[18px] leading-tight font-semibold tracking-[-0.02em] text-slate-700">
        {task.title}
      </h4>

      <div className="mt-3 flex items-center gap-2">
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${priorityClasses[task.priority]}`}
        >
          {task.priority.toUpperCase()}
        </span>
        <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${dueClasses[dueTone]}`}>
          <CalendarIcon className="mr-1.5 h-3.5 w-3.5" />
          {dueLabel}
        </span>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <p className="inline-flex items-center gap-2 text-[15px] font-medium text-slate-500">
          <span className={`h-2.5 w-2.5 rounded-full ${tagDotClasses[tagKey] ?? "bg-[#6d4cff]"}`} />
          {firstTag}
        </p>
        <div className="flex -space-x-2">
          {task.assigneeIds.slice(0, 2).map((memberId) => {
            const member = membersMap[memberId];

            if (!member) {
              return null;
            }

            return (
              <span
                key={member.id}
                title={member.name}
                className="inline-flex h-8 w-8 items-center justify-center rounded-full border-2 border-white text-[11px] font-bold text-white shadow-[0_6px_10px_rgba(15,23,42,0.22)]"
                style={{ backgroundColor: member.color }}
              >
                {member.avatar}
              </span>
            );
          })}
        </div>
      </div>
    </article>
  );
}

export const TaskCard = memo(TaskCardComponent);
