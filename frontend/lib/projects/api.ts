import { projectsMockData } from "./mock-data";
import type { ProjectsPageData } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function fetchProjectsPageData(): Promise<ProjectsPageData> {
  const response = await fetch(`${API_BASE_URL}/projects/overview`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return projectsMockData;
  }

  return (await response.json()) as ProjectsPageData;
}

export async function createProject(payload: {
  name: string;
  platform: string;
  description: string;
}): Promise<{ id: string }> {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Unable to create project.");
  }

  return (await response.json()) as { id: string };
}

