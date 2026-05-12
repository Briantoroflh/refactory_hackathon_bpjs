"use client";

import { useAsync } from "@/lib/api/hooks";
import { tasksAPI } from "@/lib/api/client";

export interface APITask {
  task_id: number;
  project_id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  story_points?: number;
  assigned_to?: number;
  deadline?: string;
  version: number;
}

export function useTasks(projectId: number, skip = 0, limit = 20) {
  return useAsync(() => tasksAPI.list(projectId, skip, limit), !!projectId, [
    projectId,
    skip,
    limit,
  ]);
}

export function useTask(taskId: number) {
  return useAsync(() => tasksAPI.get(taskId), !!taskId, [taskId]);
}

export function useCreateTask(projectId: number) {
  const createTask = async (data: any) => {
    return tasksAPI.create(projectId, data);
  };

  return { createTask };
}

export function useUpdateTask(taskId: number) {
  const updateTask = async (data: any) => {
    return tasksAPI.update(taskId, data);
  };

  return { updateTask };
}

export function useTaskComments(taskId: number) {
  return useAsync(() => tasksAPI.getComments(taskId), !!taskId, [taskId]);
}

export function useAddTaskComment(taskId: number) {
  const addComment = async (content: string) => {
    return tasksAPI.addComment(taskId, content);
  };

  return { addComment };
}

export function useTaskHistory(taskId: number) {
  return useAsync(() => tasksAPI.getHistory(taskId), !!taskId, [taskId]);
}
