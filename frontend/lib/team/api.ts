import { apiClient } from "@/lib/api/client";
import type { TeamAccessControl } from "./types";

interface APITeamAccessControl extends Omit<TeamAccessControl, "totalMembers"> {
  total_members: number;
}

export function createEmptyTeamAccessControl(): TeamAccessControl {
  return {
    team: null,
    teams: [],
    members: [],
    totalMembers: 0,
    permissions: [],
    notice: null,
  };
}

function mapTeamAccessControl(data: APITeamAccessControl): TeamAccessControl {
  return {
    team: data.team ?? null,
    teams: data.teams ?? [],
    members: data.members ?? [],
    totalMembers: data.total_members ?? 0,
    permissions: data.permissions ?? [],
    notice: data.notice ?? null,
  };
}

export async function fetchTeamAccessControl(teamId?: number): Promise<TeamAccessControl> {
  const query = teamId ? `?team_id=${teamId}` : "";
  const data = await apiClient.get<APITeamAccessControl>(`/teams/access-control${query}`);
  return mapTeamAccessControl(data);
}
