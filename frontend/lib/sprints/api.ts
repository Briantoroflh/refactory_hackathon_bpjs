import { sprintBoardMockData } from "./mock-data";
import type { CreateTaskInput, SprintBoardData, SprintTaskStatus } from "./types";
import { apiClient } from "@/lib/api/client";

// Default project to attach sprint to (user selected)
const DEFAULT_PROJECT_ID = 3;

// Simple in-memory cache
let boardDataCache: SprintBoardData | null = null;
let lastFetchTime = 0;
const CACHE_TTL = 30000; // 30 seconds

export async function fetchSprintBoardData(projectId: number = DEFAULT_PROJECT_ID): Promise<SprintBoardData> {
  const now = Date.now();
  
  if (boardDataCache && now - lastFetchTime < CACHE_TTL) {
    return boardDataCache;
  }

  try {
    // Fetch tasks from backend for the selected project and map into sprint board shape
    const tasksResponse = await apiClient.get<any>(`/projects/${projectId}/tasks`);
    // apiClient returns the JSON from backend; unwrap if it's enveloped
    const payload = (tasksResponse && tasksResponse.data) ? tasksResponse.data : tasksResponse;

    // Map tasks to sprint board minimal structure
    const tasks = Array.isArray(payload)
      ? payload.map((t: any) => ({
          id: String(t.task_id || t.id),
          title: t.title || t.name || "Untitled",
          status: (t.status ?? "todo") as SprintTaskStatus,
          priority: t.priority ?? "medium",
          dueDate: t.deadline ?? null,
          storyPoints: t.story_points ?? t.storyPoints ?? 0,
          tags: t.tags ?? [],
          assigneeIds: t.assigned_to ? [String(t.assigned_to)] : [],
        }))
      : [];

    const data: SprintBoardData = {
      sprint: {
        id: `project-${projectId}-sprint`,
        name: `Project ${projectId} Active Sprint`,
        projectPath: ["Projects", `Project ${projectId}`],
        startDateLabel: "",
        endDateLabel: "",
        daysRemaining: 0,
        storyPointGoal: tasks.reduce((s, t) => s + (t.storyPoints || 0), 0),
      },
      members: [], // backend doesn't expose sprint members yet
      stats: [],
      tasks,
      sidebarItems: sprintBoardMockData.sidebarItems,
    };

    boardDataCache = data;
    lastFetchTime = now;
    return data;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      console.warn("Backend sync failed. Using local data fallback.");
    }
    return boardDataCache ?? sprintBoardMockData;
  }
}

export async function createSprint(payload: {
  name: string;
  startDate: string;
  endDate: string;
  goalPoints: number;
}) {
  // Backend doesn't have sprint model; return client-side id for now
  return { id: `local-${Date.now()}` };
}

export async function createSprintTask(payload: CreateTaskInput, projectId: number = DEFAULT_PROJECT_ID) {
  // Create task in project via backend
  const response = await apiClient.post<any>(`/projects/${projectId}/tasks`, payload);
  const payloadResp = (response && response.data) ? response.data : response;
  return { id: String(payloadResp.task_id || payloadResp.id) };
}

export async function updateTaskStatus(taskId: string, status: SprintTaskStatus, projectId: number = DEFAULT_PROJECT_ID, version?: number) {
  // Use project-scoped update endpoint
  const body: any = { status };
  if (typeof version !== 'undefined') body.version = version;
  await apiClient.patch(`/projects/${projectId}/tasks/${taskId}/status`, body);
}

