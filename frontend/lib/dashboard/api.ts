import { apiClient } from "@/lib/api/client";
import type { DashboardOverview } from "./types";

export async function fetchDashboardOverview(days = 30): Promise<DashboardOverview> {
  return apiClient.get<DashboardOverview>(`/api/v1/dashboard/overview?days=${days}`);
}
