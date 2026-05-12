import type { DashboardNavItem, DashboardOverview } from "./types";

export const dashboardNavItems: DashboardNavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: "dashboard", active: true },
  { label: "Project", href: "/projects", icon: "project" },
  { label: "Sprint", href: "/sprints", icon: "sprint" },
  { label: "Tasks", href: "/tasks", icon: "tasks" },
  { label: "Analytics", href: "/analytics", icon: "analytics" },
  { label: "AI Assistant", href: "/ai", icon: "ai" },
  { label: "Team", href: "/team", icon: "team" },
  { label: "Settings", href: "/settings", icon: "settings" },
];

export const dashboardOverview: DashboardOverview = {
  stats: [
    {
      title: "Sprint Velocity",
      value: "42",
      delta: "+12%",
      deltaDirection: "up",
      description: "Points completed this sprint",
      accent: "from-indigo-200 to-indigo-400",
      icon: "trend",
    },
    {
      title: "Completion Rate",
      value: "94%",
      delta: "+2%",
      deltaDirection: "up",
      description: "Vs. trailing 3 sprints",
      accent: "from-emerald-200 to-emerald-400",
      icon: "check",
    },
    {
      title: "Team Burnout Risk",
      value: "Low",
      delta: "AI Assessed",
      deltaDirection: "up",
      description: "Workload evenly distributed",
      accent: "from-amber-200 to-amber-400",
      icon: "flame",
    },
    {
      title: "Active Blockers",
      value: "2",
      delta: "+1",
      deltaDirection: "down",
      description: "Requires immediate attention",
      accent: "from-rose-200 to-rose-400",
      icon: "block",
    },
  ],
  sprint: {
    title: "Active Sprint Progress",
    subtitle: "Sprint 42: Core Infrastructure",
    bars: [
      { label: "Mon", value: 28 },
      { label: "Tue", value: 42 },
      { label: "Wed", value: 56 },
      { label: "Thu", value: 78, active: true },
      { label: "Fri", value: 22 },
    ],
  },
  activities: [
    {
      id: "act-1",
      title: "API auth flow wired",
      project: "Bloom OS",
      owner: "Ayu",
      timestamp: "2m ago",
      status: "done",
    },
    {
      id: "act-2",
      title: "Sprint backlog reviewed",
      project: "Engineering Dashboard",
      owner: "Raka",
      timestamp: "18m ago",
      status: "in progress",
    },
    {
      id: "act-3",
      title: "Design tokens aligned",
      project: "Productivity Core",
      owner: "Nina",
      timestamp: "1h ago",
      status: "review",
    },
    {
      id: "act-4",
      title: "Blocking issue escalated",
      project: "Dashboard System",
      owner: "Dio",
      timestamp: "3h ago",
      status: "done",
    },
  ],
  notifications: [
    {
      id: "noti-1",
      title: "Sprint prediction",
      description: "The team is on track to finish all core tasks one day early.",
      tone: "success",
    },
    {
      id: "noti-2",
      title: "Workload alert",
      description: "Sarah has taken 3 complex tickets. Consider reassigning DEV-402.",
      tone: "warning",
    },
    {
      id: "noti-3",
      title: "Daily summary",
      description: "Commit activity is stable and the review queue is under control.",
      tone: "info",
    },
  ],
};
