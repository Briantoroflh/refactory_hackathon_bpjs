"use client";

import { useAsync } from "@/lib/api/hooks";
import { aiAssistantAPI } from "@/lib/api/client";

export interface AIWorkflowRequest {
  prompt: string;
  context?: Record<string, any>;
  async_mode?: boolean;
}

export interface AIWorkflowResponse {
  workflow: string;
  status: string;
  model: string;
  content: string;
  structured_output?: Record<string, any>;
  usage?: Record<string, any>;
  source: string;
  job_id?: string;
}

export interface AIJobResponse {
  job_id: string;
  workflow: string;
  status: string;
  model: string;
  result?: AIWorkflowResponse;
  error?: string;
}

export function useAIPlanning(request?: AIWorkflowRequest, immediate = false) {
  return useAsync(
    () => aiAssistantAPI.planning(request || { prompt: "" }),
    immediate && !!request,
    [request],
  );
}

export function useAISprintSummary(
  request?: AIWorkflowRequest,
  immediate = false,
) {
  return useAsync(
    () => aiAssistantAPI.sprintSummary(request || { prompt: "" }),
    immediate && !!request,
    [request],
  );
}

export function useAIStandupRecap(
  request?: AIWorkflowRequest,
  immediate = false,
) {
  return useAsync(
    () => aiAssistantAPI.standupRecap(request || { prompt: "" }),
    immediate && !!request,
    [request],
  );
}

export function useAITaskRecommendation(
  request?: AIWorkflowRequest,
  immediate = false,
) {
  return useAsync(
    () => aiAssistantAPI.taskRecommendation(request || { prompt: "" }),
    immediate && !!request,
    [request],
  );
}

export function useAIJobStatus(jobId?: string) {
  return useAsync(
    () => aiAssistantAPI.jobStatus(jobId || ""),
    !!jobId,
    [jobId],
    5000, // Poll every 5 seconds
  );
}

export function useLazyAIPlanning() {
  const launch = async (request: AIWorkflowRequest) => {
    return aiAssistantAPI.planning(request);
  };

  return { launch };
}

export function useLazyAISprintSummary() {
  const launch = async (request: AIWorkflowRequest) => {
    return aiAssistantAPI.sprintSummary(request);
  };

  return { launch };
}

export function useLazyAITaskRecommendation() {
  const launch = async (request: AIWorkflowRequest) => {
    return aiAssistantAPI.taskRecommendation(request);
  };

  return { launch };
}
