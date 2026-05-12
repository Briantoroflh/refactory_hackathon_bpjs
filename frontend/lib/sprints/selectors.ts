import type {
  SprintFilterState,
  SprintMember,
  SprintTask,
  SprintTaskStatus,
} from "./types";

export function createMembersMap(members: SprintMember[]) {
  return Object.fromEntries(members.map((member) => [member.id, member])) as Record<
    string,
    SprintMember
  >;
}

export function filterTasks(
  tasks: SprintTask[],
  filters: SprintFilterState,
  membersMap: Record<string, SprintMember>,
) {
  const query = filters.query.trim().toLowerCase();

  return tasks.filter((task) => {
    if (filters.priority !== "all" && task.priority !== filters.priority) {
      return false;
    }

    if (filters.assigneeId !== "all" && !task.assigneeIds.includes(filters.assigneeId)) {
      return false;
    }

    if (!query) {
      return true;
    }

    const assigneeNames = task.assigneeIds
      .map((id) => membersMap[id]?.name ?? "")
      .join(" ")
      .toLowerCase();

    return (
      task.id.toLowerCase().includes(query) ||
      task.title.toLowerCase().includes(query) ||
      task.tags.join(" ").toLowerCase().includes(query) ||
      assigneeNames.includes(query)
    );
  });
}

export function groupTasksByStatus(tasks: SprintTask[]) {
  const initial: Record<SprintTaskStatus, SprintTask[]> = {
    todo: [],
    in_progress: [],
    review: [],
    done: [],
  };

  for (const task of tasks) {
    initial[task.status].push(task);
  }

  return initial;
}

export function getDueDateState(dueDate: string) {
  const now = new Date();
  now.setHours(0, 0, 0, 0);

  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);

  const diffDays = Math.round((due.getTime() - now.getTime()) / 86_400_000);

  if (diffDays < 0) {
    return { label: "Overdue", tone: "danger" as const };
  }

  if (diffDays <= 2) {
    return { label: `Due in ${diffDays}d`, tone: "warning" as const };
  }

  return { label: `Due in ${diffDays}d`, tone: "neutral" as const };
}

export function getSprintPointSummary(tasks: SprintTask[]) {
  const total = tasks.reduce((sum, task) => sum + task.storyPoints, 0);
  const completed = tasks
    .filter((task) => task.status === "done")
    .reduce((sum, task) => sum + task.storyPoints, 0);

  return {
    total,
    completed,
    remaining: Math.max(total - completed, 0),
  };
}

export function getSprintProgress(tasks: SprintTask[]) {
  if (!tasks.length) {
    return 0;
  }

  const doneCount = tasks.filter((task) => task.status === "done").length;
  return Math.round((doneCount / tasks.length) * 100);
}

