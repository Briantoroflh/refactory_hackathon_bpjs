import { dashboardOverview } from "./mock-data";
import type { DashboardOverview } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function fetchDashboardOverview(): Promise<DashboardOverview> {
  const response = await fetch(`${API_BASE_URL}/dashboard/overview`, {
    cache: "no-store",
  });

  if (!response.ok) {
    return dashboardOverview;
  }

  return (await response.json()) as DashboardOverview;
}
