"use client";

import type { SprintMember, SprintTask, SprintTaskStatus } from "@/lib/sprints/types";
import { KanbanColumn } from "./kanban-column";

type KanbanBoardProps = {
  tasksByStatus: Record<SprintTaskStatus, SprintTask[]>;
  membersMap: Record<string, SprintMember>;
  onDropTask: (status: SprintTaskStatus) => void;
  onDragStart: (taskId: string) => void;
  onDragEnd: () => void;
};

const columnConfigs: Array<{
  status: SprintTaskStatus;
  title: string;
  borderColorClass: string;
}> = [
  { status: "todo", title: "Todo", borderColorClass: "border-t-[3px] border-t-slate-300" },
  { status: "in_progress", title: "In Progress", borderColorClass: "border-t-[3px] border-t-[#4f46e5]" },
  { status: "review", title: "Review", borderColorClass: "border-t-[3px] border-t-[#f59e0b]" },
  { status: "done", title: "Done", borderColorClass: "border-t-[3px] border-t-[#10b981]" },
];

export function KanbanBoard({
  tasksByStatus,
  membersMap,
  onDropTask,
  onDragStart,
  onDragEnd,
}: KanbanBoardProps) {
  return (
    <div className="grid gap-4 xl:grid-cols-4 md:grid-cols-2 grid-cols-1">
      {columnConfigs.map((column) => (
        <KanbanColumn
          key={column.status}
          status={column.status}
          title={column.title}
          borderColorClass={column.borderColorClass}
          tasks={tasksByStatus[column.status]}
          membersMap={membersMap}
          onDropTask={onDropTask}
          onDragStart={onDragStart}
          onDragEnd={onDragEnd}
        />
      ))}
    </div>
  );
}

