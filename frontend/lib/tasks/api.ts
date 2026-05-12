import { apiClient } from "@/lib/api/client";
import { fetchProjectsPageData } from "@/lib/projects/api";
import type { SprintBoardData } from "@/lib/sprints/types";
import type { SprintTasks, TaskCard, TaskColumn } from "./types";

const statusColumns: Array<{ id: string; title: string; order: string[] }> = [
  { id: "todo", title: "To Do", order: ["todo"] },
  { id: "in_progress", title: "In Progress", order: ["in_progress"] },
  { id: "review", title: "Review", order: ["review"] },
  { id: "done", title: "Done", order: ["done"] },
];

function formatRepositoryHref(repositoryUrl?: string | null): string {
  if (!repositoryUrl) {
    return "#";
  }

  if (/^https?:\/\//i.test(repositoryUrl)) {
    return repositoryUrl;
  }

  const scpMatch = repositoryUrl.match(/^git@([^:]+):(.+)$/);
  if (scpMatch) {
    const host = scpMatch[1];
    const path = scpMatch[2].replace(/\.git$/, "");
    return `https://${host}/${path}`;
  }

  return repositoryUrl;
}

function formatRepositoryLabel(repositoryUrl?: string | null, fallback = "project"): string {
  if (!repositoryUrl) {
    return fallback;
  }

  try {
    const normalized = repositoryUrl.startsWith("http")
      ? new URL(repositoryUrl).pathname
      : repositoryUrl.match(/^git@([^:]+):(.+)$/)
        ? repositoryUrl.match(/^git@([^:]+):(.+)$/)?.[2] ?? repositoryUrl
        : repositoryUrl;

    return normalized.replace(/^\/+/, "").replace(/\.git$/, "") || fallback;
  } catch {
    return repositoryUrl.replace(/^https?:\/\//, "").replace(/\.git$/, "") || fallback;
  }
}

function createAvatar(name?: string, email?: string): string {
  if (name) {
    return name
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase();
  }

  return (email ?? "??").slice(0, 2).toUpperCase();
}

function normalizePriority(priority: unknown): "low" | "medium" | "high" {
  if (priority === "low" || priority === "medium" || priority === "high") {
    return priority;
  }

  return "medium";
}

function backendStatusToColumn(status: string): string {
  const mapping: Record<string, string> = {
    backlog: "todo",
    in_progress: "in_progress",
    in_review: "review",
    completed: "done",
    closed: "done",
  };

  return mapping[status] ?? "todo";
}

function mapTask(task: Record<string, unknown>, memberMap: Map<string, SprintBoardData["members"][number]>): TaskCard & { status: string } {
  const assigneeId = task.assigned_to ?? task.assignedTo ?? null;
  const assignee = assigneeId ? memberMap.get(String(assigneeId)) : undefined;

  return {
    id: String(task.task_id ?? task.id),
    title: String(task.title ?? "Untitled task"),
    description: String(task.description ?? ""),
    label: `#${String(task.task_id ?? task.id)}`,
    priority: normalizePriority(task.priority),
    assignee: assignee
      ? {
          name: assignee.name,
          avatar: assignee.avatar || createAvatar(assignee.name),
        }
      : undefined,
    dueDate: String(task.deadline ?? ""),
    status: backendStatusToColumn(String(task.status ?? "backlog")),
  };
}

function buildColumns(tasks: Array<TaskCard & { status: string }>): TaskColumn[] {
  return statusColumns
    .map((column) => {
      const cards = tasks.filter((task) => column.order.includes(task.status));
      return {
        id: column.id,
        title: column.title,
        count: cards.length,
        cards: cards.map(({ status: _status, ...card }) => card),
      };
    })
    .filter((column) => column.count > 0 || column.id !== "done");
}

function parseSprintNumber(title: string): number | undefined {
  const match = title.match(/\b(\d+)\b/);
  if (!match) {
    return undefined;
  }

  const parsed = Number(match[1]);
  return Number.isFinite(parsed) ? parsed : undefined;
}

export function createEmptyTaskBoard(): SprintTasks {
  return {
    sprintTitle: "Live Task Board",
    dateRange: "Waiting for live data",
    repositoryLink: "project",
    repositoryHref: "#",
    columns: buildColumns([]),
  };
}

export async function fetchTaskBoardSnapshot(): Promise<{
  board: SprintTasks;
  notice?: string;
}> {
  const projectsData = await fetchProjectsPageData();
  const projectId = Number(projectsData.projects[0]?.id);

  if (!Number.isFinite(projectId)) {
    return {
      board: createEmptyTaskBoard(),
      notice: "No live projects available yet.",
    };
  }

  const [sprintResult, projectResult, tasksResult] = await Promise.allSettled([
    apiClient.get<SprintBoardData>(`/projects/${projectId}/sprint-overview`),
    apiClient.get<Record<string, unknown>>(`/projects/${projectId}`),
    apiClient.get<Array<Record<string, unknown>>>(`/projects/${projectId}/tasks?skip=0&limit=100`),
  ]);

  const notices: string[] = [];
  const sprintOverview = sprintResult.status === "fulfilled" ? sprintResult.value : null;
  const project = projectResult.status === "fulfilled" ? projectResult.value : null;
  const tasks = tasksResult.status === "fulfilled" ? tasksResult.value : [];

  if (sprintResult.status === "rejected") {
    notices.push(sprintResult.reason instanceof Error ? sprintResult.reason.message : "Sprint data unavailable");
  }
  if (projectResult.status === "rejected") {
    notices.push(projectResult.reason instanceof Error ? projectResult.reason.message : "Project data unavailable");
  }
  if (tasksResult.status === "rejected") {
    notices.push(tasksResult.reason instanceof Error ? tasksResult.reason.message : "Task data unavailable");
  }

  const memberMap = new Map(
    (sprintOverview?.members ?? []).map((member) => [member.id, member]),
  );
  const mappedTasks = tasks.map((task) => mapTask(task, memberMap));

  const repositoryUrl = String(project?.repository_url ?? "");
  const sprintTitle = sprintOverview?.sprint.name ?? String(project?.name ?? "Live Task Board");

  return {
    board: {
      sprintNumber: sprintOverview ? parseSprintNumber(sprintOverview.sprint.name) : undefined,
      sprintTitle,
      dateRange:
        sprintOverview
          ? `${sprintOverview.sprint.startDateLabel} - ${sprintOverview.sprint.endDateLabel}`
          : "Waiting for live data",
      repositoryLink: formatRepositoryLabel(
        repositoryUrl || (sprintOverview ? sprintOverview.sprint.projectPath?.[sprintOverview.sprint.projectPath.length - 1] : undefined),
        "project",
      ),
      repositoryHref: formatRepositoryHref(repositoryUrl),
      columns: buildColumns(mappedTasks),
      generatedAt: sprintOverview?.generatedAt,
    },
    notice: notices.length ? notices[0] : undefined,
  };
}
