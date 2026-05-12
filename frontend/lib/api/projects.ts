"use client";

import { useAsync, useFetch } from "@/lib/api/hooks";
import { projectsAPI } from "@/lib/api/client";

export interface APIProject {
  project_id: number;
  name: string;
  description?: string;
  status: string;
  created_by: number;
  start_date?: string;
  end_date?: string;
  repository_url?: string;
  repository_type?: string;
  version: number;
}

export function useProjects(skip = 0, limit = 20) {
  return useAsync(() => projectsAPI.list(), true, [skip, limit]);
}

export function useProject(projectId: number) {
  return useAsync(() => projectsAPI.get(projectId), !!projectId, [projectId]);
}

export function useCreateProject() {
  const createProject = async (data: any) => {
    return projectsAPI.create(data);
  };

  return { createProject };
}

export function useUpdateProject(projectId: number) {
  const updateProject = async (data: any) => {
    return projectsAPI.update(projectId, data);
  };

  return { updateProject };
}
