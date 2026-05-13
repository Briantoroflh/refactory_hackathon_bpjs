import { apiClient } from "@/lib/api/client";
import type {
  CreateTaskInput,
  SprintBoardData,
  SprintSidebarItem,
  SprintTask,
  SprintTaskStatus,
} from "./types";

const DEFAULT_PROJECT_ID = 3;

export const sprintSidebarItems: SprintSidebarItem[] = [
  { label: "Dashboard", href: "/home", icon: "dashboard" },
  { label: "Project", href: "/projects", icon: "project" },
  { label: "Sprint", href: "/sprints", icon: "sprint", active: true },
  { label: "Tasks", href: "/tasks", icon: "tasks" },
  { label: "Analytics", href: "/analytics", icon: "analytics" },
  { label: "AI Assistant", href: "/ai", icon: "ai" },
  { label: "Team", href: "/team", icon: "team" },
  { label: "Settings", href: "/settings", icon: "settings" },
];

function sprintStatusToBackend(status: SprintTaskStatus) {
  const mapping: Record<SprintTaskStatus, string> = {
    todo: "backlog",
    in_progress: "in_progress",
    review: "in_review",
    done: "completed",
  };

  return mapping[status];
}

function backendStatusToSprint(status: string): SprintTaskStatus {
  const mapping: Record<string, SprintTaskStatus> = {
    backlog: "todo",
    in_progress: "in_progress",
    in_review: "review",
    completed: "done",
    closed: "done",
  };

  return mapping[status] ?? "todo";
}

function normalizeTask(task: Record<string, unknown>): SprintTask {
  const assigneeIds = Array.isArray(task.assigneeIds)
    ? (task.assigneeIds as string[])
    : Array.isArray(task.assignee_ids)
      ? (task.assignee_ids as string[])
      : task.assigned_to
        ? [String(task.assigned_to)]
        : [];

  return {
    id: String(task.id ?? task.task_id),
    title: String(task.title ?? "Untitled"),
    status: backendStatusToSprint(String(task.status ?? "backlog")),
    priority: String(task.priority ?? "medium") as SprintTask["priority"],
    dueDate: String(task.dueDate ?? task.deadline ?? ""),
    storyPoints: Number(task.storyPoints ?? task.story_points ?? 0),
    tags: Array.isArray(task.tags) ? (task.tags as string[]) : ["General"],
    assigneeIds,
    version: Number(task.version ?? 1),
  };
}

export async function fetchSprintBoardData(projectId: number = DEFAULT_PROJECT_ID): Promise<SprintBoardData> {
  const payload = await apiClient.get<{
    sprint: SprintBoardData["sprint"];
    members: SprintBoardData["members"];
    stats: SprintBoardData["stats"];
    tasks: Array<Record<string, unknown>>;
    velocity: SprintBoardData["velocity"];
    insights: SprintBoardData["insights"];
  }>(`/projects/${projectId}/sprint-overview`);

  return {
    sprint: payload.sprint,
    members: payload.members ?? [],
    stats: payload.stats ?? [],
    tasks: (payload.tasks ?? []).map(normalizeTask),
    sidebarItems: sprintSidebarItems,
    velocity: payload.velocity ?? [],
    insights: payload.insights ?? {
      title: "AI Standup Insight",
      subtitle: "Live sprint summary",
      summary: "No sprint insight available yet.",
      alertTitle: "No Active Data",
      alertBody: "Create tasks to populate sprint insights.",
      status: "at_risk",
    },
  };
}

export async function createSprint(payload: {
  name: string;
  startDate: string;
  endDate: string;
  goalPoints: number;
}) {
  return { id: `local-${Date.now()}` };
}

export async function createSprintTask(payload: CreateTaskInput, projectId: number = DEFAULT_PROJECT_ID) {
  const response = await apiClient.post<Record<string, unknown>>(`/projects/${projectId}/tasks`, {
    title: payload.title,
    description: payload.tags.length ? payload.tags.join(", ") : "",
    story_points: payload.storyPoints,
    assigned_to: payload.assigneeIds[0] ? Number(payload.assigneeIds[0]) : undefined,
    priority: payload.priority,
    deadline: payload.dueDate,
  });

  const createdTask = normalizeTask(response);
  if (createdTask.status !== payload.status) {
    await updateTaskStatus(createdTask.id, payload.status, projectId, createdTask.version);
  }

  return { id: createdTask.id, version: createdTask.version };
}

export async function updateTaskStatus(
  taskId: string,
  status: SprintTaskStatus,
  projectId: number = DEFAULT_PROJECT_ID,
  version?: number,
) {
  const body: Record<string, unknown> = {
    status: sprintStatusToBackend(status),
  };

  if (typeof version !== "undefined") {
    body.version = version;
  }

  const response = await apiClient.patch<Record<string, unknown>>(
    `/projects/${projectId}/tasks/${taskId}/status`,
    body,
  );

  return normalizeTask(response);
}
