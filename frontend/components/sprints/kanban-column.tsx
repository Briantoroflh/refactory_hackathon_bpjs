"use client";

import type { SprintMember, SprintTask, SprintTaskStatus } from "@/lib/sprints/types";
import { TaskCard } from "./task-card";

type KanbanColumnProps = {
  status: SprintTaskStatus;
  title: string;
  borderColorClass: string;
  tasks: SprintTask[];
  membersMap: Record<string, SprintMember>;
  onDropTask: (status: SprintTaskStatus) => void;
  onDragStart: (taskId: string) => void;
  onDragEnd: () => void;
};

export function KanbanColumn({
  status,
  title,
  borderColorClass,
  tasks,
  membersMap,
  onDropTask,
  onDragStart,
  onDragEnd,
}: KanbanColumnProps) {
  return (
    <section
      onDragOver={(event) => event.preventDefault()}
      onDrop={() => onDropTask(status)}
      className={`rounded-3xl border border-[#dde2f1] bg-[#f3f1fb] p-4 ${borderColorClass}`}
    >
      <header className="mb-4 flex items-center justify-between">
        <h3 className="text-[21px] font-bold tracking-[-0.02em] text-slate-700">{title}</h3>
        <span className="inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-[#e6e4f1] px-2 text-[13px] font-semibold text-slate-500">
          {tasks.length}
        </span>
      </header>

      <div className="space-y-3">
        {tasks.length ? (
          tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              membersMap={membersMap}
              dueLabel={task.dueState?.label ?? ""}
              dueTone={task.dueState?.tone ?? "neutral"}
              onDragStart={onDragStart}
              onDragEnd={onDragEnd}
            />
          ))
        ) : (
          <div className="rounded-2xl border border-dashed border-[#d8dcec] bg-white/65 p-6 text-center text-[15px] text-slate-500">
            No tasks yet in this column.
          </div>
        )}
      </div>
    </section>
  );
}

