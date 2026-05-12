import type { ProjectItem, ProjectsPageData } from "./types";

export const projectsMockData: ProjectsPageData = {
  projects: [
    {
      id: "core-authentication-service",
      name: "core-authentication-service",
      platform: "GitHub",
      description: "Authentication core, token lifecycle, and access control rules.",
      status: "healthy",
      aiHealthScore: 98,
      healthDelta: 2,
      commitVelocity: 42,
      commitBars: [16, 24, 20, 30, 18, 38, 44],
      progress: 86,
      updatedAtLabel: "2h ago",
      members: [
        { id: "u1", name: "Ayu", avatar: "AY" },
        { id: "u2", name: "Raka", avatar: "RK" },
        { id: "u3", name: "Nina", avatar: "NN" },
      ],
    },
    {
      id: "frontend-dashboard-v2",
      name: "frontend-dashboard-v2",
      platform: "GitLab",
      description: "Main frontend workspace for analytics and reporting dashboards.",
      status: "warning",
      aiHealthScore: 74,
      healthDelta: -5,
      commitVelocity: 12,
      commitBars: [36, 24, 18, 10, 14, 22, 16],
      progress: 54,
      updatedAtLabel: "5h ago",
      members: [
        { id: "u4", name: "Dio", avatar: "DO" },
        { id: "u5", name: "Mila", avatar: "ML" },
      ],
    },
    {
      id: "payment-gateway-api",
      name: "payment-gateway-api",
      platform: "GitHub",
      description: "Payment transaction orchestration and reconciliation endpoints.",
      status: "healthy",
      aiHealthScore: 88,
      healthDelta: 0,
      commitVelocity: 28,
      commitBars: [18, 14, 24, 10, 32, 20, 30],
      progress: 69,
      updatedAtLabel: "1d ago",
      members: [{ id: "u6", name: "Sena", avatar: "SE" }],
    },
  ],
  repositories: [
    {
      id: "repo-1",
      repositoryName: "infrastructure-as-code",
      platform: "GitHub Enterprise",
      status: "syncing",
    },
    {
      id: "repo-2",
      repositoryName: "open-source-docs",
      platform: "GitLab Cloud",
      status: "paused",
    },
  ],
};

export const emptyProjectsMockData: ProjectsPageData = {
  projects: [],
  repositories: [],
};

export const projectSidebarItems = [
  { label: "Dashboard", href: "/dashboard", icon: "dashboard" },
  { label: "Project", href: "/projects", icon: "project", active: true },
  { label: "Sprint", href: "/sprints", icon: "sprint" },
  { label: "Tasks", href: "/tasks", icon: "tasks" },
  { label: "Analytics", href: "/analytics", icon: "analytics" },
  { label: "AI Assistant", href: "/ai", icon: "ai" },
  { label: "Team", href: "/team", icon: "team" },
  { label: "Settings", href: "/settings", icon: "settings" },
] as const;

export function findProjectById(projects: ProjectItem[], id: string): ProjectItem | undefined {
  return projects.find((project) => project.id === id);
}
