import type { TeamAnalytics } from "./types";

export const mockTeamAnalytics: TeamAnalytics = {
  sprintId: "sprint-42",
  sprintNumber: 42,
  quarter: "Q3",
  year: 2023,
  teamVelocity: {
    current: 84,
    previous: 76,
    trend: 10.5,
    completedPoints: 84,
  },
  engineers: [
    {
      id: "eng-1",
      name: "Sarah J.",
      role: "Frontend Lead",
      velocity: 32,
      quality: 98,
      score: 9.4,
      status: "optimal",
      avatar: "SJ",
    },
    {
      id: "eng-2",
      name: "Mike T.",
      role: "Backend Engineer",
      velocity: 28,
      quality: 95,
      score: 9.1,
      status: "optimal",
      avatar: "MT",
    },
    {
      id: "eng-3",
      name: "Alex M.",
      role: "Full Stack",
      velocity: 24,
      quality: 92,
      score: 8.8,
      status: "warning",
      avatar: "AM",
    },
  ],
  insights: [
    {
      id: "insight-1",
      title: "Workload Imbalance",
      description:
        "Alex M. is currently assigned 20% less capacity than optimal. Consider redistributing tasks.",
      severity: "warning",
      metric: "20%",
      trend: "down",
    },
    {
      id: "insight-2",
      title: "Code Quality Improving",
      description:
        "Team quality score improved by 3.2% compared to last sprint.",
      severity: "info",
      metric: "3.2%",
      trend: "up",
    },
  ],
  dateRange: {
    start: "2023-09-01",
    end: "2023-09-15",
  },
};
