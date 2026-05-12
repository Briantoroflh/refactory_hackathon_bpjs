"use client";

import { useAsync } from "@/lib/api/hooks";
import { teamsAPI, workersAPI } from "@/lib/api/client";

export interface APITeam {
  team_id: number;
  name: string;
  category_id: number;
  description?: string;
  status: string;
  capacity_hours: number;
}

export interface APIWorker {
  worker_id: number;
  full_name: string;
  email: string;
  division_id: number;
  employment_status: string;
}

export function useTeams(skip = 0, limit = 20) {
  return useAsync(() => teamsAPI.list(skip, limit), true, [skip, limit]);
}

export function useTeam(teamId: number) {
  return useAsync(() => teamsAPI.get(teamId), !!teamId, [teamId]);
}

export function useTeamMembers(teamId: number) {
  return useAsync(() => teamsAPI.getMembers(teamId), !!teamId, [teamId]);
}

export function useCreateTeam() {
  const createTeam = async (data: any) => {
    return teamsAPI.create(data);
  };

  return { createTeam };
}

export function useWorkers(skip = 0, limit = 20) {
  return useAsync(() => workersAPI.list(skip, limit), true, [skip, limit]);
}

export function useWorker(workerId: number) {
  return useAsync(() => workersAPI.get(workerId), !!workerId, [workerId]);
}

export function useWorkerKPI(workerId: number) {
  return useAsync(() => workersAPI.getKPI(workerId), !!workerId, [workerId]);
}
