import { sprintBoardMockData } from "./mock-data";
import type { CreateTaskInput, SprintBoardData, SprintTaskStatus } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function fetchSprintBoardData(): Promise<SprintBoardData> {
  const response = await fetch(`${API_BASE_URL}/sprints/active`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return sprintBoardMockData;
  }

  return (await response.json()) as SprintBoardData;
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

