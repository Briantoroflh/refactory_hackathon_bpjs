import { sprintBoardMockData } from "./mock-data";
import type { CreateTaskInput, SprintBoardData, SprintTaskStatus } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

// Simple in-memory cache
let boardDataCache: SprintBoardData | null = null;
let lastFetchTime = 0;
const CACHE_TTL = 30000; // 30 seconds

export async function fetchSprintBoardData(): Promise<SprintBoardData> {
  const now = Date.now();
  
  if (boardDataCache && now - lastFetchTime < CACHE_TTL) {
    return boardDataCache;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/sprints/active`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000), // Timeout after 5s
    });

    if (!response.ok) {
      return boardDataCache ?? sprintBoardMockData;
    }

    const data = (await response.json()) as SprintBoardData;
    boardDataCache = data;
    lastFetchTime = now;
    return data;
  } catch (error) {
    // Only log actual errors, not failed fetches when backend is down
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
  const response = await fetch(`${API_BASE_URL}/sprints`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Unable to create sprint.");
  }

  return (await response.json()) as { id: string };
}

export async function createSprintTask(payload: CreateTaskInput) {
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Unable to create task.");
  }

  return (await response.json()) as { id: string };
}

export async function updateTaskStatus(taskId: string, status: SprintTaskStatus) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });

  if (!response.ok) {
    throw new Error("Unable to update task status.");
  }
}

