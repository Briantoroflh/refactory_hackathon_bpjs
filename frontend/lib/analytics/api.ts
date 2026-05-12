import { apiClient } from "@/lib/api/client";
import { fetchProjectsPageData } from "@/lib/projects/api";
import { fetchSprintBoardData } from "@/lib/sprints/api";
import type { TeamAnalytics } from "./types";

const currentYear = new Date().getFullYear();

export function createEmptyAnalytics(): TeamAnalytics {
  return {
    sprintId: "analytics-empty",
    sprintNumber: 0,
    sprintLabel: "Live Team Analytics",
    quarter: `Q${Math.floor(new Date().getMonth() / 3) + 1}`,
    year: currentYear,
    teamVelocity: {
      current: 0,
      previous: 0,
      trend: 0,
      completedPoints: 0,
    },
    engineers: [],
    insights: [],
    dateRange: {
      start: new Date().toISOString(),
      end: new Date().toISOString(),
    },
  };
}

export async function fetchAnalyticsSnapshot(): Promise<{
  analytics: TeamAnalytics;
  notice?: string;
}> {
  const projectsData = await fetchProjectsPageData();
  const projectId = Number(projectsData.projects[0]?.id);

  if (!Number.isFinite(projectId)) {
    return {
      analytics: createEmptyAnalytics(),
      notice: "No live projects available yet.",
    };
  }

  const [analyticsResult, sprintResult] = await Promise.allSettled([
    apiClient.get<TeamAnalytics>(`/projects/${projectId}/analytics-overview`),
    fetchSprintBoardData(projectId),
  ]);

  const analytics =
    analyticsResult.status === "fulfilled" ? analyticsResult.value : createEmptyAnalytics();
  const sprint = sprintResult.status === "fulfilled" ? sprintResult.value : null;

  const notice =
    analyticsResult.status === "rejected"
      ? analyticsResult.reason instanceof Error
        ? analyticsResult.reason.message
        : "Failed to load analytics"
      : sprintResult.status === "rejected"
        ? sprintResult.reason instanceof Error
          ? sprintResult.reason.message
          : "Sprint data unavailable"
        : undefined;

  return {
    analytics: {
      ...analytics,
      sprintLabel: sprint?.sprint.name ?? analytics.sprintLabel ?? "Live Team Analytics",
      dateRange: sprint
        ? {
            start: sprint.sprint.startDateLabel || analytics.dateRange.start,
            end: sprint.sprint.endDateLabel || analytics.dateRange.end,
          }
        : analytics.dateRange,
    },
    notice,
  };
}
