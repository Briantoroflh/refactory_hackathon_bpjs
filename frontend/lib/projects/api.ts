import { apiClient } from "@/lib/api/client";
import type { ProjectsPageData } from "./types";

export async function fetchProjectsPageData(): Promise<ProjectsPageData> {
  return apiClient.get<ProjectsPageData>("/projects/overview");
}

export async function createProject(payload: {
  name: string;
  platform: string;
  description: string;
}): Promise<{ id: string }> {
  return apiClient.post<{ id: string }>("/projects", payload);
}
